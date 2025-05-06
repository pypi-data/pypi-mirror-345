from __future__ import annotations
from dataclasses import dataclass

# from typing import TYPE_CHECKING


@dataclass
class MuscleShutdownRequest:
    """Requests a :class:`Brain` to release a :class:`Muscle`.

    * Sender: :class:`RolloutWorker`
    * Receiver: :class:`Learner`

    When a simulation episode ends, the :class:`Muscle`s acting in it are
    shut down. This message informs a :class:`Brain`'s :class:`Learner`
    watchdog that this has happend. The :class:`Learner` is then able to
    clean up, train one last time, etc.

    Parameters
    ----------
    sender_muscle_id : str
        The UID of the :class:`Muscle` that shuts down
    receiver_brain_id : str
        The UID of the :class:`Brain` the :class:`Muscle` belongs to
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        ID of the :class:`~ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    """

    sender_muscle_id: str
    receiver_brain_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int

    @property
    def sender(self):
        return self.sender_muscle_id

    @property
    def receiver(self):
        return self.receiver_brain_id
