from dataclasses import dataclass


@dataclass
class EnvironmentSetupResponse:
    """Signals successful environment setup and delivers environment parameters

    * Sender: :class:`EnvironmentConductor`
    * Receiver: :class:`SimulationController`

    Parameters
    ----------
    sender_environment_conductor : str
        ID of the sending :class:`EnvironmentConductor`
    receiver_simulation_controller: str
        ID of the receiving :class:`SimulationController`
    experiment_run_id : str
        ID of the ::`ExperimentRun` whose next phase should be executed
    experiment_run_instance_id : str
        Instance ID of the ::`ExperimentRun`
    experiment_run_phase : int
        Number of the phase that should be started
    environment_id : str
        Internal UID of the newly setup environment. This is the unique,
        auto-gnerated ID this ::`Environment` instance is addressed
        over the major domo broker.
    environment_name : str
        The user-visible name of the newly setup environment as it the user
        has assigned it in the experiment run file. (This field is named
        ``uid`` in the experiment run file.)
    environment_type : str
        Type (i.e., class string) of the environment
    environment_parameters: dict
        All parameters that describe the environment that has just been set up
    """

    sender_environment_conductor: str
    receiver_simulation_controller: str
    environment_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    environment_name: str
    environment_type: str
    environment_parameters: dict

    @property
    def sender(self):
        return self.sender_environment_conductor

    @property
    def receiver(self):
        return self.receiver_simulation_controller
