from __future__ import annotations
from typing import Any, Iterator

import unittest
from unittest.mock import patch, AsyncMock, Mock

from palaestrai.types import SimulationFlowControl
from palaestrai.experiment import RunGovernor


class AwaitableMock(AsyncMock):
    def __await__(self) -> Iterator[Any]:
        self.await_count += 1
        return iter([])


class TestRunGovernor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.run_governor = RunGovernor(uid="rg")
        self.run_governor.experiment_run = Mock(num_phases=2)

    async def test_experiment_run_start_request(
        self,
    ):
        self.run_governor.current_phase = 42
        self.run_governor._setup_run = AsyncMock()
        self.run_governor._run_all_phases = AsyncMock()
        self.run_governor.experiment_run = None
        await self.run_governor._handle_experiment_run_start_request(Mock())

        self.assertEqual(self.run_governor.current_phase, 0)
        self.assertIsNotNone(self.run_governor.experiment_run)
        self.run_governor._setup_run.assert_awaited()
        self.run_governor._run_all_phases.assert_called()

    async def test_experiment_run_already_exists(self):
        self.run_governor.experiment_run = Mock()
        self.run_governor._setup_run = AsyncMock()
        self.run_governor._run_all_phases = AsyncMock()
        rsp = await self.run_governor._handle_experiment_run_start_request(
            Mock()
        )
        self.assertTrue(rsp.error)

    async def test_setup_run(self):
        await self.run_governor._setup_run()
        self.assertIsNotNone(self.run_governor._termination_condition)

    @patch("aiomultiprocess.core.Process.start")
    async def test_setup_phase(self, mprocess: Mock):
        self.run_governor.experiment_run = Mock(
            environment_conductors=Mock(
                return_value={1: Mock(uid="111111-EC")}
            ),
            agent_conductors=Mock(
                return_value={
                    1: Mock(uid="11111111-AC"),
                    2: Mock(uid="22222222-AC"),
                }
            ),
            simulation_controllers=Mock(
                return_value={
                    1: Mock(uid="11111111-SC"),
                    2: Mock(uid="22222222-SC"),
                    3: Mock(uid="33333333-SC"),
                }
            ),
        )
        self.run_governor.current_phase = Mock()
        self.run_governor.current_episode_counts = Mock()
        await self.run_governor._setup_phase()

        mprocess.assert_called()
        self.assertEqual(mprocess.call_count, 6)
        self.assertEqual(len(self.run_governor._simulation_controllers), 3)
        self.assertEqual(len(self.run_governor._agent_conductors), 2)
        self.assertEqual(len(self.run_governor._environment_conductors), 1)
        self.assertEqual(len(self.run_governor.current_episode_counts), 0)

    @patch(
        "asyncio.get_running_loop",
        return_value=Mock(create_future=Mock(return_value=AwaitableMock())),
    )
    async def test_run_all_phases(self, aiomock):
        self.run_governor._send_simulation_start_requests = Mock()
        self.run_governor._setup_phase = AsyncMock()
        self.run_governor._request_simulation_controllers_shutdown = (
            AsyncMock()
        )
        self.run_governor.stop = Mock()
        await self.run_governor._run_all_phases()
        aiomock.return_value.create_future.assert_called()
        self.assertEqual(aiomock.return_value.create_future.call_count, 6)
        self.assertIsNotNone(self.run_governor._future_next_phase)
        self.run_governor._future_next_phase.assert_awaited()
        self.assertEqual(
            self.run_governor._send_simulation_start_requests.call_count, 2
        )

    async def test_simcontroller_termination_reset(self):
        self.run_governor._termination_condition = Mock(
            phase_flow_control=Mock(
                return_value=(SimulationFlowControl.RESET, None)
            )
        )
        self.run_governor.current_episode_counts = {"id": 0}
        rsp = await self.run_governor._handle_simulation_controller_termination_request(
            Mock(sender="id")
        )
        self.assertTrue(rsp.restart)
        self.assertEqual(self.run_governor.current_episode_counts["id"], 1)

    async def test_simcontroller_termination_next_phase(self):
        self.run_governor._termination_condition = Mock(
            phase_flow_control=Mock(
                return_value=(SimulationFlowControl.STOP_PHASE, None)
            )
        )
        self.run_governor._request_conductors_shutdown = AsyncMock()
        self.run_governor._simulation_controllers_active = {"id"}
        self.run_governor.current_episode_counts = {"id": 0}

        rsp = await self.run_governor._handle_simulation_controller_termination_request(
            Mock(sender="id")
        )
        self.assertTrue(rsp.complete_shutdown)
        self.assertEqual(
            len(self.run_governor._simulation_controllers_active), 0
        )


if __name__ == "__main__":
    unittest.main()
