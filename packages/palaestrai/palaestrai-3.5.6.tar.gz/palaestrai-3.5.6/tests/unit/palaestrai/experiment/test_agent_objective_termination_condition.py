from __future__ import annotations
from typing import TYPE_CHECKING

import unittest
from unittest.mock import MagicMock
import numpy as np

from palaestrai.agent import Memory
from palaestrai.util.dynaloader import load_with_params
from palaestrai.experiment import AgentObjectiveTerminationCondition
from palaestrai.types import SimulationFlowControl
from palaestrai.core.protocol import SimulationControllerTerminationRequest


class AgentObjectiveTerminationConditionTest(unittest.TestCase):
    def test_init(self):
        tc = AgentObjectiveTerminationCondition(
            **{
                "Nice Agent": dict(
                    brain_avg10=8.9, brain_avg100=5.1, phase_avg10=8
                )
            }
        )
        self.assertEqual(tc._brain_avgs["Nice Agent"][10], 8.9)
        self.assertEqual(tc._brain_avgs["Nice Agent"][100], 5.1)
        self.assertEqual(tc._phase_avgs["Nice Agent"][10], 8.0)

    def test_brain_phase_control(self):
        memory = Memory()
        brain = MagicMock(memory=memory)
        brain.name = "nice_agent"
        cumsum = 0
        for i in range(100):
            cumsum += i + 1.0
            memory.append(
                "m1",
                [MagicMock()],
                [MagicMock()],
                [MagicMock(uid="r", value=float(i))],
                False,
                None,
                None,
                np.array([1.0 + float(i)]),
            )
        tc = AgentObjectiveTerminationCondition(
            nice_agent=dict(brain_avg10=8.9, brain_avg100=5.1, phase_avg10=8)
        )
        tci, tcd = tc.brain_flow_control(brain, MagicMock(sender="m1"))
        self.assertEqual(tci, SimulationFlowControl.RESET)
        self.assertEqual(len(tcd[brain.name]), 3)
        self.assertEqual(tcd[brain.name][10], 95.5)
        self.assertEqual(tcd[brain.name]["sum"], cumsum)

    def test_load_with_params(self):
        agent_name = "Some nice agent with spaces in its name"
        tc = load_with_params(
            "palaestrai.experiment:AgentObjectiveTerminationCondition",
            {agent_name: {"brain_avg10": 95.5}},
        )
        memory = Memory()
        brain = MagicMock(memory=memory)
        brain.name = agent_name
        for i in range(100):
            memory.append(
                "m1",
                [MagicMock()],
                [MagicMock()],
                [MagicMock(uid="r", value=float(i))],
                False,
                None,
                None,
                np.array([1.0 + float(i)]),
            )
        tci, tcd = tc.brain_flow_control(brain, MagicMock(sender="m1"))
        self.assertEqual(tci, SimulationFlowControl.RESET)
        self.assertEqual(len(tcd[brain.name]), 2)
        self.assertEqual(tcd[brain.name][10], 95.5)

    def test_interop_brain_phase(self):
        memory = Memory()
        brain = MagicMock(memory=memory)
        brain.name = "nice_agent"
        for i in range(5):
            memory.append(
                "m1",
                [MagicMock()],
                [MagicMock()],
                [MagicMock(uid="r", value=float(i))],
                False,
                None,
                None,
                np.array([1.0 + float(i)]),
            )
        tc1 = AgentObjectiveTerminationCondition(
            nice_agent=dict(brain_avg5=3.0)
        )
        tci, tcd = tc1.brain_flow_control(brain, MagicMock(sender="m1"))
        self.assertEqual(tci, SimulationFlowControl.RESET)

        tc2 = AgentObjectiveTerminationCondition(
            nice_agent=dict(phase_avg5=3.0)
        )
        for _ in range(4):
            tci2, tcd2 = tc2.phase_flow_control(
                MagicMock(
                    experiment_run=MagicMock(
                        simulation_controllers=MagicMock(return_value=[1])
                    )
                ),
                MagicMock(
                    sender="worker-1",
                    sender_simulation_controller="worker-1",
                    flow_control_indicator=SimulationFlowControl.RESET,
                    flow_control_data={
                        "AgentObjectiveTerminationCondition": (
                            SimulationFlowControl.RESET,
                            tcd,
                        ),
                    },
                ),
            )
            self.assertEqual(tci2, SimulationFlowControl.RESET)
        tci2, tcd2 = tc2.phase_flow_control(
            MagicMock(
                experiment_run=MagicMock(
                    simulation_controllers=MagicMock(return_value=[1])
                )
            ),
            MagicMock(
                sender="worker-1",
                sender_simulation_controller="worker-1",
                flow_control_indicator=SimulationFlowControl.RESET,
                flow_control_data={
                    "AgentObjectiveTerminationCondition": (
                        SimulationFlowControl.RESET,
                        tcd,
                    ),
                },
            ),
        )
        self.assertEqual(tci2, SimulationFlowControl.STOP_PHASE)

    def test_interop_brain_phase_multiworker(self):
        memory = Memory()
        brain = MagicMock(memory=memory)
        brain.name = "nice_agent"
        for i in range(5):
            memory.append(
                "m1",
                [MagicMock()],
                [MagicMock()],
                [MagicMock(uid="r", value=float(i))],
                False,
                None,
                None,
                np.array([1.0 + float(i)]),
            )
        tc1 = AgentObjectiveTerminationCondition(
            nice_agent=dict(brain_avg5=3.0)
        )
        tci, tcd = tc1.brain_flow_control(brain, MagicMock(sender="m1"))
        self.assertEqual(tci, SimulationFlowControl.RESET)

        tc2 = AgentObjectiveTerminationCondition(
            nice_agent=dict(phase_avg5=3.0)
        )
        for _ in range(4):
            tci2, tcd2 = tc2.phase_flow_control(
                MagicMock(
                    experiment_run=MagicMock(
                        simulation_controllers=MagicMock(return_value=[1])
                    )
                ),
                MagicMock(
                    sender="worker-1",
                    sender_simulation_controller="worker-1",
                    flow_control_indicator=SimulationFlowControl.RESET,
                    flow_control_data={
                        "AgentObjectiveTerminationCondition": (
                            SimulationFlowControl.RESET,
                            tcd,
                        ),
                    },
                ),
            )
            self.assertEqual(tci2, SimulationFlowControl.RESET)
        tci2, tcd2 = tc2.phase_flow_control(
            MagicMock(
                experiment_run=MagicMock(
                    simulation_controllers=MagicMock(return_value=[1])
                )
            ),
            MagicMock(
                sender="worker-1",
                sender_simulation_controller="worker-1",
                flow_control_indicator=SimulationFlowControl.RESET,
                flow_control_data={
                    "AgentObjectiveTerminationCondition": (
                        SimulationFlowControl.RESET,
                        tcd,
                    ),
                },
            ),
        )
        self.assertEqual(tci2, SimulationFlowControl.STOP_PHASE)

        # Getting a signal from another worker doesn't change the overall
        # result, as the best worker wins:

        tcd["nice_agent"][5] = -10_000
        tcd["nice_agent"]["sum"] = -10_000
        tci2, tcd2 = tc2.phase_flow_control(
            MagicMock(
                experiment_run=MagicMock(
                    simulation_controllers=MagicMock(return_value=[1])
                )
            ),
            MagicMock(
                sender="worker-2",
                sender_simulation_controller="worker-2",
                flow_control_indicator=SimulationFlowControl.RESET,
                flow_control_data={
                    "AgentObjectiveTerminationCondition": (
                        SimulationFlowControl.RESET,
                        tcd,
                    ),
                },
            ),
        )
        self.assertEqual(tci2, SimulationFlowControl.STOP_PHASE)

    def test_phase_short_circuit_termination(self):
        tc = AgentObjectiveTerminationCondition(
            nice_agent=dict(brain_avg5=3.0)
        )
        rg_mock = MagicMock()
        term_req = MagicMock(spec=SimulationControllerTerminationRequest)
        term_req.flow_control_indicator = SimulationFlowControl.RESET

        fci, fcd = tc.phase_flow_control(rg_mock, term_req)
        rg_mock.assert_not_called()
        self.assertEqual(fci, SimulationFlowControl.STOP_PHASE)

        term_req.flow_control_indicator = SimulationFlowControl.CONTINUE
        fci, fcd = tc.phase_flow_control(rg_mock, term_req)
        rg_mock.assert_not_called()
        self.assertEqual(fci, SimulationFlowControl.STOP_PHASE)


if __name__ == "__main__":
    unittest.main()
