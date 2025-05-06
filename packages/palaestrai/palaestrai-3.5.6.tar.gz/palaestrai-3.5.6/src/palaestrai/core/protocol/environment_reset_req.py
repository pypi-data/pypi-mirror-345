from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EnvironmentResetRequest:
    """Requests a reset of an :class:`.Environment`.

    Parameters
    ----------
    sender_simulation_controller_id: str
        ID of the sending :class:`.SimulationController`.
    receiver_environment_id: str
        ID of the receiving :class:`.Environment`.
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        Instance ID of the ::`ExperimentRun`
    experiment_run_phase : int
        Number of the phase that should be started

    """

    sender_simulation_controller_id: str
    receiver_environment_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int

    @property
    def sender(self):
        return self.sender_simulation_controller_id

    @property
    def receiver(self):
        return self.receiver_environment_id
