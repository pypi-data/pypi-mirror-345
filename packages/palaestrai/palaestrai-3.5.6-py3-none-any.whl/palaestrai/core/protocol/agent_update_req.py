from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from palaestrai.agent import (
        SensorInformation,
        ActuatorInformation,
        RewardInformation,
    )
    from palaestrai.types import Mode, SimTime


@dataclass
class AgentUpdateRequest:
    """Provides fresh data from a :class:`SimulationController` to
    an :class:`Agent`.

    * Sender: :class:`SimulationController`
    * Receiver: :class:`RolloutWorker`

    Parameters
    ----------
    sender_simulation_controller : str
        The sending :class:`SimulationController`
    receiver_rollout_worker_id : str
        The receiving agent, e.g., a :class:`RolloutWorker`; i.e., the UID
        of the receiver is internal and not the name of :class:`Muscle` as it
        is defined in the :class:`ExperimentRun`).
    experiment_run_id : str
        ID of the current experiment run this agent participates in
    experiment_run_instance_id : str
        ID of the ::`ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    actuators : List of class:`ActuatorInformation`
        List of actuators available for the agent
    sensors : List of :class:`SensorInformation`
        Sensor input data for the agent
    rewards : List of :class:`RewardInformation`, optional
        Current reward from the environment. Warning: Supplying ``None`` here
        is sensible *only* when the environment has been set up initially,
        because for any other step, the :class:`Environment` must provide
        rewards.
    is_terminal : bool
        Indicates whether this is the last update from the environment or not
    mode : Mode
        Current mode of operation, e.g., Mode.TRAIN or Mode.TEST.
    simtimes : Dict[str, palaestrai.types.SimTime]
        Contains time values from the environment. It maps environment UIDs to
        either simtime_ticks (::`int`) or simtime_timestamps (::`datetime`)
        via the ::`SimTime` class.
    walltime : datetime.datetime, default: datetime.utcnow(datetime.UTC)
        The time the message was created
    """

    sender_simulation_controller_id: str
    receiver_rollout_worker_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    actuators: List[ActuatorInformation]
    sensors: List[SensorInformation]
    rewards: Optional[List[RewardInformation]]
    is_terminal: bool
    mode: Mode
    simtimes: Dict[str, SimTime] = field(default_factory=dict)
    walltime: datetime = field(default_factory=datetime.utcnow)

    @property
    def sender(self):
        return self.sender_simulation_controller_id

    @property
    def receiver(self):
        return self.receiver_rollout_worker_id
