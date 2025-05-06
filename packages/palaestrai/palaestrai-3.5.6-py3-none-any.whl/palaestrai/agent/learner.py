"""This module contains the abstract class :class:`Brain` that is used
to implement the thinking part of agents.

"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Set, Dict

import logging
import numpy as np
from collections import defaultdict

from palaestrai.agent import Memory
from palaestrai.core import EventStateMachine as ESM
from palaestrai.types import Mode, SimulationFlowControl
from palaestrai.core import EventStateMachineFlags as ESMFlags
from palaestrai.core.protocol import (
    MuscleUpdateRequest,
    MuscleUpdateResponse,
    MuscleShutdownRequest,
    MuscleShutdownResponse,
)
from palaestrai.store import query, Session, database_model

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from . import Brain
    from palaestrai.types import ExperienceLocation
    from palaestrai.experiment import TerminationCondition


@ESM.monitor(is_mdp_worker=True)
class Learner:
    """Runtime wrapper for :class:`Brain`s.

    A :class:`Brain` is the learning implementation of an algorithm, be it
    deep reinforcement learning or any other kind of algorithm.
    However, a algorithm developers that implements a :class:`Brain` does not
    need to concern themselves with the inner workings of palaestrAI, e.g.,
    the major domo broker and the messaging protocol.
    Therefore, :class:`Brain` instances are wrapped in Learner objects that
    take care of the communication and all the many things that can possibly
    go wrong.

    Parameters
    ----------
    brain : Brain
        The actual :class:`Brain` instance this Learner wraps
    uid : str
        The unique (internal) ID of the :class:`Brain` (for communications mostly)
    name : str
        The agent's name as defined by the user
    """

    def __init__(self, brain: Brain, uid: str, name: str):
        self._uid: str = uid
        self._brain: Brain = brain
        self._experience_locations: List[ExperienceLocation] = []
        self._rollout_workers: Set[str] = set()
        self._updated: Dict[str, bool] = defaultdict(bool)  # Default: False
        self._latest_update: Any = None
        self._termination_conditions: List[TerminationCondition] = []

        self._brain._name = name

    @property
    def uid(self):
        """Unique ID of this Brain"""
        return self._uid

    @property
    def name(self):
        return self._brain.name

    @property
    def brain(self) -> Brain:
        """The :clasS:`Brain` this Learner caters for"""
        return self._brain

    def _try_load_previous_trajectories(self):
        LOG.debug(
            "%s trying to learn from previous experiences: %s",
            self,
            self._experience_locations,
        )
        if not self._experience_locations:
            return
        try:
            with Session() as dbh:
                maq = query.make_muscle_actions_query(
                    experiment_run_uids=[
                        el.experiment_run_uid
                        for el in self._experience_locations
                    ],
                    agent_uids=[
                        el.agent_name for el in self._experience_locations
                    ],
                    predicate=lambda q: q.where(
                        database_model.ExperimentRunPhase.number.in_(
                            [
                                int(el.experiment_run_phase)
                                for el in self._experience_locations
                            ]
                        )
                    ),
                )
                res = dbh.execute(maq).all()
                memory = Memory(size_limit=len(res) + 2)
                for row in res:
                    if not (
                        row["muscle_sensor_readings"]
                        or row["muscle_actuator_setpoints"]
                    ):
                        continue
                    memory.append(
                        muscle_uid="pretrainer",
                        sensor_readings=row["muscle_sensor_readings"],
                        actuator_setpoints=row["muscle_actuator_setpoints"],
                        rewards=row["muscle_action_rewards"],
                        objective=row["muscle_action_objective"],
                        done=row["muscle_action_done"],
                    )
                self._brain._memory = memory
                LOG.info(
                    "%s preloaded %s actions out of %s data points "
                    "into its memory: Ready for a replay",
                    self,
                    len(memory),
                    len(res),
                )
        except Exception as e:
            LOG.error("%s could not load previous trajectories: %s", self, e)

    def setup(self):
        """Internal setup method of the Brain

        This method initializes the brain before the main loop (run) is called.
        It does, in order:

         1. Try to load a previous brain dump
         2. calls the ::`~Brain.setup` method
         3. Tries to load previous trajectories, filling the Brain's
            :class:`~Memory`
         4. Tries to do offline learing/pretraining (:meth:`Brain.pretrain()`)


        The internal setup method does not provide a hook for setup of
        derived brain classes. If you want to implement such a hook, implement
        the public :meth:`~Brain.setup` method.
        """
        assert self._brain is not None

        self._brain.try_load_brain_dump()
        self._brain.setup()
        self._try_load_previous_trajectories()
        self._brain.pretrain()

        # noinspection PyAttributeOutsideInit
        self.mdp_service = self.uid

    @ESM.on(MuscleUpdateRequest)
    async def _handle_muscle_update_request(
        self, request: MuscleUpdateRequest
    ) -> MuscleUpdateResponse:
        assert self._brain is not None

        LOG.debug(
            "%s will think about that breaking new %s that just arrived.",
            self,
            request,
        )
        self._brain.mode = request.mode
        self._rollout_workers |= {request.sender_rollout_worker_id}
        if (
            request.sensor_readings
            and request.actuator_setpoints
            and request.rewards
            and request.objective is not None
        ):
            self._brain.memory.append(
                muscle_uid=request.sender_rollout_worker_id,
                sensor_readings=request.sensor_readings,
                actuator_setpoints=request.actuator_setpoints,
                rewards=request.rewards,
                objective=np.array([request.objective]),
                done=request.done,
            )
        else:
            LOG.debug("Got empty MuscleUpdateRequest, ignoring: %s", request)

        # TODO: Currently, we use the thinking method also to init
        #   a muscle's policy during the test phase. Which is not ideal,
        #   because each brain implementation now has to check whether it is
        #   actually allowed to train. Instead, we should have a model
        #   getter that works independently of the thinking method.

        try:
            potential_update = self._brain.thinking(
                muscle_id=request.sender_rollout_worker_id,
                data_from_muscle=request.data,
            )
        except Exception as e:  # Catch-all of errors in third-party code
            LOG.error("%s did not think: %s", self._brain, e)
            potential_update = None
        if potential_update is not None:
            self._latest_update = potential_update
            self._updated.clear()
            self._updated[request.sender_rollout_worker_id] = True
        if not self._updated[request.sender_rollout_worker_id]:
            potential_update = self._latest_update
        statistics = self._brain.pop_statistics()

        # At this point, even when we're doing testing, everything should be
        # in order, so reduce the Brain's memory size during testing now:

        if request.mode == Mode.TEST:
            self._brain.memory.size_limit = 2

        fc = [
            (
                tc.__class__.__name__,
                tc.brain_flow_control(self._brain, request),
            )
            for tc in self._termination_conditions
        ]
        try:
            fci = SimulationFlowControl(max(x[1][0].value for x in fc))
        except ValueError:
            LOG.warning(
                "Could not determine flow control indicator; "
                "advertising CONTINUE. Check that you have any "
                "termination conditions defined."
            )
            fci = SimulationFlowControl.CONTINUE

        response = MuscleUpdateResponse(
            sender_brain_id=request.receiver_brain_id,
            receiver_muscle_id=request.sender_rollout_worker_id,
            experiment_run_id=request.experiment_run_id,
            experiment_run_phase=request.experiment_run_phase,
            experiment_run_instance_id=request.experiment_run_instance_id,
            flow_control_indicator=fci,
            flow_control_data={str(x[0]): x[1] for x in fc},
            update=potential_update,
            statistics=statistics,
        )
        return response

    @ESM.on(MuscleShutdownRequest)
    async def _handle_muscle_shutdown_request(
        self, request: MuscleShutdownRequest
    ):
        assert self._brain is not None

        self._rollout_workers -= {request.sender}
        LOG.info(
            '%s saw rollout worker "%s" requesting a break. Number of '
            "workers still online: %d",
            self.name,
            request.sender,
            len(self._rollout_workers),
        )
        self._brain.store()

        if len(self._rollout_workers) == 0:
            # noinspection PyUnresolvedReferences
            self.stop()  # type: ignore[attr-defined]
            LOG.info("Brain %s completed shutdown.", self.name)

        return (
            MuscleShutdownResponse(
                sender_brain_id=request.receiver_brain_id,
                receiver_muscle_id=request.sender_muscle_id,
                experiment_run_id=request.experiment_run_id,
                experiment_run_instance_id=request.experiment_run_instance_id,
                experiment_run_phase=request.experiment_run_phase,
            ),
            None if len(self._rollout_workers) == 0 else ESMFlags.KEEPALIVE,
        )

    def __str__(self):
        return "%s(id=0x%x, uid=%s)" % (
            self.__class__.__name__,
            id(self),
            self._uid,
        )
