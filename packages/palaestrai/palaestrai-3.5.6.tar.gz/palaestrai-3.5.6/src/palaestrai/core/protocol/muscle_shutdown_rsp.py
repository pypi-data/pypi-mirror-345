from __future__ import annotations
from dataclasses import dataclass

# from typing import TYPE_CHECKING


@dataclass
class MuscleShutdownResponse:
    """Indicates that a :class:`Brain` has released the :class:`Muscle`.

    Sender: :class:`Leaner`
    Receiver: :class:`RolloutWorker`

    Parameters
    ----------
    sender_brain_id : str
        The :class:`Brain` that acknowledges the :class:`Muscle` shutdown
    receiver_muscle_id : str
        The :class:`Muscle` that may now shut down.
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        ID of the :class:`~ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    """

    sender_brain_id: str
    receiver_muscle_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int

    @property
    def sender(self):
        return self.sender_brain_id

    @property
    def receiver(self):
        return self.receiver_muscle_id
