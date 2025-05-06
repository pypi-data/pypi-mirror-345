from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, List, Dict, Tuple

from datetime import datetime
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from palaestrai.agent import SensorInformation
    from palaestrai.agent import RewardInformation
    from palaestrai.types import SimTime, SimulationFlowControl


@dataclass
class EnvironmentUpdateResponse:
    """Reports the current state of the environment.

    * Sender: :class:`~Environment`
    * Receiver: :class:`~SimulationController`

    Parameters
    ----------
    sender_environment_id : str
        ID of the sending :class:`~Environment`
    receiver_simulation_controller_id : str
        ID of the receiving :class:`~SimulationController`
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        ID of the :class:`~ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    environment_name : str
        User-given name of the environment
    sensors : List[SensorInformation]
        Current list of sensor data
    rewards : List[RewardInformation]
        Reward given by the environment
    done : bool
        Indicates whether the environment has reached a terminal state
    world_state : Any, default: None
        State of the world after optional transformation through a
        :class:`palaestrai.environment.WorldStateTransformer`
    simtime : Optional[palaestrai.types.SimTime]
        The current in-simulation time as provided by the environmment
    flow_control_data : Dict of str mapping to Tuple SimulationFlowControl, Any
        Complete flow control data: The dictionary's keys are the class names
        of the respective ::`TerminationCondition` classes,
        the values are the tuples as returned by the
        ::`TerminationCondition.brain_flow_control` method.
    walltime : datetime
        The time the message was created, default: :meth:`datetime.utcnow`
    """

    sender_environment_id: str
    receiver_simulation_controller_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    environment_name: str
    sensors: List[SensorInformation]
    rewards: List[RewardInformation]
    done: bool
    flow_control_indicator: SimulationFlowControl
    flow_control_data: Dict[str, Tuple[SimulationFlowControl, Any]] = field(
        default_factory=dict
    )
    world_state: Any = None
    simtime: Optional[SimTime] = None
    walltime: datetime = field(default_factory=datetime.now)

    @property
    def sender(self):
        return self.sender_environment_id

    @property
    def receiver(self):
        return self.receiver_simulation_controller_id

    @property
    def is_terminal(self):
        return self.done
