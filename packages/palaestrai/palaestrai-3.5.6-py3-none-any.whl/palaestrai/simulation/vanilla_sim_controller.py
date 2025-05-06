from __future__ import annotations
from typing import Tuple

import logging
import itertools

from palaestrai.types import SimulationFlowControl
from .simulation_controller import SimulationController

LOG = logging.getLogger(__name__)


class VanillaSimController(SimulationController):
    """Scatter-gather simulation controller for agents

    This simulation controller implements an execution strategy in which agents
    act in parallel.
    """

    async def advance(self):
        rsp = await self.act(self.agents)
        _ = await self.step(
            self.agents,
            [
                a
                for a in itertools.chain.from_iterable(
                    [r.actuators for r in rsp]
                )
            ],
        )
