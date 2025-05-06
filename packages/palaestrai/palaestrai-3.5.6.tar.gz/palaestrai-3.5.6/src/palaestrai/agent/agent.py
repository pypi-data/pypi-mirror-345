"""This module contains the class :class:`Agent` that
stores all information regarding a specific agent.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, List, Dict

if TYPE_CHECKING:
    from .brain import Brain
    from .muscle import Muscle
    from . import SensorInformation, ActuatorInformation


@dataclass
class Agent:
    """Stores information about an agent.

    The agent class is used to store information about an
    agent. It is currently used by the simulation controller
    to have an internal representation of all agents.

    Parameters
    ----------
    uid: str
        The user-defined ID ("name") of an Agent.
    brain_classname: str
        Name of the class implementing the :class:`Brain` learner algorithm
    brain: :class:`palaestrai.agent.Brain`, optional
        An instance of a palaestrAI :class:`Brain`. Dynamically instanciated
        from the ::`Agent.brain_classname`.
    brain_params: dict
        This dictionary contains all parameters needed by the :class:`Brain`.
    muscle_classname: str
        Name of the class implementing the :class:`Muscle` inference algorithm
    muscles: dict of str, :class:`palaestrai.agent.Muscle`
        Internal UIDs to actual :class:`Muscle`. Since palaestrAI supports
        multi-worker setups, inference worker have an internal
        An instance of a palaestrai muscle. It
        defines what type of AI is used and is linked
        to the type of brain
    muscle_params: dict of str, any
        Algorithm-specific parameters as they are passed to each
        :class:`Muscle` instance
    sensors: list of :class:`SensorInformation`
        The list of sensors the agent is allowed to access.
    actuators: list of :class:`ActuatorInformation`
        The list of actuators the agent is allowed to access.
    """

    uid: str
    brain_classname: str
    brain: Optional[Brain]
    brain_params: Dict[str, Any]
    muscle_classname: str
    muscles: Dict[str, Optional[Muscle]]
    muscle_params: Dict[str, Any]
    sensors: List[SensorInformation]
    actuators: List[ActuatorInformation]
