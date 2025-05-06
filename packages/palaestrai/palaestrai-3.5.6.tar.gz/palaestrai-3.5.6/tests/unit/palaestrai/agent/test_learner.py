from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch, AsyncMock, MagicMock

from palaestrai.agent import Learner
from palaestrai.agent import (
    SensorInformation,
    ActuatorInformation,
    RewardInformation,
    DummyBrain,
)
from palaestrai.core import MajorDomoWorker
from palaestrai.core.protocol import (
    MuscleUpdateResponse,
    MuscleShutdownResponse,
    MuscleUpdateRequest,
    MuscleShutdownRequest,
)
from palaestrai.experiment import TerminationCondition
from palaestrai.types import (
    Discrete,
    ExperienceLocation,
    Mode,
    SimulationFlowControl,
)


class _MockTCOne(TerminationCondition):
    pass


class _MockTCTwo(TerminationCondition):
    pass


class TestLearner(IsolatedAsyncioTestCase):
    _muscle_shutdown_request = MuscleShutdownRequest(
        sender_muscle_id="muscle-id-asdf",
        receiver_brain_id="brain-id",
        experiment_run_id="exp_42",
        experiment_run_instance_id="exp_42_instance",
        experiment_run_phase=42,
    )

    @patch("palaestrai.agent.Memory.append")
    @patch("palaestrai.agent.DummyBrain.thinking")
    @patch("palaestrai.agent.dummy_brain.DummyBrain.store")
    @patch("palaestrai.agent.dummy_brain.DummyBrain.load")
    @patch(
        "palaestrai.core.event_state_machine.MajorDomoWorker",
        return_value=AsyncMock(
            transceive=AsyncMock(
                side_effect=[
                    MuscleUpdateRequest(
                        sender_rollout_worker_id="muscle-id-asdf",
                        receiver_brain_id="brain-id",
                        muscle_uid="muscle-id",
                        sensor_readings=[
                            SensorInformation(1, Discrete(2), "0")
                        ],
                        actuator_setpoints=[
                            ActuatorInformation(0, Discrete(2), "0")
                        ],
                        experiment_run_id="exp_42",
                        experiment_run_instance_id="exp_42_instance",
                        experiment_run_phase=42,
                        rewards=[RewardInformation(2, Discrete(3), "Test")],
                        objective=2.0,
                        statistics={},
                        mode=Mode.TRAIN,
                        done=False,
                        data=None,
                    ),
                    _muscle_shutdown_request,
                ]
            )
        ),
    )
    async def test_handle_agent_update(
        self,
        major_domo_worker: MajorDomoWorker,
        rollout_brain_load,
        rollout_brain_store,
        brain_thinking,
        memory_append,
    ):
        learner = Learner(DummyBrain(), "brain-id", "brain-name")

        # noinspection PyUnresolvedReferences
        await learner.run()  # type: ignore[attr-defined]

        self.assertIsInstance(
            # noinspection PyUnresolvedReferences
            learner.__esm__._mdp_worker.transceive.mock_calls[1].args[0],  # type: ignore[attr-defined]
            MuscleUpdateResponse,
            MuscleShutdownResponse,
        )

        self.assertTrue(brain_thinking.called)
        self.assertTrue(memory_append)

    async def test_statistics(self):
        brain = DummyBrain()
        brain._memory = MagicMock()
        brain.thinking = MagicMock()

        brain.add_statistics("foo", 42)
        brain.add_statistics("bar", {"baz": "quux"})

        learner = Learner(brain, "brain-id", "brain-name")
        rsp = await learner._handle_muscle_update_request(MagicMock())
        self.assertEqual(
            rsp.statistics,
            {
                "foo": 42,
                "bar": {"baz": "quux"},
            },
        )

    @patch("palaestrai.agent.learner.Session")
    async def test_setup(self, db_session_mock):
        brain = DummyBrain()
        brain.setup = MagicMock()
        brain.try_load_brain_dump = MagicMock()
        brain.pretrain = MagicMock()
        learner = Learner(brain, "brain-id", "brain-name")
        learner._experience_locations = [
            ExperienceLocation(
                agent_name="Experienced Agent",
                experiment_run_phase=0,
                experiment_run_uid="Train the inexperienced agent",
            )
        ]
        learner.setup()
        brain.setup.assert_called()
        brain.try_load_brain_dump.assert_called()
        brain.pretrain.assert_called()
        db_session_mock.assert_called()

    async def test_termination_conditions(self):
        learner = Learner(MagicMock(), "brain-id", "brain-name")
        learner._termination_conditions = [
            MagicMock(
                spec=_MockTCOne,
                brain_flow_control=MagicMock(
                    side_effect=[
                        (
                            SimulationFlowControl.RESET,
                            "Hello!",
                        )
                    ]
                ),
            ),
            MagicMock(
                spec=_MockTCTwo,
                brain_flow_control=MagicMock(
                    side_effect=[
                        (
                            SimulationFlowControl.STOP_PHASE,
                            {"success": 42},
                        )
                    ]
                ),
            ),
        ]
        rsp = await learner._handle_muscle_update_request(MagicMock())
        self.assertEqual(
            rsp.flow_control_indicator, SimulationFlowControl.STOP_PHASE
        )
        self.assertEqual(len(rsp.flow_control_data), 2)
        self.assertDictEqual(
            rsp.flow_control_data["_MockTCTwo"][1], {"success": 42}
        )

    @patch("palaestrai.agent.learner.LOG")
    async def test_handle_no_termination_conditions(self, logmock):
        learner = Learner(MagicMock(), "brain-id", "brain-name")
        learner._termination_conditions = []
        rsp = await learner._handle_muscle_update_request(MagicMock())
        self.assertEqual(
            rsp.flow_control_indicator, SimulationFlowControl.CONTINUE
        )
        self.assertTrue(logmock.warning.called)
