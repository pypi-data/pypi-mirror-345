from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Optional, Union, Any

import numpy as np

from palaestrai.agent.util.space_value_utils import (
    assert_value_in_space,
    check_value_is_none,
)
from palaestrai.types import Space
from palaestrai.util.exception import OutOfActionSpaceError

if TYPE_CHECKING:
    import palaestrai.types

LOG = logging.getLogger(__name__)


class ActuatorInformation:
    """
    Stores information about a single actuator.

    The actuator information class is used to transfer actuator
    information. It can be called to set a new value (value):

    .. code-block::

        a = Actuator(some_space)
        a(42)  # a.value is now 42

    Parameters
    ----------
    value : any, optional
        The set value for this actuator. The type is defined by the
        :attr:`space`. Can be skipped and set afterwards.
    space : :class:`palaestrai.types.Space`
        An instance of a palaestrai space that defines the type of
        the :attr:`value`.
    uid : int or str, optional
        A unique identifier for this actuator. The agents use this ID
        only to assign the value_ids to the correct actuator. The ID
        is not analyzed to gain domain knowledge.
    value_ids: list of str or int or None (default: None) if the actuator
        has multiple value_ids, the value_ids can be used to identify the
        value_ids, e.g., the ids can be the names of the value_ids. This should
        be used if value is a list or a numpy array.
    setpoint : int or str, optional
        *Deprecated* in favor of value
    action_space : :class:`palaestrai.types.Space`
        *Deprecated* in favor of space
    actuator_id : int or str, optional
        *Deprecated* in favor of uid
    """

    def __init__(
        self,
        value: Optional[Union[int, float, np.ndarray]] = None,
        space: Optional[Space] = None,
        uid: Optional[str] = None,
        value_ids=None,
        setpoint=None,
        action_space: Optional[Space] = None,
        actuator_id=None,
    ):
        self._uid = uid if uid is not None else actuator_id
        self._value = value if value is not None else setpoint
        self._space = space if space is not None else action_space
        self.value_ids = value_ids

        assert self._uid is not None, "Must give ActuatorInformation.uid"
        assert self._space is not None

        ActuatorInformation._assert_value_in_space(
            self._space, self._value, uid=self.uid
        )

    @property
    def value_ids(self):
        return self._value_ids

    @value_ids.setter
    def value_ids(self, value):
        self._value_ids = value

    @property
    def setpoint(self):
        warnings.warn(
            f"setpoint property deprecated in class {self.__class__}. Use "
            f"value instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.value

    @setpoint.setter
    def setpoint(self, setpoint):
        warnings.warn(
            f"setpoint property deprecated in class {self.__class__}. Use "
            f"value instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.value = setpoint

    @property
    def value(self):
        check_value_is_none(self._value)
        return self._value

    @value.setter
    def value(self, value):
        ActuatorInformation._assert_value_in_space(
            self._space, value, uid=self.uid
        )
        self._value = value

    def __call__(self, setpoint):
        self.value = setpoint

    def __repr__(self):
        return "ActuatorInformation(" "value=%s, space=%s, uid=%s)" % (
            self.value,
            repr(self.space),
            self.uid,
        )

    def __len__(self):
        """The number of values in the space."""
        return len(self.space)

    def __eq__(self, other):
        return (
            isinstance(other, ActuatorInformation)
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

    def __setstate__(self, state):
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
    def space(self) -> Space:
        assert self._space is not None
        return self._space

    @space.setter
    def space(self, space: Space):
        assert space is not None
        ActuatorInformation._assert_value_in_space(
            space, self._value, uid=self.uid
        )
        self._space = space

    @property
    def action_space(self):
        warnings.warn(
            f"action_space property deprecated in class {self.__class__}. Use "
            f"space instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.space

    @action_space.setter
    def action_space(self, space: Space):
        warnings.warn(
            f"action_space setter deprecated in class {self.__class__}. Use "
            f"space instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.space = space

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
            f"id property deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.uid = value

    @property
    def actuator_id(self):
        warnings.warn(
            f"actuator_id property deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.uid

    @actuator_id.setter
    def actuator_id(self, value):
        warnings.warn(
            f"actuator_id property deprecated in class {self.__class__}. Use "
            f"uid instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.uid = value

    @property
    def uid(self) -> str:
        return self._uid

    @uid.setter
    def uid(self, value: str):
        self._uid = value

    @staticmethod
    def _assert_value_in_space(space: Space, value: Any, uid: str):
        assert_value_in_space(
            space,
            value,
            OutOfActionSpaceError(
                f'Value "{value}" not contained in space "{space}", '
                f"for uid: {uid}"
            ),
        )
