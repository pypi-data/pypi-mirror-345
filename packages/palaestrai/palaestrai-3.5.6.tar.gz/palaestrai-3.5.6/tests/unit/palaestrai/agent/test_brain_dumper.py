import unittest
from io import BytesIO
from unittest.mock import Mock

from palaestrai.agent.brain_dumper import BrainDumper


class BrainDumperTest(unittest.TestCase):
    def test_uses_first_good_loader(self):
        pseudo_brain_dump = BytesIO(b"47")
        loaders = [
            Mock(load=Mock(side_effect=RuntimeError("Expected Error"))),
            Mock(load=Mock(return_value=pseudo_brain_dump)),
            Mock(load=Mock(return_value=pseudo_brain_dump)),
        ]
        data = BrainDumper.load_brain_dump(loaders, "Foo")
        self.assertEqual(len(loaders[0].method_calls), 1)
        self.assertEqual(len(loaders[1].method_calls), 1)
        self.assertEqual(len(loaders[2].method_calls), 0)
        self.assertEqual(loaders[1].method_calls[0].args, ("Foo",))
        self.assertTrue(data.read(), b"47")

    def test_tries_all_dumpers(self):
        dumpers = [
            Mock(),
            Mock(side_effect=RuntimeError("Expected Error")),
            Mock(),
        ]
        pseudo_brain_dump = BytesIO(b"47")
        BrainDumper.store_brain_dump(
            brain_state=pseudo_brain_dump, dumpers=dumpers, tag="Foo"
        )
        self.assertTrue(all(len(d.method_calls) == 1 for d in dumpers))
        self.assertEqual(
            dumpers[2].method_calls[0].args, (pseudo_brain_dump, "Foo")
        )


if __name__ == "__main__":
    unittest.main()
