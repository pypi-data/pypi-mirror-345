"""This module contains the abstract baseclass :class:`.Objective`,
from which all other objectives should be derived.

"""

from abc import ABC, abstractmethod
from typing import Optional, Union

import numpy as np

from .memory import Memory


class Objective(ABC):
    """The base class for all objectives.

    An objective defines the goal of an agent and changing the
    objective can, e.g., transform an attacker agent to a defender
    agent.

    The objective can, e.g., a wrapper for the reward of the
    environment and, in the easiest case, the sign of the reward
    is flipped (or not) to define attacker or defender. However, the
    objective can as well use a complete different
    formula.

    """

    def __init__(self, params: dict):
        self.params = params

    @abstractmethod
    def internal_reward(
        self, memory: Memory, **kwargs
    ) -> Optional[Union[np.ndarray, float]]:
        """Calculate the reward of this objective

        Parameters
        ----------
        memory : Memory
            The :class:`Memory` that can be accessed to calculate the
            objective. :meth:`Memory.tail` is most often used to get the *n*
            latest sensor readings, setpoints, or rewards.

        Returns
        -------
        objective : np.ndarray or float, Optional
            The agent's calculated objective value,
            i.e., the result of the agent's utility or goal function.
            This is based on any information
            that is stored in the agent's : class:`Memory`.
            It is either a numpy Array, a float, or an empty numpy array or
            ``None``.
            In the latter case (empty array or None),
            no objective is stored and all other information
            from the current action of the agent is discarded.
        """
        raise NotImplementedError
