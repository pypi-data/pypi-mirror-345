import unittest
import jsonpickle

from palaestrai.agent import (
    ActuatorInformation,
)
from palaestrai.types import Discrete
from palaestrai.util.exception import OutOfActionSpaceError


class TestActuatorInformation(unittest.IsolatedAsyncioTestCase):
    def test_lazy_constructor(self):
        value = 1
        space = Discrete(2)
        uid = "S1"
        actuator_information = ActuatorInformation(value, space, uid)

        self.assertEqual(actuator_information.value, value)
        self.assertEqual(actuator_information.space, space)
        self.assertEqual(actuator_information.uid, uid)

    def test_actuator_id(self):
        uid = "S1"
        actuator_information = ActuatorInformation(
            value=1, space=Discrete(2), actuator_id=uid
        )
        self.assertEqual(actuator_information.uid, uid)
        self.assertEqual(actuator_information._uid, uid)

        uid = "S2"
        actuator_information.actuator_id = uid

        self.assertEqual(actuator_information.uid, uid)
        self.assertEqual(actuator_information._uid, uid)

    def test_id(self):
        uid = "S1"
        other_uid = "S2"
        actuator_information = ActuatorInformation(
            value=1, space=Discrete(2), uid=uid
        )
        actuator_information.id = other_uid

        self.assertEqual(actuator_information.uid, other_uid)
        self.assertEqual(actuator_information._uid, other_uid)

    def test_action_space(self):
        space = Discrete(2)
        actuator_information = ActuatorInformation(
            value=1, action_space=space, uid="S1"
        )

        self.assertEqual(actuator_information.space, space)
        self.assertEqual(actuator_information._space, space)

        space = Discrete(3)
        actuator_information.action_space = space

        self.assertEqual(actuator_information.space, space)
        self.assertEqual(actuator_information._space, space)

    def test_setpoint(self):
        value = 1
        actuator_information = ActuatorInformation(
            setpoint=value, space=Discrete(2), uid="S1"
        )

        self.assertEqual(actuator_information.value, value)
        self.assertEqual(actuator_information._value, value)

        value = 1
        actuator_information.setpoint = value

        self.assertEqual(actuator_information.value, value)
        self.assertEqual(actuator_information._value, value)

    def test_value_in_space(self):
        with self.assertRaises(OutOfActionSpaceError):
            ActuatorInformation(value=1, space=Discrete(1), uid="S1")

        actuator_information = ActuatorInformation(
            value=1, space=Discrete(2), uid="S1"
        )

        with self.assertRaises(OutOfActionSpaceError):
            actuator_information.space = Discrete(1)

        with self.assertRaises(OutOfActionSpaceError):
            actuator_information.action_space = Discrete(1)

        with self.assertRaises(OutOfActionSpaceError):
            actuator_information.value = 2

        with self.assertRaises(OutOfActionSpaceError):
            actuator_information.setpoint = 2

    def test_serializes_to_json(self):
        jsonpickle.set_preferred_backend("simplejson")
        actuator_information = ActuatorInformation(
            value=1, space=Discrete(2), uid="S1"
        )
        s = jsonpickle.dumps(actuator_information)
        self.assertIn('"value": 1', s)
        ai_restored = jsonpickle.loads(s)
        self.assertEqual(ai_restored, actuator_information)


if __name__ == "__main__":
    unittest.main()
