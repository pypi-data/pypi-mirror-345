import unittest
import jsonpickle
import numpy as np

from palaestrai.agent import (
    RewardInformation,
)
from palaestrai.types import Discrete, Box


class TestRewardInformation(unittest.IsolatedAsyncioTestCase):
    def test_lazy_constructor(self):
        value = 1
        space = Discrete(42)
        uid = "S1"
        reward_information = RewardInformation(value, space, uid)

        self.assertEqual(reward_information.value, value)
        self.assertEqual(reward_information.space, space)
        self.assertEqual(reward_information.uid, uid)

    def test_reward_id(self):
        uid = "S1"
        reward_information = RewardInformation(
            value=1, space=Discrete(42), reward_id=uid
        )
        self.assertEqual(reward_information.uid, uid)

        uid = "S2"
        reward_information.reward_id = uid

        self.assertEqual(reward_information.uid, uid)

    def test_id(self):
        uid = "S1"
        other_uid = "S2"
        reward_information = RewardInformation(
            value=1, space=Discrete(47), uid=uid
        )
        reward_information.uid = other_uid

        self.assertEqual(reward_information.uid, other_uid)
        self.assertEqual(reward_information._uid, other_uid)

    def test_observation_space(self):
        space = Discrete(42)
        reward_information = RewardInformation(
            value=1, observation_space=space, uid="S1"
        )

        self.assertEqual(reward_information.space, space)
        self.assertEqual(reward_information._space, space)

        space = Discrete(23)
        reward_information.observation_space = space

        self.assertEqual(reward_information.space, space)
        self.assertEqual(reward_information._space, space)

    def test_reward_value(self):
        value = 1
        reward_information = RewardInformation(
            reward_value=value, space=Discrete(47), uid="S1"
        )

        self.assertEqual(reward_information.value, value)
        self.assertEqual(reward_information._value, value)

        value = 1
        reward_information.value = value

        self.assertEqual(reward_information.value, value)
        self.assertEqual(reward_information._value, value)

    def test_serializes_to_json(self):
        jsonpickle.set_preferred_backend("simplejson")
        si = RewardInformation(
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
