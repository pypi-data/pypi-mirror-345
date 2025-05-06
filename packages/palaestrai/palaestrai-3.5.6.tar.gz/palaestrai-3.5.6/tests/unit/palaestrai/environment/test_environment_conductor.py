import copy
import unittest
from unittest.mock import MagicMock, PropertyMock, call, patch
from uuid import uuid4

import time

from palaestrai.core import BasicState
from palaestrai.core.protocol import (
    EnvironmentSetupRequest,
    EnvironmentSetupResponse,
    ShutdownRequest,
    ShutdownResponse,
)
from palaestrai.environment.environment_conductor import EnvironmentConductor


class _MockEnv:
    async def run(self):
        time.sleep(0.1)
        exit(0)


class _MockDyingProcess:
    def __init__(self):
        self.uid = "Aaaah-23adf1"
        self.name = "The Dreaded Castle of Aaaaaaaaah"

    async def run(self):
        exit(23)


class TestEnvironmentConductor(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.addCleanup(patch.stopall)
        self.env_cond = EnvironmentConductor(
            {
                "environment": {
                    "name": (
                        "palaestrai.environment.dummy_environment:"
                        "DummyEnvironment"
                    ),
                    "uid": "0815",
                    "params": {"discrete": False},
                },
            },
            123,
            uuid4(),
        )

    @patch("aiomultiprocess.core.Process.start")
    async def test_spawn_worker(self, aioproc):
        msg_setup = EnvironmentSetupRequest(
            experiment_run_id="run away",
            experiment_run_instance_id="run away instance",
            experiment_run_phase=47,
            receiver_environment_conductor_id="the boss",
            sender_simulation_controller_id="the servant",
        )

        self.assertEqual(self.env_cond._environment_processes, {})
        self.env_cond.handle_environment_setup_request(msg_setup)
        self.assertNotEqual(self.env_cond._environment_processes, {})
        self.assertEqual(
            len(list(self.env_cond._environment_processes.values())), 1
        )
        self.env_cond.handle_environment_setup_request(msg_setup)
        self.assertEqual(
            len(list(self.env_cond._environment_processes.values())), 2
        )
        self.assertEqual(aioproc.call_count, 2)

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentSetupRequest(
                        experiment_run_id="run away",
                        experiment_run_instance_id="run away instance",
                        experiment_run_phase=47,
                        receiver_environment_conductor_id="the boss",
                        sender_simulation_controller_id="the servant",
                    ),
                    ShutdownRequest(
                        sender="the boss",
                        receiver="the servant",
                        experiment_run_id="run away",
                    ),
                    None,
                ]
            )
        ),
    )
    async def test_run_shutdown(self, _):
        self.env_cond._environment = MagicMock(uid="0815")
        self.env_cond._load_environment = MagicMock()
        self.env_cond._init_environment = MagicMock()
        await self.env_cond.run()
        self.assertEqual(self.env_cond._state, BasicState.FINISHED)

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentSetupRequest(
                        experiment_run_id="run away",
                        experiment_run_instance_id="run away instance",
                        experiment_run_phase=47,
                        receiver_environment_conductor_id="the servant",
                        sender_simulation_controller_id="the boss",
                    ),
                    EnvironmentSetupRequest(
                        experiment_run_id="run away",
                        experiment_run_instance_id="run away instance",
                        experiment_run_phase=47,
                        receiver_environment_conductor_id="the servant",
                        sender_simulation_controller_id="the boss",
                    ),
                    ShutdownRequest(
                        sender="the boss",
                        receiver="the servant",
                        experiment_run_id="run away",
                    ),
                    None,
                ]
            )
        ),
    )
    async def test_setup_conductor(self, mock_worker):
        self.env_cond._uid = "the servant"
        msg_setup_response = EnvironmentSetupResponse(
            sender_environment_conductor=self.env_cond.uid,
            receiver_simulation_controller="the boss",
            environment_id="0815",
            experiment_run_id="run away",
            experiment_run_instance_id="run away instance",
            experiment_run_phase=47,
            environment_type=self.env_cond._environment_configuration[
                "environment"
            ]["name"],
            environment_parameters=self.env_cond._environment_configuration[
                "environment"
            ]["params"],
            environment_name="Gaia",
        )
        msg_setup_response2 = copy.deepcopy(msg_setup_response)
        msg_setup_response2.environment_id = "0816"
        msg_shutdown_response = ShutdownResponse(
            sender=self.env_cond.uid,
            receiver="the boss",
            experiment_run_id="run away",
        )

        calls = (
            call(None, skip_recv=False),
            call(msg_setup_response, skip_recv=False),
            call(msg_setup_response2, skip_recv=False),
            call(msg_shutdown_response, skip_recv=True),
        )
        env_mock1 = MagicMock()
        env_mock1.uid = "0815"
        env_mock1.name = "Gaia"
        env_mock2 = MagicMock()
        env_mock2.uid = "0816"
        env_mock2.name = "Gaia"
        self.env_cond._load_environment = MagicMock(
            side_effect=[env_mock1, env_mock2]
        )
        self.env_cond._init_environment = MagicMock()
        await self.env_cond.run()
        self.env_cond.__esm__._mdp_worker.transceive.assert_has_awaits(calls)

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    EnvironmentSetupRequest(
                        experiment_run_id="run away",
                        experiment_run_instance_id="run away instance",
                        experiment_run_phase=47,
                        receiver_environment_conductor_id="the boss",
                        sender_simulation_controller_id="the servant",
                    ),
                    None,
                ]
            )
        ),
    )
    async def test_dying_environment_process(self, _):
        self.env_cond._load_environment = MagicMock(
            return_value=_MockDyingProcess()
        )
        with self.assertRaises(RuntimeError) as cm:
            await self.env_cond.run()
        self.assertEqual(self.env_cond._state, BasicState.ERROR)


if __name__ == "__main__":
    unittest.main()
