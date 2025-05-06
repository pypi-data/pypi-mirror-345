import unittest
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call

from palaestrai.core import BasicState
from palaestrai.agent import ActuatorInformation
from palaestrai.core.protocol import (
    AgentUpdateResponse,
)

from palaestrai.types import Mode, SimulationFlowControl, Discrete
from palaestrai.simulation import TakingTurnsSimulationController
from palaestrai.simulation.simulation_controller import FlowControlChange


class TestTakingTurnsSimulationController(IsolatedAsyncioTestCase):
    async def test_simulate(self):
        ttsc = TakingTurnsSimulationController(
            agent_conductor_ids=["AC-1", "AC-2"],
            environment_conductor_ids=["EC-1", "EC-2"],
            agents={},
            mode=Mode.TEST,  # Ha-ha.
            termination_conditions=[{}],
        )
        actuator_infos = [
            ActuatorInformation(uid="AI-1.1", space=Discrete(4711), value=815),
            ActuatorInformation(uid="AI-1.2", space=Discrete(4711), value=815),
            ActuatorInformation(uid="AI-2.1", space=Discrete(4711), value=816),
            ActuatorInformation(uid="AI-2.2", space=Discrete(4711), value=816),
        ]

        ttsc._state = BasicState.RUNNING
        ttsc._agents = {
            "AC-1.RW-1": MagicMock(
                uid="AC-1.RW-1", actuators=actuator_infos[:2]
            ),
            "AC-2.RW-2": MagicMock(
                uid="AC-2.RW-2", actuators=actuator_infos[2:]
            ),
        }
        ttsc.act = AsyncMock(
            side_effect=[
                [
                    AgentUpdateResponse(
                        sender_rollout_worker_id="RW-1",
                        receiver_simulation_controller_id="SC-1",
                        experiment_run_id="run away",
                        experiment_run_phase=42,
                        experiment_run_instance_id="Insta-1234",
                        sensor_information=[],
                        actuator_information=actuator_infos[:2],
                        flow_control_indicator=SimulationFlowControl.CONTINUE,
                    ),
                ],
                [
                    AgentUpdateResponse(
                        sender_rollout_worker_id="RW-2",
                        receiver_simulation_controller_id="SC-1",
                        experiment_run_id="run away",
                        experiment_run_phase=42,
                        experiment_run_instance_id="Insta-1234",
                        sensor_information=[],
                        actuator_information=actuator_infos[2:],
                        flow_control_indicator=SimulationFlowControl.CONTINUE,
                    ),
                ],
                [],
            ]
        )
        ttsc.step = AsyncMock(
            side_effect=[MagicMock(), FlowControlChange(None)]
        )
        ttsc.flow_control = MagicMock()

        await ttsc.simulate()

        ttsc.flow_control.assert_called()
        ttsc.act.assert_has_awaits(
            [
                call([ttsc.agents[0]]),
                call([ttsc.agents[1]]),
                call([ttsc.agents[0], ttsc.agents[1]], done=True),
            ]
        )
        ttsc.step.assert_has_awaits(
            [
                call([ttsc.agents[0]], actuator_infos[:2]),
                call([ttsc.agents[1]], actuator_infos[2:]),
            ]
        )


if __name__ == "__main__":
    unittest.main()
