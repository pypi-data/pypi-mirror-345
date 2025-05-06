from __future__ import annotations

from pathlib import Path
from typing import List
from unittest import TestCase
from tempfile import TemporaryDirectory

import pandas as pd
from pandas import Timestamp

from palaestrai.store import Session
import palaestrai.store.query as palq
from palaestrai.core import RuntimeConfig


class QueryTest(TestCase):
    def setUp(self) -> None:
        self._tmpdir = TemporaryDirectory()
        RuntimeConfig().reset()
        RuntimeConfig().load(
            {"store_uri": f"sqlite:///{self._tmpdir.name}/palaestrai.db"}
        )

        self._dbh = Session()

        fixtures_file_path = (
            Path(__file__).parent
            / ".."
            / ".."
            / ".."
            / "fixtures"
            / "dummy_run_data.sql"
        ).absolute()
        with open(fixtures_file_path, "r") as fp:
            self._dbh.connection().connection.executescript(fp.read())

    def test_experiments_and_runs_configurations(self):
        res = palq.experiments_and_runs_configurations(self._dbh)
        self.assertEqual(7, len(res))
        self.assertTrue(
            res.experiment_run_phase_mode.isin(["train", "test"]).all()
        )

    def test_like_dataframe(self):
        erc = palq.experiments_and_runs_configurations(self._dbh)
        # Try to get data only about the test phase:
        actions = palq.muscle_actions(
            self._dbh,
            like_dataframe=erc[
                (erc.experiment_run_phase_mode == "test")
                & (erc.experiment_name == "Dummy Runs")
            ],
            predicate=lambda query: query.limit(100),
        )
        self.assertTrue(len(actions) > 1)
        self.assertTrue(actions.index[-1] > 10)
        self.assertTrue(
            actions.agent_name.isin(["Agent One_2", "Agent Two_2"]).all()
        )

    def test_get_max_experiment_run_instance_id(self):
        experiment_name = "Dummy Runs"
        experiment_run_uid = "Dummy experiment run where the agents take turns"

        (
            experiment_run_instance_id,
            _,
        ) = palq.get_max_experiment_run_instance_uid(
            self._dbh, experiment_name, experiment_run_uid
        )

        self.assertEqual(
            experiment_run_instance_id, "b7af3425-9cc9-4965-93b8-17de352538d7"
        )

    def test_select_agent(self):
        experiment_name = "Dummy Runs"
        experiment_run_uid = "Dummy experiment run where the agents take turns"

        (
            experiment_run_instance_uid,
            erc,
        ) = palq.get_max_experiment_run_instance_uid(
            self._dbh, experiment_name, experiment_run_uid
        )

        experiment_ids = [str(erc.experiment_id.iloc[0])]
        experiment_run_uids = [str(erc.experiment_run_uid.iloc[0])]
        experiment_run_instance_uids = [
            str(erc.experiment_run_instance_uid.iloc[0])
        ]
        experiment_run_phase_uids = ["First Phase"]

        erc = palq.agents_configurations(
            self._dbh,
            experiment_ids=experiment_ids,
            experiment_run_uids=experiment_run_uids,
            experiment_run_instance_uids=experiment_run_instance_uids,
            experiment_run_phase_uids=experiment_run_phase_uids,
        )

        self.assertListEqual(
            erc.agent_name.to_list(), ["Agent Two", "Agent One"]
        )

    def test_select_muscle_actions(self):
        experiment_name = "Dummy Runs"
        experiment_run_uid = "Dummy experiment run where the agents take turns"

        (
            experiment_run_instance_uid,
            erc,
        ) = palq.get_max_experiment_run_instance_uid(
            self._dbh, experiment_name, experiment_run_uid
        )

        experiment_ids = [str(erc.experiment_id.iloc[0])]
        experiment_run_uids = [str(erc.experiment_run_uid.iloc[0])]
        experiment_run_instance_uids = [
            str(erc.experiment_run_instance_uid.iloc[0])
        ]
        experiment_run_phase_uids = ["First Phase"]
        agent_uids = ["Agent One"]

        erc = palq.muscle_actions(
            self._dbh,
            experiment_ids=experiment_ids,
            experiment_run_uids=experiment_run_uids,
            experiment_run_instance_uids=experiment_run_instance_uids,
            experiment_run_phase_uids=experiment_run_phase_uids,
            agent_uids=agent_uids,
        )

        sensor_readings = erc.muscle_sensor_readings.iloc[0]
        sensor_reading_values = [
            sensor_reading.value for sensor_reading in sensor_readings
        ]
        self.assertListEqual(sensor_reading_values, [0, 0, 0, 0, 0])

        muscle_actuator_setpoints = erc.muscle_actuator_setpoints.iloc[0]
        muscle_actuator_setpoint_values = [
            muscle_actuator_setpoint.value
            for muscle_actuator_setpoint in muscle_actuator_setpoints
        ]
        self.assertListEqual(muscle_actuator_setpoint_values, [0, 0, 0, 0, 0])
        self.assertEqual(erc.muscle_action_objective.iloc[0], 1.0)

    def test_latest_muscle_action_values(self):
        experiment_name = "Dummy Runs"
        experiment_run_uid = "Dummy experiment run where the agents take turns"
        experiment_run_phase_uids = ["First Phase"]
        agent_uids = ["Agent One"]
        erc = palq.latest_muscle_action_values(
            self._dbh,
            experiment_name=experiment_name,
            experiment_run_uid=experiment_run_uid,
            experiment_run_phase_uids=experiment_run_phase_uids,
            agent_uids=agent_uids,
        )
        _asserted_values = {
            "myenv_tt.0": [0, 0],
            "myenv_tt.1": [0, 0],
            "myenv_tt.2": [0, 0],
            "myenv_tt.3": [0, 0],
            "myenv_tt.4": [0, 0],
        }

        _setpoints_dict = erc.muscle_actuator_setpoints.iloc[0]

        for uid in _setpoints_dict.keys():
            self.assertEqual(_setpoints_dict[uid], _asserted_values[uid][0])

        _sensor_readings_dict = erc.muscle_sensor_readings.iloc[0]

        for uid in _sensor_readings_dict.keys():
            self.assertEqual(
                _sensor_readings_dict[uid], _asserted_values[uid][1]
            )

        self.assertEqual(erc.muscle_action_rewards.iloc[0]["Dummy Reward"], 1)

        first_simtime_ticks = erc.muscle_action_simtime_ticks.iloc[0]
        self.assertEqual(first_simtime_ticks, 1)

        self.assertEqual(erc.muscle_action_objective.iloc[0], 1.0)

    def test_latest_muscle_action_values_non_empty_multi_index(self):
        experiment_name = "Dummy experiment record for experiment run Classic-ARL-Experiment-0"
        experiment_run_uid = "Classic-ARL-Experiment-0"
        experiment_run_phase_uids = ["phase_ac_training"]
        agent_uids = ["Gandalf SAC (autocurriculum-training)"]
        erc = palq.latest_muscle_action_values_non_empty_multi_index(
            self._dbh,
            experiment_name=experiment_name,
            experiment_run_uid=experiment_run_uid,
            experiment_run_phase_uids=experiment_run_phase_uids,
            agent_uids=agent_uids,
        )

        self.assertListEqual(
            list(erc.muscle_sensor_readings.columns),
            [
                "midas_powergrid.Powergrid-0.0-line-2.in_service",
                "midas_powergrid.Powergrid-0.0-line-4.loading_percent",
                "midas_powergrid.Powergrid-0.0-bus-14.vm_pu",
                "midas_powergrid.Powergrid-0.0-bus-3.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-1.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-13.in_service",
                "midas_powergrid.Powergrid-0.0-bus-2.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-10.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-13.va_degree",
                "midas_powergrid.Powergrid-0.0-line-9.in_service",
                "midas_powergrid.Powergrid-0.0-line-8.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-6.in_service",
                "midas_powergrid.Powergrid-0.0-bus-5.va_degree",
                "midas_powergrid.Powergrid-0.0-line-14.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-11.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-0.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-7.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-12.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-10.in_service",
                "midas_powergrid.Powergrid-0.0-bus-7.va_degree",
                "midas_powergrid.Powergrid-0.0-line-11.in_service",
                "midas_powergrid.Powergrid-0.0-bus-13.vm_pu",
                "midas_powergrid.Powergrid-0.0-bus-8.vm_pu",
                "midas_powergrid.Powergrid-0.0-bus-10.vm_pu",
                "midas_powergrid.Powergrid-0.0-bus-6.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-10.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-3.loading_percent",
                "midas_powergrid.Powergrid-0.0-bus-3.vm_pu",
                "midas_powergrid.Powergrid-0.0-bus-4.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-13.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-5.loading_percent",
                "midas_powergrid.Powergrid-0.0-bus-6.va_degree",
                "midas_powergrid.Powergrid-0.0-line-1.loading_percent",
                "midas_powergrid.Powergrid-0.0-bus-11.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-11.vm_pu",
                "midas_powergrid.Powergrid-0.0-bus-2.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-2.loading_percent",
                "midas_powergrid.Powergrid-0.0-bus-4.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-14.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-7.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-14.in_service",
                "midas_powergrid.Powergrid-0.0-line-12.in_service",
                "midas_powergrid.Powergrid-0.0-line-9.loading_percent",
                "midas_powergrid.Powergrid-0.0-line-1.in_service",
                "midas_powergrid.Powergrid-0.0-bus-9.va_degree",
                "midas_powergrid.Powergrid-0.0-line-6.loading_percent",
                "midas_powergrid.Powergrid-0.0-bus-1.va_degree",
                "midas_powergrid.Powergrid-0.0-bus-8.va_degree",
                "midas_powergrid.Powergrid-0.0-line-8.in_service",
                "midas_powergrid.Powergrid-0.0-line-7.in_service",
                "midas_powergrid.Powergrid-0.0-line-5.in_service",
                "midas_powergrid.Powergrid-0.0-bus-12.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-0.in_service",
                "midas_powergrid.Powergrid-0.0-bus-12.va_degree",
                "midas_powergrid.Powergrid-0.0-line-3.in_service",
                "midas_powergrid.Powergrid-0.0-bus-9.vm_pu",
                "midas_powergrid.Powergrid-0.0-line-4.in_service",
                "midas_powergrid.Powergrid-0.0-bus-5.vm_pu",
            ],
        )
        self.assertTrue("vm_pu-min" in erc.muscle_action_rewards)
        self.assertTrue(
            all(x < 1.15 for x in erc.muscle_action_rewards["vm_pu-max"])
        )
        self.assertListEqual(
            list(
                erc.muscle_action_simtime_timestamp.muscle_action_simtime_timestamp
            ),
            ["None", "2020-02-23T08:00:06+01:00", "2020-02-23T08:00:10+01:00"],
        )

    def _assert_list_eq_for_all_sub_cols(
        self, erc_col: pd.DataFrame, asserted_values: List
    ):
        for column in erc_col.columns:
            self.assertListEqual(
                list(erc_col[column]),
                asserted_values,
            )
