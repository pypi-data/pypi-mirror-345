import unittest
import jsonpickle
import numpy as np

from palaestrai.agent import (
    SensorInformation,
)
from palaestrai.types import Discrete, Box


class TestSensorInformation(unittest.IsolatedAsyncioTestCase):
    def test_lazy_constructor(self):
        value = 1
        space = Discrete(3)
        uid = "S1"
        sensor_information = SensorInformation(value, space, uid)

        self.assertEqual(sensor_information.value, value)
        self.assertEqual(sensor_information.space, space)
        self.assertEqual(sensor_information.uid, uid)

    def test_sensor_id(self):
        uid = "S1"
        sensor_information = SensorInformation(
            value=1, space=Discrete(3), sensor_id=uid
        )
        self.assertEqual(sensor_information.uid, uid)
        self.assertEqual(sensor_information._uid, uid)

        uid = "S2"
        sensor_information.sensor_id = uid

        self.assertEqual(sensor_information.uid, uid)
        self.assertEqual(sensor_information._uid, uid)

    def test_id(self):
        uid = "S1"
        other_uid = "S2"
        sensor_information = SensorInformation(
            value=1, space=Discrete(3), uid=uid
        )
        sensor_information.id = other_uid

        self.assertEqual(sensor_information.uid, other_uid)
        self.assertEqual(sensor_information._uid, other_uid)

    def test_observation_space(self):
        space = Discrete(3)
        sensor_information = SensorInformation(
            value=1, observation_space=space, uid="S1"
        )

        self.assertEqual(sensor_information.space, space)
        self.assertEqual(sensor_information._space, space)

        space = Discrete(2)
        sensor_information.observation_space = space

        self.assertEqual(sensor_information.space, space)
        self.assertEqual(sensor_information._space, space)

    def test_sensor_value(self):
        value = 1
        sensor_information = SensorInformation(
            sensor_value=value, space=Discrete(4), uid="S1"
        )

        self.assertEqual(sensor_information.value, value)
        self.assertEqual(sensor_information._value, value)

        value = 1
        sensor_information.sensor_value = value

        self.assertEqual(sensor_information.value, value)
        self.assertEqual(sensor_information._value, value)

    def test_serializes_to_json(self):
        jsonpickle.set_preferred_backend("simplejson")
        si = SensorInformation(
            value=np.array([1.0], dtype=np.float32),
            space=Box(low=[-2.0], high=[2.0]),
            uid="S1",
        )
        s = jsonpickle.dumps(si)
        self.assertIn('"value": [1.0]', s)
        si_restored = jsonpickle.loads(s)
        self.assertEqual(si_restored, si)


if __name__ == "__main__":
    unittest.main()
