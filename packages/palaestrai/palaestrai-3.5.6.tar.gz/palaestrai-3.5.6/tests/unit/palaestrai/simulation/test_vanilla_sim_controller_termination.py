from unittest import TestCase

from palaestrai.agent import RewardInformation
from palaestrai.agent.sensor_information import SensorInformation
from palaestrai.core.protocol import EnvironmentUpdateResponse
from palaestrai.simulation import VanillaSimControllerTerminationCondition
from palaestrai.types import Discrete, SimulationFlowControl


class TestVanillaSimControllerTerminationCondition(TestCase):
    def test_check_termination_true(self):
        term_cond = VanillaSimControllerTerminationCondition()
        self.assertTrue(
            term_cond.check_termination(
                EnvironmentUpdateResponse(
                    sender_environment_id="0",
                    receiver_simulation_controller_id="0",
                    experiment_run_id="0",
                    experiment_run_instance_id="0-0",
                    experiment_run_phase=47,
                    environment_name="The World",
                    sensors=[SensorInformation(1, Discrete(2), "0")],
                    rewards=[RewardInformation(0, Discrete(2), "Test")],
                    done=True,
                    flow_control_indicator=SimulationFlowControl.RESET,
                )
            )
        )

    def test_check_termination_False(self):
        term_cond = VanillaSimControllerTerminationCondition()
        self.assertFalse(
            term_cond.check_termination(
                EnvironmentUpdateResponse(
                    sender_environment_id="0",
                    receiver_simulation_controller_id="0",
                    experiment_run_id="0",
                    experiment_run_instance_id="0-0",
                    experiment_run_phase=47,
                    environment_name="Zombieland",
                    sensors=[SensorInformation(1, Discrete(2), "0")],
                    rewards=[RewardInformation(0, Discrete(2), "Test")],
                    done=False,
                    flow_control_indicator=SimulationFlowControl.CONTINUE,
                )
            )
        )
