import unittest
from unittest.mock import AsyncMock

from palaestrai.experiment.executor import Executor


class ExecutorTest(unittest.IsolatedAsyncioTestCase):
    async def test_starts_only_one_experiment_at_a_time(self):
        executor = Executor()
        executor._deploy_experiment_run = AsyncMock(side_effect=RuntimeError())
        await executor._try_start_next_scheduled_experiment()
        executor._deploy_experiment_run.assert_not_awaited()
        executor._runs_scheduled = [1, 2, 3]
        with self.assertRaises(RuntimeError):
            await executor._try_start_next_scheduled_experiment()
        executor._deploy_experiment_run = AsyncMock(side_effect=RuntimeError())
        executor._run_governors[123] = True
        await executor._try_start_next_scheduled_experiment()
        executor._deploy_experiment_run.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
