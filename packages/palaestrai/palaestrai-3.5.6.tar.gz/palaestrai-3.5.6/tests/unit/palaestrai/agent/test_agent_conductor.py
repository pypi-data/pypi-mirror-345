import unittest
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from uuid import uuid4
from warnings import catch_warnings

from palaestrai.core import BasicState
from palaestrai.agent.actuator_information import ActuatorInformation
from palaestrai.agent.agent_conductor import AgentConductor
from palaestrai.agent.dummy_brain import DummyBrain
from palaestrai.agent.file_brain_dumper import FileBrainDumper
from palaestrai.agent import Learner
from palaestrai.agent.sensor_information import SensorInformation
from palaestrai.agent.store_brain_dumper import StoreBrainDumper
from palaestrai.core.protocol import (
    AgentSetupRequest,
    AgentSetupResponse,
    ShutdownRequest,
)


class TestAgentConductor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agent_params = {
            "name": "defender",
            "brain": {
                "name": "palaestrai.agent.dummy_brain:DummyBrain",
                "params": {},
            },
            "muscle": {
                "name": "palaestrai.agent.dummy_muscle:DummyMuscle",
                "params": {},
            },
            "objective": {
                "name": "palaestrai.agent.dummy_objective:DummyObjective",
                "params": {"params": 1},
            },
            "sensors": [SensorInformation(0, MagicMock(), "TestSensor-1")],
            "actuators": [
                ActuatorInformation(0, MagicMock(), "TestActuator-1")
            ],
        }

        self.ac = AgentConductor(self.agent_params, 0, "Some AgentConductor")
        self.ac._objective = MagicMock()
        self.ac._experiment_info = MagicMock(experiment_run_phase=0)
        self.setup_req = AgentSetupRequest(
            receiver_agent_conductor=self.ac.uid,
            sender_simulation_controller="0",
            experiment_run_id="1",
            experiment_run_instance_id="SomeInstance",
            experiment_run_phase=42,
            configuration=self.agent_params,
            sensors=[
                SensorInformation(0, MagicMock(), "TestSensor-1"),
                SensorInformation(0, MagicMock(), "TestSensor-2"),
            ],
            actuators=[
                ActuatorInformation(0, MagicMock(), "TestActuator-1"),
                ActuatorInformation(0, MagicMock(), "TestActuator-2"),
            ],
            muscle_name="TestAgent",
        )
        self.setup_req_empty = AgentSetupRequest(
            receiver_agent_conductor=self.ac.uid,
            sender_simulation_controller="0",
            experiment_run_instance_id="SomeExperimentRunInstance",
            experiment_run_phase=47,
            configuration=self.agent_params,
            experiment_run_id="1",
            sensors=list(),
            actuators=list(),
            muscle_name="TestAgent",
        )
        self.shutdown_req = ShutdownRequest(
            sender="Somebody", receiver=self.ac.uid, experiment_run_id="1"
        )

    @patch("palaestrai.agent.agent_conductor.aiomultiprocess.Process")
    def test_init_brain(self, mockaio):
        type(self.ac._experiment_info).experiment_run_uid = MagicMock(
            return_value="TestExperiment"
        )
        type(self.ac._experiment_info).experiment_run_phase = PropertyMock(
            return_value=0
        )
        self.ac._init_brain(self.setup_req.sensors, self.setup_req.actuators)

        self.assertEqual(mockaio.call_count, 1)
        self.assertIsInstance(self.ac._learner, Learner)
        self.assertIsInstance(self.ac._learner._brain, DummyBrain)
        self.assertEqual(len(self.ac._learner._brain.sensors), 2)
        self.assertEqual(len(self.ac._learner._brain.actuators), 2)

    @patch("palaestrai.agent.agent_conductor.aiomultiprocess.Process")
    def test_init_muscle(self, mockaio):
        type(self.ac._experiment_info).experiment_run_uid = MagicMock(
            return_value="TestExperiment"
        )
        type(self.ac._experiment_info).experiment_run_phase = PropertyMock(
            return_value=0
        )
        self.ac._learner = MagicMock()
        self.ac._init_muscle(MagicMock(), str(uuid4()))

        self.assertEqual(mockaio.call_count, 1)
        self.assertEqual(len(self.ac._rollout_workers), 1)
        self.assertEqual(len(self.ac._rollout_worker_processes), 1)

    @patch("palaestrai.agent.agent_conductor.aiomultiprocess.Process")
    def test_handle_agent_setup(self, mockaio):
        self.ac._init_brain = MagicMock()
        self.ac._init_muscle = MagicMock()

        rsp = self.ac._handle_agent_setup(self.setup_req)
        self.ac._init_brain.assert_called_once()
        self.ac._init_muscle.assert_called()
        self.assertIsInstance(rsp, AgentSetupResponse)

    @patch("palaestrai.agent.agent_conductor.aiomultiprocess.Process")
    async def test_handle_shutdown(self, _):
        self.ac.stop = MagicMock()
        self.ac._handle_shutdown_request(self.shutdown_req)
        self.ac.stop.assert_called_once()

    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=unittest.mock.AsyncMock(
            transceive=unittest.mock.AsyncMock(
                side_effect=[
                    AgentSetupRequest(
                        experiment_run_id="run away",
                        experiment_run_instance_id="run away instance",
                        experiment_run_phase=47,
                        receiver_agent_conductor="the servant",
                        sender_simulation_controller="the boss",
                        muscle_name="Yoho muscle",
                        actuators=[],
                        sensors=[],
                        configuration={"name": "Yoho muscle", "params": {}},
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
    async def test_run_until_shutdown(self, _):
        self.ac._load_brain = MagicMock()
        self.ac._init_brain = MagicMock()
        self.ac._load_muscle = MagicMock()
        self.ac._init_muscle = MagicMock()
        await self.ac.run()
        self.assertEqual(self.ac._state, BasicState.FINISHED)

    def test_load_brain_dumpers(self):
        type(self.ac._experiment_info).experiment_run_uid = MagicMock(
            return_value="TestExperiment"
        )
        type(self.ac._experiment_info).experiment_run_phase = PropertyMock(
            return_value=0
        )

        dumpers = self.ac._load_brain_dumpers()

        self.assertEqual(2, len(dumpers))
        self.assertIsInstance(dumpers[0], FileBrainDumper)
        self.assertIsInstance(dumpers[1], StoreBrainDumper)

    def test_implicit_brain_load_not_in_phase_0(self):
        type(self.ac._experiment_info).experiment_run_uid = MagicMock(
            return_value="TestExperiment"
        )
        type(self.ac._experiment_info).experiment_run_phase = PropertyMock(
            return_value=0
        )
        dumpers = self.ac._load_brain_dumpers()
        self.assertTrue(len(dumpers) > 0)
        self.assertIsNone(dumpers[0]._brain_source)

    def test_implicit_brain_load(self):
        type(self.ac._experiment_info).experiment_run_uid = MagicMock(
            return_value="TestExperiment"
        )
        type(self.ac._experiment_info).experiment_run_phase = PropertyMock(
            return_value=1
        )
        dumpers = self.ac._load_brain_dumpers()
        self.assertTrue(len(dumpers) > 0)
        self.assertIsNotNone(dumpers[0]._brain_source)
        self.assertEqual(dumpers[0]._brain_source.experiment_run_phase, 0)

    @patch("palaestrai.agent.agent_conductor.LOG")
    def test_load_brain_malformed_config(self, logmock):
        type(self.ac._experiment_info).experiment_run_uid = MagicMock(
            return_value="TestExperiment"
        )
        type(self.ac._experiment_info).experiment_run_phase = PropertyMock(
            return_value=0
        )
        self.ac._config["load"] = ["agent", "12341234", 0]

        dumpers = self.ac._load_brain_dumpers()
        self.assertEqual(2, len(dumpers))
        logmock.warning.assert_called()

    @patch("palaestrai.agent.agent_conductor.aiomultiprocess.Process")
    def test_replay_locations(self, _):
        replay_locs = [
            dict(agent="myelf", experiment_run="asdf", phase=1),
            dict(phase=0),
        ]
        self.ac._config["replay"] = replay_locs
        self.ac._load_brain = MagicMock()
        self.ac._init_brain([], [])
        self.assertEqual(len(self.ac._learner._experience_locations), 2)
        self.assertEqual(
            self.ac._learner._experience_locations[0].agent_name, "myelf"
        )
        self.assertEqual(
            self.ac._learner._experience_locations[1].agent_name, self.ac.name
        )


if __name__ == "__main__":
    unittest.main()
