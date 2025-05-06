from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple, Optional, Any

import numpy as np

import asyncio
import logging
from asyncio import Future
from inspect import isawaitable

from palaestrai.types import Mode
from palaestrai.core import EventStateMachine as ESM
from palaestrai.core.protocol import (
    AgentShutdownRequest,
    AgentShutdownResponse,
    AgentUpdateRequest,
    AgentUpdateResponse,
    EnvironmentResetNotificationRequest,
    EnvironmentResetNotificationResponse,
    MuscleShutdownRequest,
    MuscleUpdateRequest,
    MuscleUpdateResponse,
    MuscleShutdownResponse,  # ErrorIndicator
)
from palaestrai.agent import Memory

if TYPE_CHECKING:
    from palaestrai.agent import (
        Muscle,
        Objective,
        SensorInformation,
        ActuatorInformation,
        RewardInformation,
    )
    from palaestrai.types import SimTime

LOG = logging.getLogger(__name__)


@ESM.monitor(is_mdp_worker=True)
class RolloutWorker:
    """
    Worker wrapper around :class:`Muscle`s.

    A :class:`Muscle` is the inference part of any algorithm.
    It is the acting entity in an :class:`Environment`: Given sensory
    inputs, it chooses the appropriate actions.
    However, algorithm implementors do not have to concern themselves with the
    details of palaestrAI's inner workings (e.g., the message broker).
    Therefore, RolloutWorkers wrap :class:`Muscle`s and connect to the
    majordomo broker, handle messages, etc.

    Parameters
    ----------
    muscle : Muscle
        The actual ::`Muscle` (the inference part of an agent's implementation)
        that this rollout worker wrap
    objective : Objective
        The :class:`Objective` that calculates an agent's objective values
        (utility/goal function)
    uid : str
        The internal unique ID of this rollout worker. This is opposed to the
        UID of a :class:`Muscle` (cf. ::`Muscle.uid`): The rollout worker's
        UID is the internal, unique ID used in communications, whereas the
        :class:`Muscle.uid` is the unique *name* of the agent (as per the
        user-defined :class:`ExperimentRun` file). This distinction exists,
        because for multi-worker support, we still need to distinguish
        individual rollout workers, whereas they are just instances of the
        same Agent.
    brain_uid : str
        The UID of the :class:`Brain` that learns from the :class:`Muscle`'s
        actions
    """

    def __init__(
        self, muscle: Muscle, objective: Objective, uid: str, brain_uid: str
    ):
        self._uid = uid
        self._brain_uid = brain_uid

        self._muscle = muscle
        self._objective = objective
        self._memory = Memory()

        self._done: bool = False
        self._experiment_run_id: Optional[str] = None
        self._experiment_run_instance_id: Optional[str] = None
        self._experiment_run_phase: Optional[int] = None

        self._model_loaded: bool = False

        # Store state of t-1 to match s, a, and r.
        #   If a state at time t leads to an action, the reward of this action
        #   is visible during the next step. I.e., r(t) arrives at t+1.
        #   Therefore, we temporary store readings and setpoints
        #   of the previous step:
        self._previous_simtimes: Optional[Dict[str, SimTime]] = None
        self._previous_sensor_readings: Optional[List[SensorInformation]] = (
            None
        )
        self._previous_actuator_setpoints: Optional[
            List[ActuatorInformation]
        ] = None
        self._previous_data_for_brain: Any = None
        self._previous_statistics: Optional[Dict[str, Any]] = None

        self._future_agent_update: Optional[Future] = None
        self._future_muscle_shutdown: Optional[Future] = None

    @property
    def uid(self):
        """
        Unique ID of this Rollout Worker.

        The UID of the Rollout Worker is different from that of the
        :class:`Muscle` it wraps.
        palaestrAI supports multi-worker setups (i.e., one :class:`Brain` is
        fed data from several instances of the same :class:`Muscle`),
        hence, palaestrAI needs to internally distinuguish the different
        Rollout Workers.
        In order to find the actual UID ("name") of the acting muscle,
        have a look at :class:`Muscle.uid` (cf. ::`RolloutWorker.muscle`).

        Returns
        -------
        rollout_worker_uid : str
            The generated, unique (internal) ID of this Rollout Worker.
        """
        return self._uid

    @property
    def muscle(self) -> Muscle:
        assert self._muscle is not None
        return self._muscle

    @property
    def mode(self):
        """Current execution ::`~Mode` of this muscle (e.g., training)"""
        assert self._muscle is not None
        return self._muscle.mode

    def setup(self):
        self._future_agent_update = asyncio.get_running_loop().create_future()

        self.prepare_model_for_inference_muscle()
        try:
            self._muscle.setup()
        except Exception as e:  # Catch-all because of user-defined code
            LOG.exception(
                'Setup of muscle "%s" failed with %s.', self._muscle, e
            )

        # noinspection PyAttributeOutsideInit
        self.mdp_service = self.uid
        LOG.debug("%s waiting for requests: Act, not think!", self)

    def prepare_model_for_inference_muscle(self):
        if self.mode == Mode.TEST and not self._model_loaded:
            try:
                self._muscle.prepare_model()
                self._model_loaded = True
            except Exception:
                LOG.exception(
                    f"{str(self)}: Error while preparing model. "
                    "This muscle is likely to be stupid as hell."
                )
                raise

    def _remember(self, request: AgentUpdateRequest):
        self._memory.append(
            self.uid,
            sensor_readings=self._previous_sensor_readings,
            actuator_setpoints=self._previous_actuator_setpoints,
            rewards=request.rewards,
            done=request.is_terminal,
        )
        try:
            objective = self._objective.internal_reward(self._memory)
        except Exception as e:  # Whatever may happen in userland...
            LOG.exception(
                "Could not calculate objective %s: %s. "
                "Will substitute with 0.0 just to be defensive, "
                "but your results will be screwed.",
                self._objective,
                e,
            )
            objective = 0.0
        self._memory.append(self.uid, objective=np.array([objective]))

    @ESM.on(AgentUpdateRequest)
    async def _handle_agent_update(self, request: AgentUpdateRequest):
        """
        Handle an agent update.

        :class:`~AgentUpdateRequest`s contain new data from our environment(s),
        i.e., :class:`~SensorInformation` and :class:`~RewardInformation`
        objects. For each such request, the task of the muscle is to infer
        actions.

        Muscles distinguish between two modes, training and test. They are
        set in the experiment run configuration for a phase.

        In *training mode*, every update request to the muscle is forwarded
        to the brain. The brain answers with information that the muscle can
        use to update itself.

        In *testing mode*, the serialized brain instance is loaded and
        inference is done only through this, without updates from a brain
        instance.

        Finally, an update response is prepared.

        Parameters
        ----------
        request : AgentUpdateRequest
            The update request from the simulation controller.
            Contains, among other information, the current sensor
            readings and the reward of the previous actions.

        Returns
        -------
        AgentUpdateResponse
            The update response with the agent's actions.
        """
        LOG.debug("%s received %s", self, request)
        assert self.uid is not None
        assert self._muscle is not None

        self._experiment_run_id = request.experiment_run_id
        self._experiment_run_instance_id = request.experiment_run_instance_id
        self._experiment_run_phase = request.experiment_run_phase

        assert self._experiment_run_id is not None
        assert self._experiment_run_instance_id is not None
        assert self._experiment_run_phase is not None
        assert isawaitable(self._future_agent_update)

        self._muscle._mode = request.mode
        self._done = request.is_terminal

        # Remember values only if there is something to remember from the
        # previous action. At first, we don't have the full (s, a, s', r)
        # quadruplet to remember, so skip this.

        if (
            self._previous_sensor_readings is not None
            and self._previous_actuator_setpoints is not None
            and request.rewards is not None
        ):
            self._remember(request)

        # Even if there is nothing to remember, we current send out a
        # MuscleUpdateRequest, because only then the Brain will provide us with
        # a model. This is especially crucial *initially*,
        # because the Muscle starts without a model.
        # TODO: We really need an independent getter here.

        self._future_agent_update = asyncio.get_running_loop().create_future()
        _ = self._request_muscle_update(
            sensors=self._previous_sensor_readings,
            actuators=self._previous_actuator_setpoints,
            rewards=request.rewards,
            objective=(
                self._memory.tail(1).objective.item()
                if len(self._memory) > 0
                else 0.0
            ),
            data_for_brain=self._previous_data_for_brain,
            statistics=self._previous_statistics,
            simtimes=self._previous_simtimes,
        )
        await self._future_agent_update
        mursp: MuscleUpdateResponse = self._future_agent_update.result()

        setpoints, data_for_brain = RolloutWorker.try_propose_actions(
            self._muscle, request.sensors, request.actuators
        )
        self._previous_simtimes = request.simtimes
        self._previous_sensor_readings = request.sensors
        self._previous_actuator_setpoints = setpoints
        self._previous_data_for_brain = data_for_brain
        try:  # Update statistics
            # The brain should have sent us something, and if not, we'll
            # initialize with an empty dict.
            self._previous_statistics = (
                self._future_agent_update.result().statistics or {}
            )
            self._previous_statistics.update(self._muscle.pop_statistics())
        except Exception as e:  # Catch-all for malicious user code!! >:-] if
            # Muscle.pop_statistics is overwritten
            LOG.error(
                "Could not update statistics, "
                "either Brain (%s) or Muscle (%s) "
                "sent non-dict garbage: %s",
                self._brain_uid,
                self._muscle,
                e,
            )

        return AgentUpdateResponse(
            sender_rollout_worker_id=self.uid,
            receiver_simulation_controller_id=request.sender,
            experiment_run_id=self._experiment_run_id,
            experiment_run_instance_id=self._experiment_run_instance_id,
            experiment_run_phase=self._experiment_run_phase,
            actuator_information=setpoints,
            sensor_information=request.sensors,
            flow_control_indicator=mursp.flow_control_indicator,
            flow_control_data=mursp.flow_control_data,
        )

    @ESM.requests
    def _request_muscle_update(
        self,
        sensors: List[SensorInformation],
        actuators: List[ActuatorInformation],
        rewards: List[RewardInformation],
        objective: float,
        data_for_brain: Any,
        statistics: Dict[str, Any],
        simtimes: Dict[str, SimTime],
    ):
        assert self._experiment_run_id is not None
        assert self._experiment_run_instance_id is not None
        assert self._experiment_run_phase is not None

        LOG.debug(
            "%s"
            "sending MuscleUpdateRequest(experiment_run_id=%s)"
            "for instance=%s in phase=%s",
            self,
            self._experiment_run_id,
            self._experiment_run_instance_id,
            self._experiment_run_phase,
        )

        assert self.uid is not None
        assert self._brain_uid is not None

        return MuscleUpdateRequest(
            sender_rollout_worker_id=self.uid,
            receiver_brain_id=self._brain_uid,
            muscle_uid=self._muscle.uid,
            sensor_readings=sensors,
            actuator_setpoints=actuators,
            experiment_run_id=self._experiment_run_id,
            experiment_run_instance_id=self._experiment_run_instance_id,
            experiment_run_phase=self._experiment_run_phase,
            rewards=rewards,
            objective=objective,
            done=self._done,
            mode=self.mode,
            data=data_for_brain,
            statistics=statistics,
            simtimes=simtimes,
        )

    @ESM.on(MuscleUpdateResponse)
    async def _handle_muscle_update_response(
        self, response: MuscleUpdateResponse
    ):
        assert self._muscle is not None
        assert self._future_agent_update is not None

        if response.has_update():
            try:
                self._muscle.update(response.update)
            except Exception as e:  # User code lurks above...
                LOG.exception(
                    "%s could not update: %s. Some people never learn...",
                    self,
                    str(e),
                    e,
                )
        self._future_agent_update.set_result(response)

    @staticmethod
    def try_propose_actions(
        muscle: Muscle,
        sensors: List[SensorInformation],
        actuators: List[ActuatorInformation],
    ) -> Tuple[List[ActuatorInformation], Any]:
        assert muscle is not None
        setpoints: List[ActuatorInformation] = []
        data_for_brain = None

        try:
            data = muscle.propose_actions(sensors, actuators)
            if isinstance(data, tuple):
                setpoints, data_for_brain = data
            else:
                setpoints = data
        except Exception as ex:  # Catch-all for malicious user code!! >:-]
            LOG.exception(
                "%s: propose_actions(sensors=%s, actuators_available=%s) "
                "returned exception. Returning no actions and trying to "
                "continue next time.",
                muscle,
                sensors,
                actuators,
                exc_info=ex,
            )
        return setpoints, data_for_brain

    @ESM.on(EnvironmentResetNotificationRequest)
    async def _handle_environment_reset_notification(
        self, request: EnvironmentResetNotificationRequest
    ) -> EnvironmentResetNotificationResponse:
        """
        Handle notification about environment reset.

        Whenever an environment has finished and a new episode is
        started, a notification is sent to the agents.
        The corresponding method an agent implementation should provide in
        this case is :meth:`Muscle.reset`.

        Parameters
        ----------
        request: EnvironmentResetNotificationRequest
            The notification request from the simulation controller.

        Returns
        -------
        EnvironmentResetNotificationResponse
            The response for the simulation controller.
        """
        assert self._muscle is not None
        self._muscle.reset()
        return EnvironmentResetNotificationResponse(
            receiver_simulation_controller_id=request.sender,
            sender_muscle_id=self.uid,
        )

    @ESM.on(AgentShutdownRequest)
    async def _handle_agent_shutdown_request(
        self, request: AgentShutdownRequest
    ):
        """
        Handle agent shutdown.

        This method informs the correesponding ::`Brain` that this Muscle
        shuts down.
        What happens because of this is up to the Brain;
        but an acknowledgement via :class:`MuscleShutdownResponse` is required.

        Parameters
        ----------
        request : AgentShutdownRequest
            The shutdown request from the simulation controller. This
            message has no further information that need to be
            processed.

        Returns
        -------
        AgentShutdownResponse
            The shutdown response that confirms the shutdown of the
            muscle.
        """
        LOG.info("%s is shutting down: Now I'm sore.", self.uid)

        assert self._brain_uid is not None
        assert self._experiment_run_id is not None
        assert self._experiment_run_instance_id is not None
        assert self._experiment_run_phase is not None

        # Explicitly await the response here, because the protocol requires
        #   that we take care of the response before stopping:
        self._future_muscle_shutdown = (
            asyncio.get_running_loop().create_future()
        )
        _ = self._request_muscle_shutdown()
        await self._future_muscle_shutdown

        # Needs to stop here instead, because with stop being called from
        # _handle_muscle_shutdown_response the AgentShutdownResponse
        # does not get sent
        # noinspection PyUnresolvedReferences
        self.stop()  # type: ignore[attr-defined]

        return AgentShutdownResponse(
            sender=self.uid,
            receiver=self._brain_uid,
            experiment_run_id=self._experiment_run_id,
            experiment_run_instance_id=self._experiment_run_instance_id,
            experiment_run_phase=self._experiment_run_phase,
        )

    @ESM.requests
    def _request_muscle_shutdown(self):
        assert self._brain_uid is not None
        assert self._experiment_run_id is not None
        assert self._experiment_run_instance_id is not None
        assert self._experiment_run_phase is not None

        return MuscleShutdownRequest(
            sender_muscle_id=self.uid,
            receiver_brain_id=self._brain_uid,
            experiment_run_id=self._experiment_run_id,
            experiment_run_instance_id=self._experiment_run_instance_id,
            experiment_run_phase=self._experiment_run_phase,
        )

    @ESM.on(MuscleShutdownResponse)
    async def _handle_muscle_shutdown_response(
        self, response: MuscleShutdownResponse
    ):
        LOG.debug("%s may finally rest: %s", self, response)
        assert self._future_muscle_shutdown is not None
        self._teardown_muscle()
        self._future_muscle_shutdown.set_result(response)

    def _teardown_muscle(self):
        # Run any muscle teardown code, if available, and catch any errors.
        try:
            self._muscle.teardown()
        except Exception as e:  # Yep, catch-all
            LOG.error(
                "%s encountered an error when calling teardown() on %s: %s",
                self,
                self._muscle,
                e,
            )

    def __str__(self):
        return f"{self.__class__}(id=0x{id(self):x}, uid={self.uid})"
