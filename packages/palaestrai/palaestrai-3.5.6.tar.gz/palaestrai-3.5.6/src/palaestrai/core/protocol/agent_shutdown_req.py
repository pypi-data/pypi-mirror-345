from __future__ import annotations
from warnings import warn

from .shutdown_req import ShutdownRequest


class AgentShutdownRequest(ShutdownRequest):
    """Signals an agent (:class:`~Muscle`) to shut down.

    * Sender: A :class:`~SimulationController`
    * Receiver: A :class:`~Muscle`

    This is a specialized variant of the :class:`~ShutdownRequest`.
    """

    @property
    def agent_id(self) -> str:
        warn(
            f"{self.__class__.__name__}.agent_id is deprecated, "
            f"use {self.__class__.__name__}.receiver_agent instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.receiver

    @property
    def complete_shutdown(self) -> bool:
        warn(
            f"{self.__class__.__name__}.agent_id is deprecated is always"
            "returns False. There is a separate ShutdownRequest for the "
            "conductors, please use that instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return False

    @complete_shutdown.setter
    def complete_shutdown(self, complete_shutdown: bool):
        warn(
            f"{self.__class__.__name__}.agent_id is deprecated is always"
            "returns False. There is a separate ShutdownRequest for the "
            "conductors, please use that instead.",
            DeprecationWarning,
            stacklevel=2,
        )
