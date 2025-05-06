from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

from palaestrai.agent.memory import Memory
from palaestrai.agent.objective import Objective


class DummyObjective(Objective):
    """A simple objective that sums all environment rewards

    This objective is a simple pass-through objective that sums up the
    :class:`RewardInformation` from the latest addition to an agent's
    :class:`Memory`.
    I.e., it uses :meth:`Memory.tail` to get the latest row, and then sums all
    :class:`RewardInformation` objects that were stored here.
    I.e., ``sum(memory.tail(1).rewards)``.

    This can be used as a pass-through for the simpler reinforcement learning
    cases, in which the environment's reward is also the agent's objective
    function.
    It can also act as a simple dummy (i.e., placeholder) for a more meaningful
    objective function.
    """

    def __init__(self, params=None):
        super().__init__(params=({} if params is None else params))

    def internal_reward(self, memory: Memory, **kwargs) -> float:
        rewards = memory.tail(1).rewards
        if len(rewards) == 0:
            value = 0.0
        else:
            value = rewards.sum(axis=1)[0]
        return float(value)
