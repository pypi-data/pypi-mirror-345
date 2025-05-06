from __future__ import annotations
from typing import Optional

from dataclasses import dataclass

import warnings


@dataclass
class ShutdownRequest:
    """Requests a component to shut down.

    The ::`~ShutdownRequest` message can be exchanged between any two
    components. The sender asks the receiver to shut down completely.
    If the receiver runs alone in a separate process, then the process should
    exit, too.

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
    """

    sender: str
    receiver: str
    experiment_run_id: Optional[str] = None
    experiment_run_instance_id: Optional[str] = None
    experiment_run_phase: Optional[int] = None

    @property
    def run_id(self) -> Optional[str]:
        """Deprecated: Use experiment_run_id instead."""
        warnings.warn(
            f"Run_id property deprecated in class {self.__class__}. "
            f"Use experiment_run_id instead."
        )
        return self.experiment_run_id

    @run_id.setter
    def run_id(self, value: str):
        """Deprecated: Use experiment_run_id instead."""
        warnings.warn(
            f"Run_id property deprecated in class {self.__class__}. "
            f"Use experiment_run_id instead."
        )
        self.experiment_run_id = value

    def __eq__(self, other):
        if (
            type(other) is type(self)
            and other.experiment_run_id == self.experiment_run_id
        ):
            return True
        return False
