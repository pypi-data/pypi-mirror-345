from __future__ import annotations
from .shutdown_rsp import ShutdownResponse


class EnvironmentShutdownResponse(ShutdownResponse):
    """Indicates that an :class:`~Environment` has shut down.

    Sender: :class:`~Environment`
    Receiver: :class:`~SimulationController`

    This class is a specialization of the :class:`~ShutdownResponse`.
    """

    @property
    def environment_id(self):
        return self.sender
