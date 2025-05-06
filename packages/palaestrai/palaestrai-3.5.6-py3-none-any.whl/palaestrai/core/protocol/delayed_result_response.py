from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DelayedResultResponse:
    """Notifies the client that a worker task takes longer than expected.

    Some operations can run longer, such as training an agent. In this case,
    in order to avoid hard timeouts and to indicate that worker is still alive,
    this message is returned instead of the actual result.
    Then, the client can request the result again using a
    :class:`DelayedResultRequest` message.

    This implements a form of active polling built on the request-reply
    communication pattern of the MDP.

    Parameters
    ----------
    sender : str
        The name of the sender, usually an MDP worker
    receiver : str
        The name of the receiver, usually an MDP client
    task_uuid : str
        The generated unique ID of the pending task, which can be used later
        on to query the result (cf. :class:`DelayedResultRequest`)
    """

    sender: str
    receiver: str
    task_uuid: str
