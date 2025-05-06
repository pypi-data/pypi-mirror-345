from .shutdown_req import ShutdownRequest


class EnvironmentShutdownRequest(ShutdownRequest):
    """Signals an environment to shut down.

    * Sender: A :class:`~SimulationController`
    * Receiver: :class:`~Environment`

    This is a variant of the :class:`~ShutdownRequest`.
    """

    @property
    def environment_id(self) -> str:
        return self.receiver
