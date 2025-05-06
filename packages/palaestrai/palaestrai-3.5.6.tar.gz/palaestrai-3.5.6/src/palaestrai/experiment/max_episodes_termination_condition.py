from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Tuple, Any

import logging

from .termination_condition import TerminationCondition
from ..core.protocol import SimulationControllerTerminationRequest
from ..types import SimulationFlowControl

if TYPE_CHECKING:
    from palaestrai.experiment import RunGovernor

LOG = logging.getLogger(__name__)


class MaxEpisodesTerminationCondition(TerminationCondition):
    """Checks whether a maximum number of episodes has been exceeded.

    This termination condition will only trigger on phase level.
    It uses the ``episodes`` key in the phase configuration to check
    whether a maximum number of episodes has been reached.

    Examples
    --------

    Consider the following experiment phase definition::

        schedule:
          Training:
            phase_config:
              mode: train
              worker: 2
              episodes: 100
            simulation:
              conditions:
              - name: palaestrai.experiment:MaxEpisodesTerminationCondition
                params: {}
              name: palaestrai.simulation:TakingTurns
        run_config:
          condition:
            name: palaestrai.experiment:MaxEpisodesTerminationCondition
            params: {}


    Then, the phase would end when both workers (``worker: 2``) have reached
    100 episodes (``episodes: 100``).
    """

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: SimulationControllerTerminationRequest,
    ) -> Tuple[SimulationFlowControl, Any]:
        if not isinstance(message, SimulationControllerTerminationRequest):
            return SimulationFlowControl.CONTINUE, None
        if run_governor.experiment_run is None:
            LOG.warning(
                "MaxEpisodesTerminationCondition cannot control flow: "
                "Run governor has no experiment run object!"
            )
            return SimulationFlowControl.CONTINUE, None
        try:
            max_episodes = run_governor.experiment_run.get_episodes(
                run_governor.current_phase
            )
        except KeyError:
            # If the current phase does not define a phase limit, we can
            # continue indefinitely.
            return SimulationFlowControl.CONTINUE, None

        # If all SCs have reached the max number of episodes, indicate end of
        # the phase:

        if all(
            x >= max_episodes
            for x in run_governor.current_episode_counts.values()
        ):
            return SimulationFlowControl.STOP_PHASE, None

        # If only the current one, indicate shutdown of the current simulation
        # controller:

        sc_uid = message.sender
        if run_governor.current_episode_counts[sc_uid] >= max_episodes:
            return SimulationFlowControl.STOP_SIMULATION, None
        return SimulationFlowControl.CONTINUE, None
