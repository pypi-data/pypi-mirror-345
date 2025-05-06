from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from palaestrai.types import SimTime
    from palaestrai.agent import SensorInformation, RewardInformation


@dataclasses.dataclass
class EnvironmentState:
    """Describes the current state of an :class:`~Environment`.

    This dataclass is used as return value of the :meth:`~Environment.update()`
    method. It contains current sensor readings, reward of the environment,
    indicates whether the environment has terminated or not, and finally gives
    time information.

    Attributes
    ----------
    sensor_information : List[SensorInformation]
        List of current sensor values after evaluating the environment
    rewards : List[RewardInformation]
        Current rewards given from the environment
    done : bool
        Whether the environment has terminated (``True``) or not (``False``)
    world_state : Any (default: None)
        Current state of the world (whatever the environment thinks it is)
    simtime: SimTime (default: None)
        Environment starting time
    """

    sensor_information: List[SensorInformation]
    rewards: List[RewardInformation]
    done: bool
    world_state: Any = None
    simtime: Optional[SimTime] = None
