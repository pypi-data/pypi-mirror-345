import unittest
from io import BytesIO
from tempfile import TemporaryDirectory

import sqlalchemy as sa

import palaestrai.store.database_model as dbm
from palaestrai.agent import StoreBrainDumper, BrainLocation, NoBrainFoundError
from palaestrai.core import RuntimeConfig
from palaestrai.store import Session
from palaestrai.store.database_util import setup_database


class StoreBrainDumperTest(unittest.TestCase):
    @staticmethod
    def _create_dummy_db_data(dbh):
        ex = dbm.Experiment(name="Dummy Experiment")

        er = dbm.ExperimentRun(uid="Dummy Experiment Run", hash="0xcafe")
        ex.experiment_runs.append(er)

        eri = dbm.ExperimentRunInstance(uid="ExpermentRunInstance-0")
        er.experiment_run_instances.append(eri)

        erp = dbm.ExperimentRunPhase(
            uid="Phase-0",
            number=0,
        )
        eri.experiment_run_phases.append(erp)

        ag = dbm.Agent(
            uid="0xdecafe",
            name="Mighty Agent 123",
            muscles=["Muscle-0"],
        )
        erp.agents.append(ag)

        er = dbm.ExperimentRun(uid="Interphasic Experiment Run")
        ex.experiment_runs.append(er)

        eri = dbm.ExperimentRunInstance(uid="ExpermentRunInstance-47")
        er.experiment_run_instances.append(eri)

        erp = dbm.ExperimentRunPhase(
            uid="Assimilation Phase",
            number=8472,
        )
        eri.experiment_run_phases.append(erp)

        ag = dbm.Agent(
            uid="8472",
            name="Species 8472",
            muscles=["Bioship"],
        )
        erp.agents.append(ag)

        dbh.add(ex)
        dbh.commit()

    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.store_path = f"{self.tempdir.name}/palaestrai.db"
        self.store_uri = f"sqlite:///{self.store_path}"
        RuntimeConfig().reset()
        RuntimeConfig().load({"store_uri": self.store_uri})
        setup_database(self.store_uri)
        self.dbh = Session()
        StoreBrainDumperTest._create_dummy_db_data(self.dbh)
        self.brain_dumper = StoreBrainDumper(
            dump_to=BrainLocation(
                agent_name="Mighty Agent 123",
                experiment_run_uid="Dummy Experiment Run",
                experiment_run_phase=0,
            ),
            load_from=BrainLocation(
                agent_name="Species 8472",
                experiment_run_uid="Interphasic Experiment Run",
                experiment_run_phase=8472,
            ),
        )

    def test_stores(self):
        brain_state = b"424723"
        self.brain_dumper.save(BytesIO(brain_state))
        try:
            record = self.dbh.execute(sa.select(dbm.BrainState)).one()
        except Exception as e:
            self.fail(e)
        state = record[dbm.BrainState].state
        self.assertIsNotNone(state)
        self.assertEqual(state, brain_state)

    def test_loads(self):
        sbd = StoreBrainDumper(dump_to=self.brain_dumper._brain_source)
        brain_state = b"424723"
        sbd.save(BytesIO(brain_state), "specimen")
        bio = self.brain_dumper.load("specimen")
        self.assertEqual(bio.read(), brain_state)
        self.assertRaises(NoBrainFoundError, self.brain_dumper.load)


if __name__ == "__main__":
    unittest.main()
