from unittest.async_case import IsolatedAsyncioTestCase

from palaestrai.agent import (
    DummyMuscle,
)


class TestMuscle(IsolatedAsyncioTestCase):
    def setUp(self):
        pass

    async def test_statistics_handling(self):
        self.muscle: DummyMuscle = DummyMuscle()
        self.muscle._uid = "muscle-id"

        self.assertEqual(len(self.muscle._statistics), 0)

        self.muscle.add_statistics("metric1", 1)
        self.muscle.add_statistics("metric2", 1.5)
        self.assertEqual(len(self.muscle._statistics), 2)

        statistics_dict = self.muscle.pop_statistics()
        self.assertDictEqual(
            statistics_dict,
            {
                "metric1": 1,
                "metric2": 1.5,
            },
        )

        self.assertEqual(len(self.muscle._statistics), 0)

    async def test_not_overwriting_statistics(self):
        self.muscle: DummyMuscle = DummyMuscle()
        self.muscle._uid = "muscle-id"

        self.muscle.add_statistics("metric1", 1)
        self.assertRaises(
            AssertionError, self.muscle.add_statistics, "metric1", 1
        )

    async def test_overwriting_statistics(self):
        self.muscle: DummyMuscle = DummyMuscle()
        self.muscle._uid = "muscle-id"

        self.assertEqual(len(self.muscle._statistics), 0)

        self.muscle.add_statistics("metric1", 1)
        self.muscle.add_statistics("metric1", 2, allow_overwrite=True)
        self.assertEqual(len(self.muscle._statistics), 1)

        statistics_dict = self.muscle.pop_statistics()
        self.assertDictEqual(
            statistics_dict,
            {
                "metric1": 2,
            },
        )

        self.assertEqual(len(self.muscle._statistics), 0)

    async def test_wrong_key_statistics(self):
        self.muscle: DummyMuscle = DummyMuscle()
        self.muscle._uid = "muscle-id"

        # Key must be of type str
        self.assertRaises(AssertionError, self.muscle.add_statistics, 1, 1)
        self.assertRaises(AssertionError, self.muscle.add_statistics, None, 1)

    async def test_wrong_internal_statistics_variable(self):
        self.muscle: DummyMuscle = DummyMuscle()
        self.muscle._uid = "muscle-id"

        # If overwriting (type of) internal _statistics variable (to None),
        # adding statistics will fail.
        self.muscle._statistics = None
        self.assertRaises(
            AssertionError, self.muscle.add_statistics, "metric1", 1
        )

        # But it should work if (resetting it)
        self.muscle._statistics = {}
        self.muscle.add_statistics("metric1", 1)

        # If overwriting (type of) internal _statistics variable (other than
        # Dict), adding statistics will fail.
        self.muscle._statistics = []
        self.assertRaises(
            AssertionError, self.muscle.add_statistics, "metric1", 1
        )

        # But it should work if (resetting it)
        self.muscle._statistics = {}
        self.muscle.add_statistics("metric1", 1)
