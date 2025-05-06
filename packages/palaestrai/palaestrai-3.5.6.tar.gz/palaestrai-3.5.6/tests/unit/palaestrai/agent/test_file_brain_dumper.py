import io
import sys
import unittest
import unittest.mock as um

from palaestrai.agent import (
    DummyBrain,
    DummyObjective,
    BrainLocation,
    BrainDumper,
    FileBrainDumper,
)
from palaestrai.core import RuntimeConfig


class FileBrainDumperTest(unittest.TestCase):
    def setUp(self) -> None:
        self._brain = DummyBrain()
        self._brain_src = BrainLocation(
            agent_name="DummyAgent",
            experiment_run_uid="DummyExperimentRun",
            experiment_run_phase=0,
        )
        self._brain_dst = BrainLocation(
            agent_name="NewDummyAgent",
            experiment_run_uid="NewDummyExperimentRun",
            experiment_run_phase=0,
        )
        _ = RuntimeConfig()  # Avoid conflicts with mock_open

    @um.patch("pathlib.Path.mkdir")
    @um.patch(
        "builtins.open",
        new_callable=um.mock_open,
        read_data=(0xDEADBEEF).to_bytes(4, sys.byteorder),
    )
    def test_loads(self, mockopen, mock_mkdir):
        fbd = FileBrainDumper(
            dump_to=self._brain_dst, load_from=self._brain_src
        )
        val = fbd.load()
        self.assertTrue(mockopen.called)
        self.assertEqual(0xDEADBEEF, int.from_bytes(val.read(), sys.byteorder))

    @um.patch("pathlib.Path.mkdir")
    @um.patch(
        "builtins.open",
        new_callable=um.mock_open,
        read_data=(0xDEADBEEF).to_bytes(4, sys.byteorder),
    )
    def test_load_from_brain_dumper(self, mockopen, mock_mkdir):
        fbd = FileBrainDumper(
            dump_to=self._brain_dst, load_from=self._brain_src
        )
        val = BrainDumper.load_brain_dump([fbd])
        self.assertTrue(mockopen.called)
        self.assertEqual(0xDEADBEEF, int.from_bytes(val.read(), sys.byteorder))
        self.assertIn(
            f"/{self._brain_src.experiment_run_uid}"
            f"/{self._brain_src.experiment_run_phase}"
            f"/{self._brain_src.agent_name}.",
            mockopen.call_args[0][0],
        )

    @um.patch("pathlib.Path.mkdir")
    @um.patch(
        "builtins.open",
        new_callable=um.mock_open,
        read_data=(0xDEADBEEF).to_bytes(4, sys.byteorder),
    )
    def test_stores(self, mockopen, mock_mkdir):
        fbd = FileBrainDumper(
            dump_to=self._brain_dst, load_from=self._brain_src
        )
        fbd.save(io.BytesIO(b"foo"))
        self.assertTrue(mockopen.called)
        self.assertTrue(mock_mkdir.called)
        self.assertIn(
            f"/{self._brain_dst.experiment_run_uid}"
            f"/{self._brain_dst.experiment_run_phase}"
            f"/{self._brain_dst.agent_name}.",
            mockopen.call_args[0][0],
        )

    @um.patch("pathlib.Path.mkdir")
    @um.patch(
        "builtins.open",
        new_callable=um.mock_open,
        read_data=(0xDEADBEEF).to_bytes(4, sys.byteorder),
    )
    def test_stores_tagged(self, mockopen, mock_mkdir):
        fbd = FileBrainDumper(
            dump_to=self._brain_dst, load_from=self._brain_src
        )
        fbd.save(io.BytesIO(b"foo"), tag="Quux")
        self.assertTrue(mock_mkdir.called)
        self.assertTrue(mockopen.called)
        self.assertIn(
            f"/{self._brain_dst.experiment_run_uid}"
            f"/{self._brain_dst.experiment_run_phase}"
            f"/{self._brain_dst.agent_name}-Quux.",
            mockopen.call_args[0][0],
        )


if __name__ == "main":
    unittest.main()
