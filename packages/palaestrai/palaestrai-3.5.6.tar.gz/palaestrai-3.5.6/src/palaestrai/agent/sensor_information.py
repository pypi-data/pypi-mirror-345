"""This module contains the class :class:`SensorInformation` that stores all
information the agents need about a single sensor."""

from __future__ import annotations

import logging
import warnings
from typing import Optional

import numpy as np

from palaestrai.agent.util.space_value_utils import (
    assert_value_in_space,
    check_value_is_none,
)
from palaestrai.types import Space

LOG = logging.getLogger(__name__)


class SensorInformation:
    """
    Stores information about a single sensor.

    Once created, a *SensorInformation* object can be called to
    retrieve its value, e.g.,:

    .. code-block::

        a = SensorInformation(42, some_space)
        a()  # => 42
        a.value  # => 42


    Parameters
    ----------
    value: int float as described in space
        The value of the sensor's last reading. The type of this value
        is described by :attr:`space`
    space: :class:`palaestrai.types.Space`
        An instance of a palaestrai space object defining the type of
        the value
    uid: str or int, optional
        A unique identifier for this sensor. The agents use the ID only
        for assignment of previous value_ids with the same ID. The ID is
        not analyzed to gain domain knowledge (e.g., if the sensor is
        called "Powergrid.Bus1", the agent will not use the ID to
        identify this sensor as part of a Bus in a powergrid.)
    value_ids: list of str or int or None (default: None) if the sensor
        has multiple value_ids, the value_ids can be used to identify the
        value_ids, e.g., the ids can be the names of the value_ids. This should
        be used if value is a list or a numpy array.
    sensor_value: int float as described in space
        *Deprecated* in favor of value
    observation_space : :class:`palaestrai.types.Space`
        *Deprecated* in favor of space
    sensor_id: str or int, optional
        *Deprecated* in favor of uid
    """

    def __init__(
        self,
        value=None,
        space: Optional[Space] = None,
        uid=None,
        value_ids=None,
        sensor_value=None,
        observation_space: Optional[Space] = None,
        sensor_id=None,
    ):

        self._uid = uid if uid is not None else sensor_id
        self._value = value if value is not None else sensor_value
        self._space = space if space is not None else observation_space
        self.value_ids = value_ids

        assert self._uid is not None, "Must give SensorInformation.uid"
        assert self._space is not None

        assert_value_in_space(self._space, self._value, uid=self.uid)

    def __call__(self, **kwargs):
        return self.value

    def __repr__(self):
        return (
            "SensorInformation("
            f"value={self.value}, space={repr(self.space)}, uid={self.uid})"
        )

    def __str__(self):
        return repr(self)

    def __len__(self):
        """The number of values in the space."""
        return len(self.space)

    def __eq__(self, other):
        return (
            isinstance(other, SensorInformation)
            and self.uid == other.uid
            and self.value == other.value
            and self.space == other.space
            and self.value_ids == other.value_ids
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
            value_ids=self._value_ids,
        )

    def __setstate__(self, state: dict):
        self._uid = state["uid"]
        self._space = Space.from_string(state["space"])
        assert self._space is not None
        self._value = (
            np.array(state["value"], dtype=self._space.dtype)
            if isinstance(state["value"], list)
            else state["value"]
        )
        self._value_ids = state["value_ids"]

    @property
    def value(self):
        check_value_is_none(self._value)
        return self._value

    @value.setter
    def value(self, value):
        assert_value_in_space(self._space, value, uid=self.uid)
        self._value = value

    @property
    def sensor_value(self):
        warnings.warn(
            f"sensor_value property deprecated in class {self.__class__}. Use "
            f"value instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.value

    @sensor_value.setter
    def sensor_value(self, value):
        warnings.warn(
            f"sensor_value setter deprecated in class {self.__class__}. Use "
            f"value instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.value = value

    @property
    def id(self):
        warnings.warn(
            f"id property deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.uid

    @id.setter
    def id(self, value):
        warnings.warn(
            f"id setter deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.uid = value

    @property
    def sensor_id(self):
        warnings.warn(
            f"sensor_id property deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.uid

    @sensor_id.setter
    def sensor_id(self, uid):
        warnings.warn(
            f"sensor_id setter deprecated in class {self.__class__}. Use "
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
    def space(self) -> Space:
        assert self._space is not None
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
    def observation_space(self, space: Space):
        warnings.warn(
            f"observation_space setter deprecated in class {self.__class__}. Use "
            f"space instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.space = space

    @property
    def value_ids(self):
        return self._value_ids

    @value_ids.setter
    def value_ids(self, value):
        self._value_ids = value
