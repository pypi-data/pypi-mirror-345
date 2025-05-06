from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DelayedResultRequest:
    """Polls a worker for a future result that has been delayed.

    When a worker needs longer to finish an operation than the MDP timeout
    would allow, it replies with a :class:`DelayedResultResponse`.
    The client can then ask again whether the operation has finished by
    sending this message.

    This implements a form of active polling built on the request-reply
    communication pattern of the MDP.
    The :class:`EventStateMachine` implements this transparently.

    Parameters
    ----------
    sender : str
        The name of the sender, usually an MDP worker
    receiver : str
        The name of the receiver, usually an MDP client
    task_uuid : str
        The generated unique ID of the pending task: The worker emits this
        ID with a :class:`DelayedResultResponse` message.
    """

    sender: str
    receiver: str
    task_uuid: str
