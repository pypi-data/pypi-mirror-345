import unittest
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from queue import Queue
from tempfile import TemporaryDirectory
from typing import Optional
from unittest.mock import patch

import jsonpickle
import numpy as np
from sqlalchemy import select

import palaestrai.core.protocol
import palaestrai.store.database_model as dbm
from palaestrai.agent import (
    RewardInformation,
    SensorInformation,
    ActuatorInformation,
)
from palaestrai.core import RuntimeConfig
from palaestrai.experiment import ExperimentRun
from palaestrai.store.database_util import setup_database
from palaestrai.store.receiver import StoreReceiver
from palaestrai.types import Box, Mode, SimulationFlowControl


class TestReceiver(unittest.TestCase):
    experiment_run = ExperimentRun.load(
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / "fixtures"
        / "dummy_run.yml"
    )

    # Store all messages that we care about in the test as a list in order to
    # replay them piece by piece:
    messages = [
        palaestrai.core.protocol.ExperimentRunStartRequest(
            sender_executor_id="executor",
            receiver_run_governor_id="run_governor",
            experiment_run_id="MockExperimentRun-0",
            experiment_run=experiment_run,
        ),
        palaestrai.core.protocol.SimulationStartRequest(
            sender_run_governor_id="RunGovernor-0",
            receiver_simulation_controller_id="SimulationController-0",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            experiment_run_phase_id="Phase 42",
            experiment_run_phase_configuration={"mode": "TRAINING"},
        ),
        palaestrai.core.protocol.EnvironmentSetupResponse(
            sender_environment_conductor="EnvironmentConductor-0",
            receiver_simulation_controller="SimulationController-0",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            environment_id="EnvironmentConductor-0.Environment-0",
            environment_parameters={"Mock": "Parameters", "For": "Testing"},
            environment_type="DummyEnvironment",
            environment_name="Environment",
        ),
        palaestrai.core.protocol.EnvironmentUpdateResponse(
            sender_environment_id="EnvironmentConductor-0.Environment-0",
            receiver_simulation_controller_id="SimulationController-0",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            sensors=[
                SensorInformation(
                    uid="MockSensor-0",
                    value=np.array([08.15], dtype=np.float32),
                    space=Box(low=[0.0], high=[10.0]),
                )
            ],
            rewards=[
                RewardInformation(
                    value=23,
                    space=Box(low=0.0, high=470.0, shape=()),
                    uid="PseudoReward",
                )
            ],
            environment_name="Environment",
            done=False,
            flow_control_indicator=SimulationFlowControl.CONTINUE,
            flow_control_data={},
        ),
        palaestrai.core.protocol.AgentSetupRequest(
            sender_simulation_controller="SimulationController-0",
            receiver_agent_conductor="AgentConductor-0",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            muscle_name="Agent-0",
            configuration={"Agent": "Configuration", "Name": "Agent-0"},
            sensors=[
                SensorInformation(
                    uid="MockSensor-0",
                    value=np.array([08.15], dtype=np.float32),
                    space=Box(low=[0.0], high=[10.0]),
                ),
                SensorInformation(
                    uid="MockSensor-1",
                    value=np.array([42.47], dtype=np.float32),
                    space=Box(low=[0.0], high=[66.6]),
                ),
            ],
            actuators=[
                ActuatorInformation(
                    uid="MockActor-47",
                    value=np.array([23.0], dtype=np.float32),
                    space=Box(low=[-47.0], high=[+47.0]),
                )
            ],
        ),
        palaestrai.core.protocol.AgentSetupResponse(
            sender_agent_conductor="AgentConductor-0",
            receiver_simulation_controller="SimulationController-0",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            rollout_worker_id="Agent-0",
            muscle_name="Agent",
        ),
        palaestrai.core.protocol.MuscleUpdateRequest(
            sender_rollout_worker_id="AgentConductor-0.Agent-0",
            receiver_brain_id="Agent-0-Brain",
            muscle_uid="Agent-0-Muscle",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            sensor_readings=[],
            actuator_setpoints=[],
            rewards=[],
            objective=0,
            mode=Mode.TRAIN,
            statistics={"trust": 0.0},
            done=False,
            data=None,
        ),
        palaestrai.core.protocol.MuscleUpdateRequest(
            sender_rollout_worker_id="Agent-0",
            receiver_brain_id="Agent-0-Brain",
            muscle_uid="Agent-0-Muscle",
            experiment_run_id=experiment_run.uid,
            experiment_run_instance_id=experiment_run.instance_uid,
            experiment_run_phase=42,
            sensor_readings=[
                SensorInformation(
                    uid="MockSensor-0",
                    value=np.array([08.15], dtype=np.float32),
                    space=Box(low=[0.0], high=[10.0]),
                ),
                SensorInformation(
                    uid="MockSensor-1",
                    value=np.array([42.47], dtype=np.float32),
                    space=Box(low=[0.0], high=[66.6]),
                ),
            ],
            actuator_setpoints=[
                ActuatorInformation(
                    uid="MockActor-47",
                    value=np.array([23.0], dtype=np.float32),
                    space=Box(low=[-47.0], high=[+474747.0]),
                )
            ],
            rewards=[
                RewardInformation(
                    value=np.array([23.0], dtype=np.float32),
                    space=Box(low=[0.0], high=[4247.0]),
                    uid="PseudoReward",
                )
            ],
            objective=3.4,
            statistics={"trust": 1.0},
            done=False,
            mode=Mode.TEST,
            data=None,
            simtimes={
                "EnvironmentConductor-0.Environment-0": palaestrai.types.SimTime(
                    simtime_ticks=1, simtime_timestamp=datetime.now()
                )
            },
        ),
    ]

    def setUp(self) -> None:
        self.tempdir: Optional[TemporaryDirectory] = TemporaryDirectory()
        self.store_path = f"{self.tempdir.name}/palaestrai.db"
        self.store_uri = f"sqlite:///{self.store_path}"
        RuntimeConfig().reset()
        RuntimeConfig().load({"store_uri": self.store_uri})
        setup_database(self.store_uri)
        self.queue: Queue = Queue()
        self.store: Optional[StoreReceiver] = StoreReceiver(self.queue)

    def tearDown(self) -> None:
        self.store = None
        self.tempdir = None

    def test_handles_all_protocol_messages(self):
        all_message_types = [
            v
            for k, v in palaestrai.core.protocol.__dict__.items()
            if k.endswith("Request") or k.endswith("Response")
        ]
        for t in all_message_types:
            try:
                _ = self.store._message_dispatch[t]
            except KeyError:
                self.fail(
                    f"Message type {t} raises key error as it is unknown to "
                    f"the store receiver's dispatcher."
                )

    def test_stores_experiment_run(self):
        self.store.write(TestReceiver.messages[0])
        q = self.store._dbh.query(dbm.Experiment).join(dbm.ExperimentRun)
        self.assertEqual(q.count(), 1)
        experiment_record = q.first()
        self.assertEqual(len(experiment_record.experiment_runs), 1)
        experiment_run_record = experiment_record.experiment_runs[0]
        self.assertEqual(
            experiment_run_record.uid, TestReceiver.experiment_run.uid
        )
        self.assertIsInstance(experiment_run_record.document, dict)
        er = ExperimentRun.from_dict(experiment_run_record.document)
        experiment_run_json = jsonpickle.Unpickler().restore(
            experiment_run_record._document_json
        )
        self.assertIsNotNone(experiment_run_json)
        self.assertEqual(
            experiment_run_json["uid"], TestReceiver.experiment_run.uid
        )
        self.assertEqual(
            er.canonical_config, TestReceiver.experiment_run.canonical_config
        )
        q = self.store._dbh.query(dbm.ExperimentRunInstance)
        self.assertEqual(1, q.count())
        q = (
            self.store._dbh.query(dbm.Experiment)
            .join(dbm.ExperimentRun)
            .join(dbm.ExperimentRunInstance)
        )
        self.assertEqual(1, q.count())

    def test_stores_experiment_run_phase(self):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        q = self.store._dbh.query(dbm.ExperimentRunInstance)
        self.assertEqual(q.count(), 1)
        experiment_run_instance_record = q.first()
        self.assertIsNotNone(experiment_run_instance_record)
        self.assertEqual(
            experiment_run_instance_record.uid,
            TestReceiver.experiment_run.instance_uid,
        )
        q = self.store._dbh.query(dbm.ExperimentRunPhase)
        self.assertEqual(1, q.count())
        q = (
            self.store._dbh.query(dbm.Experiment)
            .join(dbm.ExperimentRun)
            .join(dbm.ExperimentRunInstance)
            .join(dbm.ExperimentRunPhase)
        )
        self.assertEqual(1, q.count())
        r = q.first()
        experiment_run_phase_record = (
            r.experiment_runs[0]
            .experiment_run_instances[0]
            .experiment_run_phases[0]
        )
        self.assertEqual(
            TestReceiver.messages[1].experiment_run_phase,
            experiment_run_phase_record.number,
        )
        self.assertEqual(
            TestReceiver.messages[1].experiment_run_phase_id,
            experiment_run_phase_record.uid,
        )
        self.assertEqual(
            TestReceiver.messages[1].experiment_run_phase_configuration,
            experiment_run_phase_record.configuration,
        )

        second_phase_start_request = deepcopy(TestReceiver.messages[1])
        second_phase_start_request.experiment_run_phase = 1
        second_phase_start_request.experiment_run_phase_id = "SecondPhase"
        second_phase_start_request.experiment_run_phase_configuration = {
            "mode": "TESTING",
            "episodes": 23,
        }
        self.store.write(second_phase_start_request)
        q = select(dbm.ExperimentRunPhase)
        r = self.store._dbh.execute(q).all()
        self.assertEqual(2, len(r))
        experiment_run_phase_record = r[1][dbm.ExperimentRunPhase]
        self.assertEqual(
            experiment_run_phase_record.configuration,
            second_phase_start_request.experiment_run_phase_configuration,
        )

    def test_stores_environment(self):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        self.store.write(TestReceiver.messages[2])
        q = self.store._dbh.query(dbm.Environment)
        self.assertEqual(1, q.count())
        q = (
            self.store._dbh.query(dbm.Experiment)
            .join(dbm.ExperimentRun)
            .join(dbm.ExperimentRunInstance)
            .join(dbm.ExperimentRunPhase)
            .join(dbm.Environment)
            .filter(
                dbm.Environment.uid
                == TestReceiver.messages[2].environment_name
            )
        )
        self.assertEqual(1, q.count())
        r = (
            q.first()
            .experiment_runs[0]
            .experiment_run_instances[0]
            .experiment_run_phases[0]
            .environments[0]
        )
        self.assertEqual(TestReceiver.messages[2].environment_name, r.uid)
        self.assertEqual(TestReceiver.messages[2].environment_id, r.worker_uid)
        self.assertEqual(TestReceiver.messages[2].environment_type, r.type)
        self.assertIsNotNone(r.parameters)

    def test_stores_world_state(self):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        self.store.write(TestReceiver.messages[2])
        self.store.write(TestReceiver.messages[3])
        q = self.store._dbh.query(dbm.WorldState)
        self.assertEqual(1, q.count())

        additional_world_state = deepcopy(TestReceiver.messages[3])
        additional_world_state.done = True
        self.store.write(additional_world_state)
        q = self.store._dbh.query(dbm.WorldState).order_by(
            dbm.WorldState.simtime_ticks
        )
        self.assertEqual(2, q.count())
        self.assertEqual(1, q[0].simtime_ticks)
        self.assertEqual(2, q[1].simtime_ticks)
        self.assertTrue(additional_world_state.is_terminal, q[1].done)

        q = (
            self.store._dbh.query(dbm.Experiment)
            .join(dbm.ExperimentRun)
            .join(dbm.ExperimentRunInstance)
            .join(dbm.ExperimentRunPhase)
            .join(dbm.Environment)
            .join(dbm.WorldState)
            .filter(
                dbm.Environment.uid
                == TestReceiver.messages[2].environment_name
            )
        )
        self.assertEqual(2, q.count())
        world_states = (
            q.first()
            .experiment_runs[0]
            .experiment_run_instances[0]
            .experiment_run_phases[0]
            .environments[0]
            .world_states
        )
        self.assertFalse(world_states[0].done)
        self.assertTrue(world_states[1].done)

    @patch("palaestrai.store.receiver.LOG")
    def test_stores_agent(self, logmock):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        self.store.write(TestReceiver.messages[4])
        self.assertFalse(logmock.critical.called)

        q = self.store._dbh.query(dbm.Agent)
        self.assertEqual(1, q.count())

        additional_run_phase = deepcopy(TestReceiver.messages[1])
        additional_run_phase.experiment_run_phase = 47
        additional_run_phase.experiment_run_phase_id = "Phase 47"
        self.store.write(additional_run_phase)
        q = self.store._dbh.query(dbm.ExperimentRunPhase)
        self.assertEqual(2, q.count())
        q = self.store._dbh.query(dbm.Agent)
        self.assertEqual(1, q.count())

        additional_agent_setup_request = deepcopy(TestReceiver.messages[4])
        additional_agent_setup_request.experiment_run_phase = (
            additional_run_phase.experiment_run_phase
        )
        self.store.write(additional_agent_setup_request)
        self.assertFalse(logmock.critical.called)
        q = self.store._dbh.query(dbm.ExperimentRunPhase)
        self.assertEqual(2, q.count())
        q = self.store._dbh.query(dbm.Agent)
        self.assertEqual(2, q.count())
        q = (
            select(dbm.ExperimentRunInstance, dbm.ExperimentRunPhase)
            .join(dbm.ExperimentRunInstance.experiment_run_phases)
            .where(
                dbm.ExperimentRunInstance.uid
                == additional_run_phase.experiment_run_instance_id,
                dbm.ExperimentRunPhase.number
                == additional_run_phase.experiment_run_phase,
            )
        )
        r = self.store._dbh.execute(q).all()
        self.assertEqual(1, len(r))
        self.assertEqual(1, len(r[0][dbm.ExperimentRunPhase].agents))

    @patch("palaestrai.store.receiver.LOG")
    def test_stores_muscles(self, logmock):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        self.store.write(TestReceiver.messages[4])
        self.store.write(TestReceiver.messages[5])
        self.assertFalse(logmock.critical.called)

        q = select(dbm.Agent).where(
            dbm.Agent.uid == TestReceiver.messages[5].sender_agent_conductor
        )
        r = self.store._dbh.execute(q).all()
        self.assertEqual(
            [TestReceiver.messages[5].rollout_worker_id],
            r[0][dbm.Agent].muscles,
        )

    @patch("palaestrai.store.receiver.LOG")
    def test_stores_muscle_actions(self, logmock):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        self.store.write(TestReceiver.messages[4])
        self.store.write(TestReceiver.messages[5])
        self.store.write(TestReceiver.messages[6])
        self.assertFalse(
            logmock.critical.called, msg=logmock.critical.call_args
        )
        self.assertFalse(logmock.error.called, msg=logmock.critical.call_args)
        self.assertFalse(
            logmock.warning.called, msg=logmock.critical.call_args
        )

        self.store.write(TestReceiver.messages[7])
        self.assertFalse(
            logmock.critical.called, msg=logmock.critical.call_args
        )
        self.assertFalse(logmock.error.called, msg=logmock.critical.call_args)
        self.assertFalse(
            logmock.warning.called, msg=logmock.critical.call_args
        )

        r = self.store._dbh.execute(
            select(dbm.MuscleAction).order_by(dbm.MuscleAction.id)
        ).all()
        self.assertListEqual(
            r[0][dbm.MuscleAction].sensor_readings,
            TestReceiver.messages[7].sensor_readings,
        )
        self.assertListEqual(
            r[0][dbm.MuscleAction].actuator_setpoints,
            TestReceiver.messages[7].actuator_setpoints,
        )
        self.assertListEqual(
            r[0][dbm.MuscleAction].rewards,
            TestReceiver.messages[7].rewards,
        )
        self.assertEqual(
            r[0][dbm.MuscleAction].objective,
            TestReceiver.messages[7].objective,
        )
        self.assertEqual(
            r[0][dbm.MuscleAction].statistics,
            TestReceiver.messages[7].statistics,
        )

        self.assertEqual(
            r[0][dbm.MuscleAction].simtimes[
                TestReceiver.messages[2].environment_name
            ]["simtime_ticks"],
            TestReceiver.messages[7]
            .simtimes[TestReceiver.messages[2].environment_id]
            .simtime_ticks,
        )
        self.assertEqual(
            r[0][dbm.MuscleAction].simtimes[
                TestReceiver.messages[2].environment_name
            ]["simtime_timestamp"],
            TestReceiver.messages[7]
            .simtimes[TestReceiver.messages[2].environment_id]
            .simtime_timestamp.isoformat(),
        )

        self.assertEqual(
            r[0][dbm.MuscleAction].walltime,
            TestReceiver.messages[7].walltime,
        )

    @patch("palaestrai.store.receiver.LOG")
    def test_stores_world_states_with_infinity(self, logmock):
        self.store.write(TestReceiver.messages[0])
        self.store.write(TestReceiver.messages[1])
        self.store.write(TestReceiver.messages[2])

        environment_update_response = deepcopy(TestReceiver.messages[3])
        environment_update_response.sensors = [
            SensorInformation(
                uid="MockSensor-0",
                value=np.array([np.Infinity], dtype=np.float32),
                space=Box(low=[0.0], high=[np.Infinity]),
            ),
        ]
        try:
            self.store.write(environment_update_response)
        except Exception as e:
            self.fail(str(e))
        self.assertFalse(
            logmock.critical.called, msg=logmock.critical.call_args
        )
        r = self.store._dbh.execute(select(dbm.WorldState)).one()
        self.assertTrue(
            all(np.isnan(s()[0]) for s in r[dbm.WorldState].state_dump),
            msg="NaN and Infinity must be converted to NULL/None",
        )


if __name__ == "__main__":
    unittest.main()
