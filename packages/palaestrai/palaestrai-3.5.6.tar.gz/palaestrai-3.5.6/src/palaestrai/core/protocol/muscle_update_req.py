from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from palaestrai.agent import (
        SensorInformation,
        RewardInformation,
        ActuatorInformation,
    )
    from palaestrai.types import SimTime, Mode


@dataclass
class MuscleUpdateRequest:
    """Notifies the :class:`Brain` that a :class:`Muscle` of an action.

    * Sender: A :class:`Muscle` after acting
    * Receiver: The :class:`Brain`

    Parameters
    -----------
    sender_rollout_worker_id : str
        The unique internal ID of the rollout worker
    receiver_brain_id : str
        The UID of the receiving brain
    muscle_uid : str
        The unique user-defined ID of the agent
    sensor_readings : list of :class:`SensorInformation`
        List of sensor information on which the muscle
        acted, not the scaled/transformed values which are given to the network
        Can be ``None`` when the environment is just initialized
    actuator_setpoints : list of :class:`ActuatorInformation`
        The actuator setpoints as the agent wants to apply them to the
        environment.
        Can be ``None`` when the environment is just initialized
    rewards : list of class:`RewardInformation`
        Rewards received from the previous action
        Can be ``None`` when the environment is just initialized
    objective : float
        The objective value of the agent; a single-value float based on the
        agents objective function (cf. :class:`Objective`)
    done : bool
        Indicates whether this was the last action as the current episode is
        done.
    data : any
        Any data that the :class:`~.Muscle` wants to send to its
        :class:`~.Brain`. This is algorithm-specific.
    statistics : dict of str, any; optional
        Contains a mapping of metric keys to values. This
        dynamically allows various implementation-dependent statistics
        metrics.
    simtimes : dict of str, :class:`palaestrai.types.SimTime`
        Contains time values from the environment. It maps environment UIDs to
        either simtime_ticks (::`int`) or simtime_timestamps (::`datetime`)
        via the :class:`SimTime` class.
    walltime : ::`datetime.datetime`, default: datetime.now(datetime.UTC)
        The time the message was created
    """

    sender_rollout_worker_id: str
    receiver_brain_id: str
    muscle_uid: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    sensor_readings: Optional[List[SensorInformation]]
    actuator_setpoints: Optional[List[ActuatorInformation]]
    rewards: Optional[List[RewardInformation]]
    objective: float
    done: bool
    mode: Mode
    data: Any
    statistics: Optional[Dict[str, Any]]
    simtimes: Dict[str, SimTime] = field(default_factory=dict)
    walltime: datetime = field(default_factory=datetime.utcnow)

    @property
    def sender(self):
        return self.sender_rollout_worker_id

    @property
    def receiver(self):
        return self.receiver_brain_id

    @property
    def is_terminal(self):
        return self.done
