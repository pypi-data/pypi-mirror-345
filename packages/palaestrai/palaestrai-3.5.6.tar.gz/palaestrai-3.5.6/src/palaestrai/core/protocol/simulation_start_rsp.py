from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SimulationStartResponse:
    """Confirms that a simulation is started up.

    * Sender: :class:`SimulationController`
    * Receiver: :class:`RunGovernor`
    """

    sender_simulation_controller: str
    receiver_run_governor: str

    @property
    def sender(self):
        return self.sender_simulation_controller

    @property
    def receiver(self):
        return self.receiver_run_governor
