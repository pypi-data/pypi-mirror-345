import unittest

import numpy as np
from palaestrai.agent import ActuatorInformation
from palaestrai.types import Box, Discrete, MultiBinary, MultiDiscrete, Tuple
from palaestrai.util.exception import OutOfActionSpaceError


class TestActuatorInformation(unittest.TestCase):
    def setUp(self):
        self.test_box1 = Box(0.0, 10.0, shape=(1,), dtype=np.float64)
        self.test_box2 = Box(
            low=np.array([0.0, -10.0]),
            high=np.array([1.0, 0.0]),
            dtype=np.float64,
        )
        self.test_box3 = Box(
            low=-1.0, high=2.0, shape=(3, 4), dtype=np.float64
        )
        self.test_discrete = Discrete(10)
        self.test_multidiscrete = MultiDiscrete([5, 4, 2])
        self.test_multibinary = MultiBinary(3)

    def test_call_actuator(self):
        act = ActuatorInformation(
            value=np.array([2.0], dtype=np.float64),
            space=self.test_box1,
            uid="Test",
        )
        act([5.0])

        val = act.value
        self.assertIsInstance(val, list)
        self.assertEqual(val, [5.0])

    def test_set_one_dim_box(self):
        act = ActuatorInformation(
            value=np.array([5.0], dtype=np.float64),
            space=self.test_box1,
            uid="Test",
        )

        # Not contained within the space
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [15.0]

        # Wrong dimensions
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [5, 5]

        act.value = [5.0]
        self.assertIsInstance(act.value, list)
        self.assertEqual(act.value, [5.0])

    def test_set_two_dim_box(self):
        act = ActuatorInformation(
            value=np.array([0.0, -10.0], dtype=np.float64),
            space=self.test_box2,
            uid="Test",
        )

        # Wrong dimensions
        with self.assertRaises(OutOfActionSpaceError):
            act.value = 0.5

        # Not within the space
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [-1, -5]

        act.value = [0, -10]
        self.assertIsInstance(act.value, list)

    def test_set_multi_dim_box(self):
        act = ActuatorInformation(
            value=self.test_box3.sample(), space=self.test_box3, uid="Test"
        )

        # Wrong dimensions
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [0.0]

        # Not within the space
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [-2.0, 0.0, 0.0, 0.0],
            ]

        act.value = [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ]
        self.assertIsInstance(act.value, list)
        for sublist in act.value:
            self.assertIsInstance(sublist, list)
            for val in sublist:
                self.assertIsInstance(val, float)

    def test_set_discrete(self):
        act = ActuatorInformation(
            value=self.test_discrete.sample(),
            space=self.test_discrete,
            uid="Test",
        )

        # Wrong dimensions
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [5, 5]

        # Not within the space
        with self.assertRaises(OutOfActionSpaceError):
            act.value = -1

        # Wrong dtype
        with self.assertRaises(OutOfActionSpaceError):
            act.value = 5.0

        act.value = 5

    def test_set_multi_discrete(self):
        act = ActuatorInformation(
            self.test_multidiscrete.sample(), self.test_multidiscrete, "Test"
        )

        # Wrong dimensions
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [1, 1]

        # Not within the space
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [5, 4, 3]

        act.value = [1, 1, 1]
        self.assertIsInstance(act.value, list)
        for val in act.value:
            self.assertIsInstance(val, int)

    def test_set_multi_binary(self):
        act = ActuatorInformation(
            self.test_multibinary.sample(), self.test_multibinary, "Test"
        )

        with self.assertRaises(OutOfActionSpaceError):
            act.value = [1, 1]
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [1, 1, 0, 0]

        # Not within the space
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [0, 1, 2]

        act.value = [0, 0.0, 1.0]
        act.value = [0, 1, 0]

    def test_set_tuple(self):
        act = ActuatorInformation(
            Tuple(
                [self.test_box2, self.test_discrete, self.test_multibinary]
            ).sample(),
            Tuple([self.test_box2, self.test_discrete, self.test_multibinary]),
            "Test",
        )

        # Wrong dimensions
        with self.assertRaises(OutOfActionSpaceError):
            act.value = [-10, -5]

        # Not within the space

        with self.assertRaises(OutOfActionSpaceError):
            act.value = [[0, -5], 5, [0, 1, 0], [1.0]]

        # This should work that is why there is not 'raises'-check
        act.value = [[0, -5], 5, [0, 1, 0]]


if __name__ == "__main__":
    unittest.main()
