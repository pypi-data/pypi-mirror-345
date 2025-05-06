import unittest
from copy import deepcopy
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from palaestrai.agent import (
    SensorInformation,
    ActuatorInformation,
    RewardInformation,
)
from palaestrai.core.protocol import (
    EnvironmentShutdownRequest,
    EnvironmentShutdownResponse,
    EnvironmentStartRequest,
    EnvironmentStartResponse,
    EnvironmentUpdateRequest,
    EnvironmentUpdateResponse,
    EnvironmentResetRequest,
    EnvironmentResetResponse,
)
from palaestrai.environment import (
    EnvironmentState,
    EnvironmentStateTransformer,
)
from palaestrai.environment.dummy_environment import DummyEnvironment
from palaestrai.types import Discrete


class FourtyTwoStateTransformer(EnvironmentStateTransformer):
    def __init__(self):
        super().__init__()
        self.call_count = 0

    def __call__(
        self, environment_state: EnvironmentState
    ) -> EnvironmentState:
        self.call_count += 1
        environment_state.world_state = 42
        return environment_state


class TestEnvironment(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.env = DummyEnvironment(
            uid=str(uuid4()),
            broker_uri="test://connection",
            seed=123,
            discrete=False,
        )
        self.env._name = "Dummy"

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentStartRequest(
                        sender_simulation_controller="sc-0",
                        receiver_environment="0",
                        experiment_run_id="1",
                        experiment_run_instance_id="inst-0",
                        experiment_run_phase=0,
                    )
                ]
            )
        ),
    )
    async def test_handle_setup(self, start_req):
        self.env.start_environment = MagicMock(
            return_value=(
                [SensorInformation(0, Discrete(1), "0")],
                [ActuatorInformation(0, Discrete(1), "0")],
            )
        )
        rsp = await self.env._handle_setup(start_req)

        self.env.start_environment.assert_called_once()
        self.assertIsInstance(rsp, EnvironmentStartResponse)
        self.assertTrue(all(self.env.name in x.uid for x in rsp.sensors))
        self.assertTrue(all(self.env.name in x.uid for x in rsp.actuators))

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentUpdateRequest(
                        experiment_run_instance_id="HelloFooBar",
                        experiment_run_phase=47,
                        sender_simulation_controller="2",
                        receiver_environment="0",
                        experiment_run_id="1",
                        actuators=list(),
                    )
                ]
            )
        ),
    )
    async def test_handle_update(self, update_req):
        self.env.update = MagicMock(
            return_value=(
                [SensorInformation(0, Discrete(1), "0")],
                [RewardInformation(0, Discrete(1), "0")],
                False,
                None,
            )
        )
        rsp = await self.env._handle_update(update_req)

        self.env.update.assert_called_once()
        self.assertIsInstance(rsp, EnvironmentUpdateResponse)
        self.assertTrue(all(self.env.name in x.uid for x in rsp.sensors))

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentShutdownRequest(
                        sender="2",
                        receiver="0",
                        experiment_run_id="1",
                    )
                ]
            )
        ),
    )
    async def test_handle_shutdown(self, shutdown_req):
        rsp = await self.env._handle_shutdown(shutdown_req)

        self.assertIsInstance(rsp, EnvironmentShutdownResponse)

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[MagicMock(spec=EnvironmentResetRequest)]
            )
        ),
    )
    async def test_handle_reset(self, reset_req):
        self.env.start_environment = MagicMock(
            return_value=(
                [SensorInformation(0, Discrete(1), "0")],
                [ActuatorInformation(0, Discrete(1), "0")],
            )
        )
        result = await self.env._handle_reset(reset_req)

        self.assertIsInstance(result, EnvironmentResetResponse)
        self.assertTrue(all(self.env.name in x.uid for x in result.sensors))
        self.assertTrue(all(self.env.name in x.uid for x in result.actuators))

        self.env.start_environment.assert_called_once()

    async def test_remove_uuid(self):
        actuator1 = ActuatorInformation(
            1, Discrete(5), "Test1.Power.dontcare1"
        )
        actuator2 = ActuatorInformation(
            2, Discrete(5), "Test1.Power.dontcare2"
        )
        a_list = [actuator1, actuator2]
        self.env._name = "Test1"
        self.env._remove_uid(a_list)

        self.assertEqual(a_list[0].uid, "Power.dontcare1")
        self.assertEqual(a_list[1].uid, "Power.dontcare2")

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentUpdateRequest(
                        experiment_run_instance_id="HelloFooBar",
                        experiment_run_phase=47,
                        sender_simulation_controller="2",
                        receiver_environment="0",
                        experiment_run_id="1",
                        actuators=list(),
                    )
                ]
            )
        ),
    )
    async def test_state_transformer(self, update_req):
        env = deepcopy(self.env)
        env._state_transformer = FourtyTwoStateTransformer()
        response = await env._handle_update(update_req)
        self.assertEqual(env._state_transformer.call_count, 1)
        self.assertEqual(response.world_state, 42)

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentStartRequest(
                        sender_simulation_controller="sc-0",
                        receiver_environment="0",
                        experiment_run_id="1",
                        experiment_run_instance_id="inst-0",
                        experiment_run_phase=0,
                    ),
                    EnvironmentUpdateRequest(
                        experiment_run_instance_id="HelloFooBar",
                        experiment_run_phase=47,
                        sender_simulation_controller="2",
                        receiver_environment="0",
                        experiment_run_id="1",
                        actuators=list(),
                    ),
                    EnvironmentUpdateRequest(
                        experiment_run_instance_id="HelloFooBar",
                        experiment_run_phase=47,
                        sender_simulation_controller="2",
                        receiver_environment="0",
                        experiment_run_id="1",
                        actuators=list(),
                    ),
                    EnvironmentUpdateRequest(
                        experiment_run_instance_id="HelloFooBar",
                        experiment_run_phase=47,
                        sender_simulation_controller="2",
                        receiver_environment="0",
                        experiment_run_id="1",
                        actuators=list(),
                    ),
                    EnvironmentShutdownRequest(
                        sender="2",
                        receiver="0",
                        experiment_run_id="1",
                    ),
                ]
            )
        ),
    )
    async def test_run(self, mock_worker):
        self.env.start_environment = MagicMock(return_value=(list(), list()))
        self.env.update = MagicMock(return_value=(list(), list(), False))
        await self.env.run()

        self.assertEqual(self.env.__esm__._mdp_worker.transceive.call_count, 6)
        self.env.start_environment.assert_called_once()
        self.assertEqual(self.env.update.call_count, 3)


if __name__ == "__main__":
    unittest.main()
