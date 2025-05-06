from unittest import TestCase

import numpy as np
import pandas as pd
from numpy import testing as npt
from pandas import testing as pdt

from palaestrai.agent import (
    RewardInformation,
    ActuatorInformation,
    SensorInformation,
)
from palaestrai.agent.memory import Memory, _MuscleMemory
from palaestrai.types import Box


class TestMemory(TestCase):
    def setUp(self) -> None:
        self.rewards = [
            RewardInformation(
                1.0,
                Box(low=0, high=10, shape=(), dtype=np.float64),
                "reward_1",
            ),
            RewardInformation(
                2.0,
                Box(low=0, high=10, shape=(), dtype=np.float64),
                "reward_2",
            ),
        ]
        self.rewards2 = [
            RewardInformation(
                3.0,
                Box(low=0, high=10, shape=(), dtype=np.float64),
                "reward_1",
            ),
            RewardInformation(
                4.0,
                Box(low=0, high=10, shape=(), dtype=np.float64),
                "reward_2",
            ),
        ]
        self.actions = [
            ActuatorInformation(
                np.array([1.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "action_1",
            ),
            ActuatorInformation(
                np.array([2.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "action_2",
            ),
        ]
        self.actions2 = [
            ActuatorInformation(
                np.array([3.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "action_1",
            ),
            ActuatorInformation(
                np.array([4.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "action_2",
            ),
        ]
        self.observations = [
            SensorInformation(
                np.array([1.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "observation_1",
            ),
            SensorInformation(
                np.array([2.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "observation_2",
            ),
        ]
        self.observations2 = [
            SensorInformation(
                np.array([3.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "observation_1",
            ),
            SensorInformation(
                np.array([4.0], dtype=np.float32),
                Box(low=0, high=10, shape=(1,), dtype=np.float32),
                "observation_2",
            ),
        ]
        self.internal_rewards = np.array([1.0])
        self.internal_rewards2 = np.array([2.0])
        self.memory = Memory()

    def test_add_with_correct_information_to_empty_memory(self):
        self.memory.append(
            "my muscle",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
        )
        pdt.assert_series_equal(
            self.memory.tail(2).rewards.iloc[-1],
            pd.Series([1.0, 2.0]),
            check_index=False,
            check_names=False,
        )

        s = pd.Series(np.array([1.0, 2.0], dtype=np.float32))

        pdt.assert_series_equal(
            self.memory.tail(2).actuator_setpoints.iloc[-1],
            s,
            check_index=False,
            check_names=False,
        )
        pdt.assert_series_equal(
            self.memory.tail(2).sensor_readings.iloc[-1],
            s,
            check_index=False,
            check_names=False,
        )

    def test_add_with_correct_information_to_memory(self):
        self.memory.append(
            "test muscle",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
        )
        self.memory.append(
            "test muscle",
            sensor_readings=self.observations2,
            actuator_setpoints=self.actions2,
            rewards=self.rewards2,
        )
        pdt.assert_series_equal(
            self.memory.tail(2).rewards.iloc[-1],
            pd.Series([3.0, 4.0]),
            check_index=False,
            check_names=False,
        )

        s = pd.Series(np.array([3.0, 4.0], dtype=np.float32))

        pdt.assert_series_equal(
            self.memory.tail(2).actuator_setpoints.iloc[-1],
            s,
            check_index=False,
            check_names=False,
        )
        pdt.assert_series_equal(
            self.memory.tail(2).sensor_readings.iloc[-1],
            s,
            check_index=False,
            check_names=False,
        )

    def test_add_nd_box(self):
        sensi = [
            SensorInformation(
                np.array([1.0, 1.0], dtype=np.float64),
                Box(
                    low=np.array([0.0, 0.0]),
                    high=np.array([10.0, 10.0]),
                ),
                "obs 42",
            ),
            SensorInformation(
                np.array([2.0, 2.0], dtype=np.float64),
                Box(
                    low=np.array([0.0, 0.0]),
                    high=np.array([10.0, 10.0]),
                ),
                "obs 47",
            ),
        ]
        self.memory.append(
            "Hey!", sensor_readings=sensi, actuator_setpoints=[], rewards=[]
        )
        self.assertIsInstance(
            self.memory.tail(2).sensor_readings["obs 42"][0], np.float64
        )
        self.assertTrue(
            np.all(
                [
                    self.memory.tail(2).sensor_readings["obs 42"],
                    sensi[0].value,
                ]
            )
        )

    def test_tail(self):
        self.memory.append(
            muscle_uid=str(__name__) + "_1",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
            objective=self.internal_rewards,
        )
        self.assertEqual(len(self.memory.tail(2)), 1)
        self.memory.append(
            muscle_uid=str(__name__) + "_2",
            sensor_readings=self.observations2,
            actuator_setpoints=self.actions2,
            rewards=self.rewards2,
            objective=self.internal_rewards2,
        )
        self.assertEqual(len(self.memory.tail(2)), 2)
        self.memory.append(
            muscle_uid=str(__name__) + "_1",
            sensor_readings=self.observations2,
            actuator_setpoints=self.actions2,
            rewards=self.rewards2,
            objective=self.internal_rewards2,
        )
        tail = self.memory.tail(2)
        tail_obs = tail.sensor_readings["observation_1"]
        self.assertEqual(len(tail), 2)
        self.assertEqual([3, 3], list(tail_obs))

    def test_truncate(self):
        self.memory.append(
            "mus",
            rewards=self.rewards,
            actuator_setpoints=self.actions,
            sensor_readings=self.observations,
            objective=self.internal_rewards,
        )
        self.memory.append(
            "mus",
            rewards=self.rewards2,
            actuator_setpoints=self.actions2,
            sensor_readings=self.observations2,
            objective=self.internal_rewards2,
        )
        self.memory.truncate(1)
        self.assertEqual(
            self.memory.tail(1).sensor_readings["observation_1"].iloc[0], 3
        )

    def test_auto_truncate(self):
        size_limit = 10_000
        self.memory.size_limit = size_limit
        for i in range(size_limit + 10):
            if i % 2 == 0:
                self.memory.append(
                    "mus0",
                    rewards=self.rewards,
                    actuator_setpoints=self.actions,
                    sensor_readings=self.observations,
                    objective=self.internal_rewards,
                )
            else:
                self.memory.append(
                    "mus1",
                    rewards=self.rewards2,
                    actuator_setpoints=self.actions2,
                    sensor_readings=self.observations2,
                    objective=self.internal_rewards2,
                )
                tail = self.memory.tail(2)
        self.assertEqual(len(self.memory), size_limit)
        self.memory.append(
            "mus2",
            rewards=self.rewards2,
            actuator_setpoints=self.actions2,
            sensor_readings=self.observations2,
            objective=self.internal_rewards2,
        )
        tail = self.memory.tail(2)
        tail_obs = tail.sensor_readings["observation_1"]
        self.assertEqual(len(tail), 2)
        self.assertEqual([3, 3], list(tail_obs))

    def test_len(self):
        self.memory.append(
            "test muscle",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
            objective=np.array([23.0]),
        )
        self.memory.append(
            "test muscle",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
            objective=np.array([24.0]),
        )
        self.assertEqual(2, len(self.memory))
        self.memory.append(
            "another muscle",
            sensor_readings=self.observations2,
            actuator_setpoints=self.actions2,
            rewards=self.rewards2,
            objective=np.array([24.0]),
        )
        self.assertEqual(3, len(self.memory))

    def test_add_lagging(self):
        self.memory.append(
            "mus1",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
        )
        self.memory.append(
            "mus1",
            rewards=self.rewards,
        )
        tail = self.memory.tail(1)
        self.assertEqual(1, len(tail))
        self.memory.append("mus1", objective=self.internal_rewards)
        tail = self.memory.tail(1)
        self.assertEqual(1, len(tail))
        self.memory.append(
            "mus2",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
        )
        self.memory.append(
            "mus1",
            sensor_readings=self.observations2,
            actuator_setpoints=self.actions2,
            rewards=self.rewards2,
        )
        self.memory.append("mus2", objective=self.internal_rewards)
        self.memory.append("mus1", objective=self.internal_rewards2)
        tail = self.memory.tail(2)
        self.assertEqual(2, len(tail))
        npt.assert_array_equal(
            np.concatenate([self.internal_rewards, self.internal_rewards2]),
            tail.objective,
        )

    def test_empty_tail_on_environment_baseline(self):
        self.memory.append(
            "some_muscle",
            sensor_readings=None,
            actuator_setpoints=None,
            rewards=None,
            objective=np.array([0.0]),
            done=False,
        )
        m = self.memory.tail(1)
        self.assertEqual(len(m), 0)
        self.memory.append(
            "some_muscle",
            sensor_readings=self.observations,
            actuator_setpoints=self.actions,
            rewards=self.rewards,
            objective=np.array([-10000.0]),
            done=True,
        )
        tail = self.memory.tail(1)
        self.assertEqual(len(tail), 1)
        self.assertEqual(tail.dones[-1], True)

    def test_MM_infos_to_df(self):
        s = [
            SensorInformation(
                np.array(1.2, dtype=np.float32),
                Box(
                    low=np.array(0.0, dtype=np.float32),
                    high=np.array(2.0, dtype=np.float32),
                    shape=(),
                    dtype=np.float32,
                ),
                "s_1",
            )
        ]
        s_pd = _MuscleMemory._infos_to_df(s)
        # The former implementation only wrapped the information values into
        # plain python lists, but pandas then interprets s_pd_values.dtype
        # as object (or rather dtype('0'))
        self.assertEqual(s_pd.values.dtype, np.float32)
        # This has to work (for e.g. the gauss function), since the former
        # implementation raised
        # 'TypeError: loop of ufunc does not support argument 0 of type
        # numpy.ndarray which has no callable exp method'
        np.exp(s_pd)

    def test_tail_filter(self):
        self.memory.append(
            "mus-1",
            rewards=self.rewards,
            actuator_setpoints=self.actions,
            sensor_readings=self.observations,
            objective=self.internal_rewards,
        )
        self.memory.append(
            "mus-2",
            rewards=self.rewards2,
            actuator_setpoints=self.actions2,
            sensor_readings=self.observations2,
            objective=self.internal_rewards2,
        )
        shard = self.memory.tail(1, include_only=["mus-1"])
        self.assertEqual(len(shard), 1)
        npt.assert_array_equal(self.internal_rewards, shard.objective)
