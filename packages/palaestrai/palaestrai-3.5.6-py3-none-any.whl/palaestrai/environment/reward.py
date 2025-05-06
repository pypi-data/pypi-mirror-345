from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from palaestrai.agent import RewardInformation
    from palaestrai.environment import EnvironmentState


class Reward(ABC):
    """Implements the calculation of a reward.

    The state of an environment can be described in terms of a reward. In
    reinforcement learning, reward is a scalar issued by a state transition,
    i.e., by a change in the enviornment's state. Rewards help the agents to
    learn, because they strive to maximize the long-term (or cumulative) reward
    of their actions.

    Many environments do not need a separate command pattern class to
    calculate the reward, as the current "performance" of the environment
    is, in many cases easy, to calculate, and there is also no reason to make
    rewards modular. An example would be the cartpole environment, where the
    reward is simply the number of frames the pole remains upright; there is
    no other information coming out of the environment that describes its
    state. Another example is Tic-Tac-Toe, where the board yields the reward.

    However, more complex environments elude the definite calculate of a
    reward. Power grids are an example for this; depending on the goal of the
    agent, any number of values might be of interest. Moreover, the "health"
    of a grid cannot be ascertained by one simple scalar alone. Hence, modular
    reward definitions that depend on the experiment currently conducted are
    important.

    Complex environments with multiple agents split :class:`Reward` and
    :class:`Objective`: The reward is issued by the environment and, basically,
    describes the current performance or state of an environment. It can be
    a scalar, but could also be something more complex (e.g., a vector). How
    good the current state of an environment is for an agent depends on the
    agent's goal, so each agent has an ::`Objective` that receives the current
    reward and calculates the agent's internal objective value ("internal
    reward," so to say) from it.

    This abstract base class defines the interface for the reward of an
    ::`Environment`. It is loaded dynamically from an experiment run file
    through the key `phase.<N>.<PHASE NAME>.environments.<M>.reward`.
    """

    def __init__(self, **kwargs):
        self._parameters = kwargs

    @abstractmethod
    def __call__(self, *states: List[EnvironmentState]) -> RewardInformation:
        """Calculates the current reward.

        This method calculates the current reward, which can be interpreted as
        the current "performance" of the environment. It can receive one or
        many ::`EnvironmentState` objects, depending on how the environment
        works. Usually, one is provided. If a reward implementation needs to
        know the past state(s), too, the derived class must save it itself.

        Parameters
        ----------
        *states : List[EnvironmentState]
            An (exploded) list of ::`EnvironmentState` objects; at least the
            current state is usually supplied.

        Returns
        -------
        ::`RewardInformation`:
            The reward issued by this object's calculation.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(id=0x{id(self):x}"
