from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Any, Tuple

from abc import ABC
from palaestrai.types import SimulationFlowControl

if TYPE_CHECKING:
    import palaestrai.environment
    from palaestrai.agent import Brain
    from palaestrai.experiment import RunGovernor
    from palaestrai.environment import Environment
    from palaestrai.core.protocol import (
        SimulationControllerTerminationRequest,
        MuscleUpdateRequest,
    )


class TerminationCondition(ABC):
    """Control execution flow of simulations.

    Termination conditions control the flow of the simulation execution. For
    every ::`palaestrai.envrionment.Environment` update
    and every ::`palaestrai.agent.Brain` update,
    the configured termination conditions are queried.
    They then return a flow control indicator (::`SimulationFlowControl`).

    This base class offers default implementations for two situations:

    * ::`TerminationCondition.brain_flow_control`
      is called after an agent's ::`Brain` has received a ::`Muscle` update
      and had time to think about it.
    * ::`TerminationCondition.environment_flow_control`
      is called after an environment update.

    The ::`SimulationFlowControl` enum defines a number of constants. They are
    ordered, i.e., ::`SimulationFlowControl.CONTINUE` has the lowest priority,
    whereas ::`SimulationFlowControl.STOP` has the highest. The indicator
    with the highest priority wins overall, i.e., if one agent indicates that
    the simulation should stop, then it will terminate the current experiment
    run phase.
    """

    def brain_flow_control(
        self, brain: Brain, message: MuscleUpdateRequest
    ) -> Tuple[SimulationFlowControl, Any]:
        """Allows a learning process to control the simulation flow.

        A learner can control the simulation, e.g., by indicating that the
        simulation should be reset or can end when it has become good enough.
        Descendant classes can reimplement this method. They will receive
        access to the respective agent's ::`Brain`, which contains all the
        necessary information (e.g., its memory, training success, etc.)

        Parameters
        ----------

        brain : ::`Brain`
            The ::`Brain` of the current agent, which can be used to query
            information about the agent's current performance.
        message : ::`MuscleUpdateRequest`
            The message that triggered evaluation of the termination
            condition, which can be used, e.g., to retrieve the UID of the
            current rollout worker.

        Returns
        -------
        Tuple of ::`SimulationFlowControl` and Any:
            An indicator for simulation control: The flow control indicator
            with the highest priority (i.e., highest value number in the
            enum) wins.
            The second element of the tuple this method returns indicates
            additional data to pass. This can be useful to, e.g., make
            data available from the ::`.brain_flow_control` method to the
            ::`.phase_flow_control` method.
        """
        return SimulationFlowControl.CONTINUE, None

    def environment_flow_control(
        self, environment: palaestrai.environment.Environment
    ) -> Tuple[SimulationFlowControl, Any]:
        """Allows an environment to control the simulation flow.

        The logic is the same as for ::`.brain_flow_control`, except that an
        environment is now checked.
        The default implementation is to reset the run when the environment is
        done (::`palaestrai.environment.Environment.done`).

        Returns
        -------
        Tuple of ::`SimulationFlowControl` and Any:
            Same logic as for the ::`.brain_flow_control` method
        """
        return (
            SimulationFlowControl.RESTART
            if environment.done
            else SimulationFlowControl.CONTINUE
        ), None

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: SimulationControllerTerminationRequest,
    ) -> Tuple[SimulationFlowControl, Any]:
        """Allows overall control of a simulation phase via the ::`RunGovernor`

        The logic is similar to the of ::`.brain_flow_control`, with the
        exception that this function is called in the ::`RunGovernor`.

        Returns
        -------
        Tuple of ::`SimulationFlowControl` and Any:
            Same logic as for the ::`.brain_flow_control` method
        """
        return SimulationFlowControl.CONTINUE, None

    def check_termination(self, message, component=None):
        return False
