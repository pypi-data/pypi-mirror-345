from __future__ import annotations

import logging
from palaestrai.core import BasicState
from .simulation_controller import SimulationController, FlowControlChange

LOG = logging.getLogger(__name__)


class TakingTurnsSimulationController(SimulationController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def simulate(self):
        """Main simulation task

        This method is usually scheduled as a task at the end of the simulation
        setup phase. It can be overwritten by descendant classes to excert
        complete control over the simulation.
        """
        agents = list(self._agents.values())  # Needed to preserve order
        ai = 0  # Index of current agent
        env_terminates = False

        while self.is_running:
            # With the index ai, we iterate over agents in the order in which
            # they were loaded, which, in turn, is given by the order in
            # which comes from the ExperimentRun object.
            # The index ai wraps (see the end of the loop).
            # Python's dict is guaranteed to remember the order in which items
            # were added to it (since Python version 3.7).

            agent = agents[ai]
            try:
                response = (await self.act([agent]))[0]
                env_updates = await self.step([agent], response.actuators)
            except FlowControlChange:
                self._state = BasicState.STOPPING
                break
            ai = (ai + 1) % len(agents)
        LOG.debug(
            "The simulation has ended, updating agents one last time.",
        )
        # Notify agents of our terminal state. We can potentially parallelize
        # here, as order is no longer important: Each agent gets the same
        # final state, no actions are applied anymore.
        try:
            _ = await self.act(agents, done=True)
        except FlowControlChange:
            pass  # Not relevant here anymore.
        self.flow_control()
