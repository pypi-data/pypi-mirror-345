from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Tuple

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from palaestrai.types import SimulationFlowControl


@dataclass
class MuscleUpdateResponse:
    """Result of a :class:`Brain`'s working

    * Sender: :class:`Learner`
    * Receiver: :class:`RolloutWorker`

    Upon receiving the corresponding :class:`MuscleUpdateRequest` message,
    the :class:`Leaner` will query its :class:`Brain` for new parameters for
    the particular :class:`Muscle`.
    What is sent depends on the algorithm.

    Parameters
    ----------

    sender_brain_id : str
        The brain the update comes from
    receiver_muscle_id : str
        The :class:`Muscle` that potentially receives an update
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        ID of the :class:`~ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    flow_control_indicator : ::`SimulationFlowControl`
        Flow control indicator from a termination conditions that examines
        the ::`Brain`. Transmits only the highest-priority indicator signal.
    flow_control_data : Dict of str mapping to Tuple SimulationFlowControl, Any
        Complete flow control data: The dictionary's keys are the class names
        of the respective ::`TerminationCondition` classes,
        the values are the tuples as returned by the
        ::`TerminationCondition.brain_flow_control` method.
    update : Any
        Whatever a :class:`Brain` wants to send to a :class:`Muscle`. This can
        be ``None``, in which case there is no update. However, since the
        major domo protocol's request-response pattern requires a response to
        *any* request, empty updates must be sent.
    statistics : Dict, default: ``{}``
        Any statistics that the Brain wants to see stored for later analysis
    """

    sender_brain_id: str
    receiver_muscle_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    flow_control_indicator: SimulationFlowControl
    flow_control_data: Dict[str, Tuple[SimulationFlowControl, Any]] = field(
        default_factory=dict
    )
    update: Any = None
    statistics: Dict = field(default_factory=dict)

    @property
    def sender(self):
        return self.sender_brain_id

    @property
    def receiver(self):
        return self.receiver_muscle_id

    def has_update(self):
        return self.update is not None
