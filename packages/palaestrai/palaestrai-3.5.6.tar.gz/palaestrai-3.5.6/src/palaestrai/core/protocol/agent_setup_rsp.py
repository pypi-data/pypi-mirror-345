from dataclasses import dataclass


@dataclass
class AgentSetupResponse:
    """Response to a successful agent setup

    * Sender: :class:`AgentConductor`
    * Receiver: :class:`SimulationController`

    Parameters
    ----------
    sender_agent_conductor : str
        ID of the transmitting :class:`AgentConductor`
    receiver_simulation_controller : str
        ID of the receiving :class:`SimulationController`
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        ID of the ::`ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    rollout_worker_id : str
        Unique ID of the agent we're setting up (e.g., a :class:`Muscle`).
        This UID is *generated* and used only internally (i.e., in the
        major domo broker) to distinguish several :class:`Muscle`s with the
        same name (e.g., for multi-worker setups).
    muscle_name : str
        Name of the :class:`Agent`. This is the user-defined name (UID)
        from the :class:`ExperimentRun` file.
    """

    sender_agent_conductor: str
    receiver_simulation_controller: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    rollout_worker_id: str
    muscle_name: str

    @property
    def sender(self):
        return self.sender_agent_conductor

    @property
    def receiver(self):
        return self.receiver_simulation_controller
