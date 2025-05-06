import unittest

from palaestrai.environment.dummy_environment import DummyEnvironment


class DummyEnvironmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.env = DummyEnvironment(
            broker_uri="test://uri",
            uid=str(__name__),
            seed=123,
            discrete=True,
        )
        self.env.start_environment()

    def test_iteration(self):
        for _ in range(9):
            self.assertNotEqual(
                True,
                self.env.update(self.env.actuators)[2],
                "Environment terminated unexpectedly",
            )
        self.assertEqual(
            True,
            self.env.update(self.env.actuators)[2],
            "Environment did not terminate on time",
        )


if __name__ == "__main__":
    unittest.main()
