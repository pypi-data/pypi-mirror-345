from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Optional, Union, Any, Tuple, Dict

import re
import logging
import numpy as np
from itertools import chain
from dataclasses import dataclass
from collections import defaultdict, deque, namedtuple

from palaestrai.types import SimulationFlowControl
from .termination_condition import TerminationCondition

if TYPE_CHECKING:
    from palaestrai.agent import Brain
    from palaestrai.experiment import RunGovernor
    from palaestrai.core.protocol import (
        SimulationControllerTerminationRequest,
        MuscleUpdateRequest,
    )


@dataclass
class _WorkerCumSums:
    done: bool
    worker_sums: Dict


LOG = logging.getLogger(__name__)


class AgentObjectiveTerminationCondition(TerminationCondition):
    """Brain controls execution flow of experiments

    This termination condition allows to control the simulation flow based on
    the overall success of an agent.

    Users may supply any objective average to terminate the flow, which will
    lead to a ::`SimulationFlowControl.RESET` during for an episode, and
    ::`SimulationFlowControl.STOP_PHASE` on phase flow control level.
    I.e., when an agent becomes successful during an episode, it will request
    to restart that episode.
    If the agent becomes successful over a number of episodes,
    the phase will end.

    Threshhold values are given in the termination condition's parameters for
    each agent.
    Under each agent key, the actual threshhold values are given.
    The keys follow a specific pattern:
    {brain|phase}_avg{number}, where "{brain|phase}" means either "brain" or
    "phase, and "number" is the number for the floating average.

    ``brain_avgN`` specifies that an agent signals to end an episode once the
    mean of the last *N* objective values is equal or more than the number
    given. The simulation controller can then decide to end the episode.
    This change in flow control is only relevant for the current worker; i.e.,
    other workers will continue until they are equally successful,
    or the phase ends for another reason.

    ``phase_avgN`` signals termination of a *phase* once the *cumulative*
    reward of the last *N* episodes is equal to or greater than the number
    given. I.e., this parameter considers the cumulative reward of all workers,
    since a worker act within one particular episode.

    E.g.,

    * ``brain_avg100: 8.9`` as parameter means that the episode ends once the
      brain reaches an objective score of at least 8.9, averaged over the last
      100 actions.
    * ``brain_avg10: 8.9``: similar to the above, except that the averaging is
      done over 10 actions.
    * ``phase_avg10: 1.0``: ends the phase once the average cumulative success
       of the brain from the last 10 *episodes* is at least 1.0.

    If you specify any ``avgN``, then the termination condition
    will ensure that at least *N* actions are recorded before calculating the
    average.

    .. note::
        For technical reasons, you must specify a ``brain_avg*`` parameter
        if you want to use ``phase_avg*``, as the result of a brain objective
        averaging is transmitted to the phase-specific portion of the
        termination condition.

        However, a special case exist when specifying a ``brain_avgN``
        parameter, but not a ``brain_avgN`` parameter. Then, the first agent
        that triggers the termination condition during an episode will end
        the whole phase.

    Examples
    --------

    The following snipped is a shortened example from palaestrAI's
    experiment definition::

        definitions:
          agents:
            myagent:
              name: My Agent
              # (Other agent definitions omitted)
          simulation:
            tt:
              name: palaestrai.simulation:TakingTurns
              conditions:
                - name: palaestrai.experiment:AgentObjectiveTerminationCondition
                  params:
                    My Agent:
                      brain_avg100: 8.9
                      phase_avg1: 8.9
    """

    _AVG_RE = re.compile(r"(brain|phase)_avg(\d+)\Z")

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._brain_avgs = defaultdict(dict)
        self._phase_avgs = defaultdict(dict)
        self._stop_phase_for_all = False

        for auid, conds in kwargs.items():
            if not isinstance(conds, dict):
                continue
            for k, v in conds.items():
                m = re.search(
                    AgentObjectiveTerminationCondition._AVG_RE, str(k)
                )
                if m and m.group(1) == "brain":
                    self._brain_avgs[auid][int(m.group(2))] = float(v)
                if m and m.group(1) == "phase":
                    self._phase_avgs[auid][int(m.group(2))] = float(v)
        if len(self._brain_avgs) == 0 and len(self._phase_avgs) == 0:
            LOG.warning(
                "%s condition does not have any configuration. This "
                "will essentially be a noop. "
                "Please check your arguments: %s",
                self.__class__.__name__,
                kwargs,
            )
        self._max_cumulative_objectives = 0
        self._cumulative_objectives = defaultdict(self._new_worker_cumsums)
        if self._phase_avgs:
            self._max_cumulative_objectives = max(
                chain.from_iterable(
                    i.keys() for i in self._phase_avgs.values()
                )
            )

    def _new_worker_cumsums(self):
        return _WorkerCumSums(
            done=False, worker_sums=defaultdict(self._new_worker_sums_deque)
        )

    def _new_worker_sums_deque(self):
        return deque(maxlen=self._max_cumulative_objectives)

    def brain_flow_control(
        self, brain: Brain, message: MuscleUpdateRequest
    ) -> Tuple[SimulationFlowControl, Dict]:
        """Allows a learning process to control the simulation flow.

        A learner can control the simulation, e.g., by indicating that the
        simulation should be reset or can end when it has become good enough.
        Descendant classes can reimplement this method. They will receive
        access to the respective agent's ::`Brain`, which contains all the
        necessary information (e.g., its memory, training success, etc.)

        Returns
        -------
        Tuple of ::`SimulationFlowControl` and Dict:
            An indicator for simulation control: The flow control indicator
            with the highest priority (i.e., highest value number in the
            enum) wins.
            The second element contains the dictionary of computed averages,
            indexed by the agent's name.
            E.g.,, ``{"my_agent_name": {10: 5.6}}``
        """
        conditions = self._brain_avgs[brain.name]
        windows = sorted(list(conditions.keys()))
        fc_data = {
            brain.name: {
                w: np.mean(
                    brain.memory.tail(
                        w, include_only=[message.sender]
                    ).objective
                )
                for w in windows
                if len(brain.memory.tail(w)) == w
            }
        }
        fc = (
            SimulationFlowControl.RESET
            if any(v >= conditions[k] for k, v in fc_data[brain.name].items())
            else SimulationFlowControl.CONTINUE
        )
        fc_data[brain.name]["sum"] = (
            brain.memory.tail(len(brain.memory)).objective.sum().item()
        )  # Add this for phase fc
        if fc.value > SimulationFlowControl.CONTINUE.value:
            LOG.info(
                "%s's rollout worker %s "
                "meets objective value termination condition "
                "for this episode: %s",
                brain.name,
                message.sender,
                fc_data,
            )
        else:
            LOG.debug(
                "%s needs to continue: %s < %s",
                brain.name,
                fc_data[brain.name],
            )
        return fc, fc_data

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: SimulationControllerTerminationRequest,
    ) -> Tuple[SimulationFlowControl, Any]:
        if self._stop_phase_for_all:  # Short-circuit of wanted
            return SimulationFlowControl.STOP_PHASE, {}

        if (
            message.flow_control_indicator.value
            < SimulationFlowControl.RESET.value
        ):  # Safety check, consider only RESET and above:
            return message.flow_control_indicator, {}

        if not self._phase_avgs:  # End phase once one worker is successful
            self._stop_phase_for_all = True
            return SimulationFlowControl.STOP_PHASE, {}

        assert run_governor.experiment_run is not None

        # When the SC requests termination, it usually means that something
        # has ended. So we at least want to RESET.
        # Otherwise, we'll just go through all cumulative sums.

        for brain, conditions in message.flow_control_data.get(
            self.__class__.__name__, (SimulationFlowControl.CONTINUE, {})
        )[1].items():
            brain_data = self._cumulative_objectives[brain]
            if brain_data.done:  # Any worker was already successful
                return SimulationFlowControl.STOP_PHASE, {}
            cumsums = brain_data.worker_sums[message.sender]
            cumsums.append(conditions["sum"])
            target_conds = self._phase_avgs[brain]
            for win, target in target_conds.items():
                if win <= 0:  # Safety net for user data
                    return SimulationFlowControl.RESET, {}
                if len(cumsums) < win:
                    continue
                recorded_sum = sum(
                    i
                    for i in itertools.islice(
                        cumsums, len(cumsums) - win, len(cumsums)
                    )
                )
                avg = recorded_sum / float(
                    win
                    * len(
                        run_governor.experiment_run.simulation_controllers(
                            run_governor.current_phase
                        )
                    )
                )
                if avg >= target:
                    LOG.info(
                        "%s terminates the current phase "
                        "according to %s having avg%d %.2f > %.2f",
                        self.__class__.__name__,
                        brain,
                        win,
                        avg,
                        target,
                    )
                    brain_data.done = True
                    return SimulationFlowControl.STOP_PHASE, {
                        win: recorded_sum
                    }

        # Usual default case is RESET:
        return SimulationFlowControl.RESET, {}

    def check_termination(self, message, component=None):
        return False
