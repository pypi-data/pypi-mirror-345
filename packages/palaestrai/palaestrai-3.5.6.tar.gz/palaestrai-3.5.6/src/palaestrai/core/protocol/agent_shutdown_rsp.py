from __future__ import annotations

import warnings

from .shutdown_rsp import ShutdownResponse


class AgentShutdownResponse(ShutdownResponse):
    """Signals that an :class:`~Muscle` has shut down.

    * Sender: :class:`~Muscle` (an agent)
    * Receiver: :class:`~SimulationController`

    This is a specialized variant of the :class:`~ShutdownResponse`.
    """

    @property
    def agent_id(self):
        return self.sender
