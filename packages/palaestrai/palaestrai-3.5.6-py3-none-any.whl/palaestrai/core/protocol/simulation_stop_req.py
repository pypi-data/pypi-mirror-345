from __future__ import annotations
from .shutdown_req import ShutdownRequest


class SimulationShutdownRequest(ShutdownRequest):
    """Signals a :class:`~SimulationController` to shut down.

    * Sender: :class:`~RunGovernor`
    * Receiver :class:`~SimulationController`

    This is a specialized variant of the :class:`~ShutdownRequest`.
    """
