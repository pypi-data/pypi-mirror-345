"""This module contains the class :class:`RewardInformation` that stores all
information the agents need about a single reward."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Union, Any

import warnings
import numpy as np

from palaestrai.agent.util.space_value_utils import (
    check_value_is_none,
    assert_value_in_space,
)
from palaestrai.types import Space

if TYPE_CHECKING:
    import palaestrai.types

LOG = logging.getLogger(__name__)


class RewardInformation:
    """
    Stores information about a single reward.

    Once created, a *RewardInformation* object can be called to
    retrieve its value, e.g.,:

        a = RewardInformation(42, some_space)
        a()  # => 42
        a.reward_value  # => 42


    Parameters
    ----------
    value : Any
        The value of the reward's last reading. The type of this value
        is described by :attr:`space`
    space : palaestrai.types.Space
        An instance of a palaestrai space object defining the type of
        the value
    uid : Optional[str]
        A unique identifier for this reward. The agents use the ID only
        for assignment of previous values with the same ID. The ID is
        important, if multiple rewards are available and/or the reward
        is a delayed reward.
    reward_value : Any
        *Deprecated* in favor of value
    observation_space : palaestrai.types.Space
        *Deprecated* in favor of space
    reward_id : Optional[str]
        *Deprecated* in favor of uid
    """

    def __init__(
        self,
        value: Optional[Union[int, float, np.ndarray]] = None,
        space: Optional[palaestrai.types.Space] = None,
        uid: Optional[str] = None,
        reward_value: Optional[Union[int, float, np.ndarray]] = None,
        observation_space: Optional[palaestrai.types.Space] = None,
        reward_id: Optional[str] = None,
    ):

        self._uid = uid if uid is not None else reward_id
        self._value = value if value is not None else reward_value
        self._space = space if space is not None else observation_space

        assert self._uid is not None, "Must give RewardInformation.uid"
        assert self._space is not None

        assert_value_in_space(self._space, self._value, uid=self.uid)

    def __call__(self):
        """Reads the reward."""
        return self.value

    def __add__(self, other):
        return self.value + other

    def __repr__(self):
        return (
            "RewardInformation("
            f"value={self.value}, space={self.space}, uid={self.uid})"
        )

    def __eq__(self, other):
        return (
            isinstance(other, RewardInformation)
            and self.uid == other.uid
            and self.value == other.value
            and self.space == other.space
        )

    def __getstate__(self):
        return dict(
            uid=self.uid,
            value=(
                self._value.tolist()
                if isinstance(self._value, np.ndarray)
                else self._value
            ),
            space=self._space.to_string(),
        )

    def __setstate__(self, state):
        self._uid = state["uid"]
        self._space = Space.from_string(state["space"])
        assert self._space is not None
        self._value = (
            np.array(state["value"], dtype=self._space.dtype)
            if isinstance(state["value"], list)
            else state["value"]
        )

    @property
    def value(self):
        check_value_is_none(self._value)
        return self._value

    @value.setter
    def value(self, value):
        assert_value_in_space(self._space, value, uid=self.uid)
        self._value = value

    @property
    def reward_value(self):
        warnings.warn(
            f"reward_value property deprecated in class {self.__class__}. Use "
            f"value instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.value

    @reward_value.setter
    def reward_value(self, value):
        warnings.warn(
            f"reward_value setter deprecated in class {self.__class__}. Use "
            f"value instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.value = value

    @property
    def reward_id(self):
        warnings.warn(
            f"reward_id property deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.uid

    @reward_id.setter
    def reward_id(self, uid):
        warnings.warn(
            f"reward_id setter deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.uid = uid

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        assert space is not None
        assert_value_in_space(space, self.value, uid=self.uid)
        self._space = space

    @property
    def observation_space(self):
        warnings.warn(
            f"observation_space property deprecated in class {self.__class__}. Use "
            f"space instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.space

    @observation_space.setter
    def observation_space(self, space: palaestrai.types.Space):
        warnings.warn(
            f"observation_space setter deprecated in class {self.__class__}. Use "
            f"space instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.space = space
