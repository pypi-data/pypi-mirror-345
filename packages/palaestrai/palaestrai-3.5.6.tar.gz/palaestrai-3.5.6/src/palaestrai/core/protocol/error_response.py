from __future__ import annotations
from typing import Optional, Any

from dataclasses import dataclass


@dataclass
class ErrorIndicator:
    """Indiciates an error as alternative response to a request

    Usually, requests have responses, and clients send out requests to workers.
    However, things can go wrong; for this case, this message type exists.
    It holds an error message and/or an exception.

    This message class can be subclassed in order to make live for the
    :class:`~EventStateMachine` easier, because ``@ESM.on`` works on
    dedicated classes to discriminate different errors from each other.

    Attributes
    ----------
    sender : str
        An object than encountered an error that prohibits it from
        continuing
    receiver : str
        The (parent) receiving service that should handle the error
    error_message : Optional[str]
        An error message, e.g. for displaying it to the end user
    exception : Any
        An exception object that should be transferred to the receiver
    """

    sender: str
    receiver: str
    error_message: Optional[str]
    exception: Any
