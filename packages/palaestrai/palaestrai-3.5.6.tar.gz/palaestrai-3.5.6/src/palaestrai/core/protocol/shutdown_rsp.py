from __future__ import annotations
from typing import Optional

import warnings
from dataclasses import dataclass


@dataclass
class ShutdownResponse:
    """Responds to a :class:`~ShutdownRequest`

    The message should be sent as last thing before the component shuts down.
    I.e., cleanups should already have taken place.

    * Sender: Any component
    * Receiver: Any component

    Attributes
    ----------
    sender : str
        The opaque unique ID of the sending component
    receiver : str
        The opaque unique ID of the receiving component
    experiment_run_id : Optional[str] = None
        ID of the current experiment run, if any. Should be given, if possible.
    experiment_run_instance_id : Optional[str] = None
        ID of the current experiment run instance, if any. Should be given,
        if possible.
    experiment_run_phase : Optional[int] = None
        Current phase number. Should be given, if possible.
    def __init__(self, experiment_run_id):
        self._experiment_run_id = experiment_run_id
    """

    sender: str
    receiver: str
    experiment_run_id: Optional[str] = None
    experiment_run_instance_id: Optional[str] = None
    experiment_run_phase: Optional[int] = None

    @property
    def run_id(self):
        """Deprecated: Use experiment_run_id instead."""
        warnings.warn(
            f"Run_id property deprecated in class {self.__class__}. "
            f"Use experiment_run_id instead.",
            DeprecationWarning,
        )
        return self.experiment_run_id

    @run_id.setter
    def run_id(self, value):
        """Deprecated: Use experiment_run_id instead."""
        warnings.warn(
            f"Run_id property deprecated in class {self.__class__}. "
            f"Use experiment_run_id instead.",
            DeprecationWarning,
        )
        self.experiment_run_id(value)

    def __eq__(self, other):
        if (
            type(other) is type(self)
            and other.experiment_run_id == self.experiment_run_id
        ):
            return True
        return False
