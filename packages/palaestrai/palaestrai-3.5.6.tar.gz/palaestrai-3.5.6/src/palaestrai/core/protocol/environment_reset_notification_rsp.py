from __future__ import annotations

import warnings
from dataclasses import dataclass


@dataclass
class EnvironmentResetNotificationResponse:
    """Response to an environment reset notification.

    Parameters
    ----------
    sender_muscle_id: str
        ID of the sending :class:`palaestrai.agent.Muscle`.
    receiver_simulation_controller_id: str
        ID of the receiving :class:`.SimulationController`.

    """

    sender_muscle_id: str
    receiver_simulation_controller_id: str

    @property
    def sender(self):
        return self.sender_agent_id

    @property
    def receiver(self):
        return self.receiver_simulation_controller_id

    @property
    def sender_agent_id(self):
        warnings.warn(
            "The 'sender_agent_id' property is deprecated "
            "in favor of 'sender_muscle_id' "
            "(which serves the same purpose).",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.sender_muscle_id
