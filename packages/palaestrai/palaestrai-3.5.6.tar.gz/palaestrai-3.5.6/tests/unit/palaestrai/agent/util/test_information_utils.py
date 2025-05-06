import unittest

import numpy as np

from palaestrai.agent import (
    SensorInformation,
    ActuatorInformation,
)
from palaestrai.agent.util.information_utils import (
    concat_flattened_values,
    concat_flattened_act_scale_bias,
)
from palaestrai.types import Box, Discrete


class TestActuatorInformation(unittest.IsolatedAsyncioTestCase):
    def test_concat_flattened_values(self):
        sensors = [
            SensorInformation(
                value=np.array([0.8], dtype=np.float32),
                space=Box(low=[-1], high=[1], dtype=np.float32),
                uid="s1",
            ),
            SensorInformation(
                value=np.array(np.array(7.35), dtype=np.float32),
                space=Box(low=0, high=10, shape=(), dtype=np.float32),
                uid="s2",
            ),
            SensorInformation(value=np.array(3), space=Discrete(4), uid="s3"),
            SensorInformation(
                value=np.array(
                    [[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]],
                    dtype=np.float32,
                ),
                space=Box(low=0, high=10, shape=(2, 2, 2), dtype=np.float32),
                uid="s4",
            ),
        ]
        self.assertEqual(sensors[1].space.shape, ())
        values = concat_flattened_values(sensors)
        for value in zip(
            values, [0.8, 7.35, 3.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        ):
            self.assertAlmostEqual(*value, delta=0.001)

    def test_concat_flattened_act_scale_bias(self):
        actuators = [
            ActuatorInformation(
                value=np.array([0.8], dtype=np.float32),
                space=Box(low=[-1], high=[1], dtype=np.float32),
                uid="a1",
            ),
            ActuatorInformation(
                value=np.array([[0.8], [1.2]], dtype=np.float32),
                space=Box(low=[[-1], [-2]], high=[[1], [3]], dtype=np.float32),
                uid="a2",
            ),
        ]

        act_scales = concat_flattened_act_scale_bias(actuators, np.subtract)
        for value in zip(act_scales, [1.0, 1.0, 2.5]):
            self.assertAlmostEqual(*value, delta=0.001)


if __name__ == "__main__":
    unittest.main()
