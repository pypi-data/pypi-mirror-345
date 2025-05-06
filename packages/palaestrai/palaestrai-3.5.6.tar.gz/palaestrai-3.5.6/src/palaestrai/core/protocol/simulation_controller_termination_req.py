from __future__ import annotations
from typing import TYPE_CHECKING, Any, Tuple, Dict

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from palaestrai.types import SimulationFlowControl


@dataclass
class SimulationControllerTerminationRequest:
    """Allows a ::`SimulationController` to announce that an episode has ended.

    * Sender: :py:class:`SimulationController`
    * Receiver: :py:class:`RunGovernor`

    When an episode's simulation control flow changes because of a
    ::`TerminationCondition`, the ::`SimulationController` uses a request
    message of this type to ask its ::`RunGovernor` how to proceed.

    Parameters
    ----------

    sender_simulation_controller_id : str
        Opaque ID of the sending :py:class:`SimulationController` instance
    receiver_run_governor_id : str
        Opaque ID of the receiving :py:class:`RunGovernor` instance
    experiment_run_id : str
        Opaque ID of an experiment run
    flow_control_indicator : ::`SimulationFlowControl`
        Flow control indicator from a termination conditions that examines
        the ::`Brain`. Transmits only the highest-priority indicator signal.
    flow_control_data : Dict of str mapping to Tuple SimulationFlowControl, Any
        Complete flow control data: The dictionary's keys are the class names
        of the respective ::`TerminationCondition` classes,
        the values are the tuples as returned by the
        ::`TerminationCondition.brain_flow_control` method.
    """

    sender_simulation_controller_id: str
    receiver_run_governor_id: str
    experiment_run_id: str
    flow_control_indicator: SimulationFlowControl
    flow_control_data: Dict[str, Tuple[SimulationFlowControl, Any]] = field(
        default_factory=dict
    )

    @property
    def sender(self):
        return self.sender_simulation_controller_id

    @property
    def receiver(self):
        return self.receiver_run_governor_id
