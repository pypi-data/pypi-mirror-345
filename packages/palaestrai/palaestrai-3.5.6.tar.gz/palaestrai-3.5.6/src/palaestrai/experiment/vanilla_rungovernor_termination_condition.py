from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Any, Tuple

from .termination_condition import TerminationCondition
from .environment_termination_condition import EnvironmentTerminationCondition
from .max_episodes_termination_condition import MaxEpisodesTerminationCondition
from palaestrai.types import SimulationFlowControl

if TYPE_CHECKING:
    from palaestrai.core.protocol import SimulationControllerTerminationRequest
    from .run_governor import RunGovernor


class VanillaRunGovernorTerminationCondition(TerminationCondition):
    """A combination of environment and max episodes flow control

    This termination condition uses the environment termination condition and
    :py:class:`MaxEpisodesTerminationCondition` to end an *episode* when the
    environment terminates, and the *phase* when all workers have reached the
    maximum number of episodes limit.

    Example
    -------

    The following excerpt from a phase configuration shows an example of
    using this termination condition to end the phase once both workers
    have experienced 10 episodes each, where each episode runs until the
    environment terminates::


        schedule:
          - phase_0:
              # (Definition of environment and agents omitted.)
              simulation:
                name: palaestrai.simulation:Vanilla
                conditions:
                  - name: palaestrai.simulation:VanillaSimControllerTerminationCondition
                    params: {}
              phase_config:  # Additional config for this phase
                mode: train
                worker: 2
                episodes: 10
        run_config:
          condition:
            name: palaestrai.experiment:VanillaRunGovernorTerminationCondition
            params: {}
    """

    def __init__(self):
        self._max_episode_tc = MaxEpisodesTerminationCondition()
        self._env_tc = EnvironmentTerminationCondition()

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: Optional[Union[SimulationControllerTerminationRequest]],
    ) -> Tuple[SimulationFlowControl, Any]:
        dones = [
            self._max_episode_tc.phase_flow_control(run_governor, message),
            self._env_tc.phase_flow_control(run_governor, message),
        ]
        return sorted(dones, key=lambda x: x[0].value)[-1]
