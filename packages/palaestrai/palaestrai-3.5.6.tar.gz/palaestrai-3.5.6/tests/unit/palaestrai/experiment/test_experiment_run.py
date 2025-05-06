import io
import os.path
import sys
import unittest
import uuid
from copy import deepcopy
from unittest.mock import MagicMock, patch
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

from importlib.metadata import (
    version as importlib_version,
)  # had to be renamed because else it would clash with the ExperimentRun class version

from palaestrai.experiment.experiment_run import ExperimentRun
from palaestrai.util.exception import EnvironmentHasNoUIDError


class _UidentifiableMock(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = str(uuid.uuid4())
        self.args = args
        self.kwargs = kwargs


def load_with_params_side_effect(*args, **kwargs):
    return _UidentifiableMock(*args, **kwargs)


class FourtyTwoStateTransformer:
    pass


@patch(
    "palaestrai.experiment.experiment_run.AgentConductor",
    MagicMock(side_effect=load_with_params_side_effect),
)
@patch(
    "palaestrai.experiment.experiment_run.load_with_params",
    MagicMock(side_effect=load_with_params_side_effect),
)
class TestExperimentRun(unittest.TestCase):
    def setUp(self):
        self.version = importlib_version("palaestrai")
        self.dummy_exp_path = os.path.realpath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "../../../fixtures/dummy_run.yml",
            )
        )
        self.invalid_exp_path = os.path.realpath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "../../../fixtures/invalid_run.yml",
            )
        )
        self.schedule = [
            {
                "phase_0": {
                    "environments": [
                        {
                            "environment": {
                                "name": "palaestrai.environment:DummyEnvironment",
                                "uid": "myenv",
                                "params": dict(),
                            },
                            # "reward": {"name": "", "params": dict()},
                        }
                    ],
                    "agents": [
                        {
                            "name": "defender",
                            "brain": {"name": "", "params": dict()},
                            "muscle": {"name": "", "params": dict()},
                            "objective": {"name": "", "params": dict()},
                            "sensors": list(),
                            "actuators": list(),
                        },
                        {
                            "name": "attacker",
                            "brain": {"name": "", "params": dict()},
                            "muscle": {"name": "", "params": dict()},
                            "objective": {"name": "", "params": dict()},
                            "sensors": list(),
                            "actuators": list(),
                        },
                    ],
                    "simulation": {
                        "name": "",
                        "params": dict(),
                        "conditions": [
                            {"name": "some:TC", "params": {}},
                            {
                                "name": "anotherTC",
                                "params": {"Humpty": "Dumpty"},
                            },
                        ],
                    },
                    "phase_config": {"mode": "train", "worker": 1},
                }
            }
        ]

        self.run_config = {
            "condition": {
                "name": (
                    "palaestrai.experiment:"
                    "VanillaRunGovernorTerminationCondition",
                ),
                "params": dict(),
            }
        }

        self.schedule_p2 = {
            "phase_1": {
                "environments": [
                    {
                        "environment": {
                            "name": "",
                            "uid": "myenv",
                            "params": dict(),
                        },
                    }
                ],
                "agents": [
                    {
                        "name": "defender",
                        "brain": {"name": "", "params": dict()},
                        "muscle": {"name": "", "params": dict()},
                        "objective": {"name": "", "params": dict()},
                        "sensors": list(),
                        "actuators": list(),
                    },
                ],
                "simulation": {
                    "name": "",
                    "params": dict(),
                    "conditions": list(),
                },
                "phase_config": {"mode": "test", "worker": 1},
            }
        }

        self.schedule_p2_simplified = {
            "phase_1": {
                "phase_config": {"mode": "test", "worker": 1},
            }
        }

        self.schedule_p3 = {
            "phase_1": {
                "environments": [
                    {
                        "environment": {
                            "name": "",
                            "uid": "myenv",
                            "params": dict(),
                        },
                    }
                ],
                "agents": [
                    {
                        "name": "attacker",
                        "brain": {"name": "", "params": dict()},
                        "muscle": {"name": "", "params": dict()},
                        "objective": {"name": "", "params": dict()},
                        "sensors": list(),
                        "actuators": list(),
                    },
                ],
                "simulation": {
                    "name": "some.nice:SC",
                    "params": dict(),
                    "conditions": list(),
                },
                "phase_config": {"mode": "train", "worker": 3},
            }
        }

        self.schedule_p4 = {
            "phase_2": {
                "agents": [
                    {
                        "name": "Warm_2x",
                        "brain": {"name": "", "params": dict()},
                        "muscle": {"name": "", "params": dict()},
                        "objective": {"name": "", "params": dict()},
                        "sensors": list(),
                        "actuators": list(),
                    },
                ],
                "simulation": {
                    "name": "",
                    "params": dict(),
                    "conditions": list(),
                },
                "phase_config": {"mode": "test", "worker": 1},
            }
        }

        self.schedule_p5 = {
            "phase_3": {
                "environments": [
                    {
                        "environment": {
                            "name": "",
                            "uid": "myenv_warm",
                            "params": dict(),
                        },
                    }
                ],
                "phase_config": {"mode": "test", "worker": 1},
            }
        }

    def test_properties(self):
        """Assert Not Empty list"""
        exp = ExperimentRun(
            uid="test_properties",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        self.assertFalse(hasattr(exp, "schedule"))

    def test_expand_config(self):
        """Assert config expansion"""
        self.schedule.append(self.schedule_p2_simplified)
        self.schedule.append(self.schedule_p4)
        self.schedule.append(self.schedule_p5)
        exp = ExperimentRun(
            uid="test_expansion_config",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )

        # schedule should not overwriten
        self.assertEqual(
            "defender",
            exp.canonical_config["schedule"][0]["phase_0"]["agents"][0][
                "name"
            ],
        )

        # schedule_p2_simplified expanded to canonical form regarding schedule
        self.assertEqual(
            "defender",
            exp.canonical_config["schedule"][1]["phase_1"]["agents"][0][
                "name"
            ],
        )

        # schedule_p2_simplified expanded to canonical form regarding schedule
        self.assertEqual(
            "myenv",
            exp.canonical_config["schedule"][1]["phase_1"]["environments"][0][
                "environment"
            ]["uid"],
        )

        # schedule_p4 expanded to canonical form regarding expanded form of schedule_2_simplified
        self.assertEqual(
            "myenv",
            exp.canonical_config["schedule"][2]["phase_2"]["environments"][0][
                "environment"
            ]["uid"],
        )

        # schedule_p4 agents not overwriten
        self.assertEqual(
            "Warm_2x",
            exp.canonical_config["schedule"][2]["phase_2"]["agents"][0][
                "name"
            ],
        )

        # schedule_p5 expanded to canonical form regarding expanded form of schedule_4
        self.assertEqual(
            "Warm_2x",
            exp.canonical_config["schedule"][3]["phase_3"]["agents"][0][
                "name"
            ],
        )

        # schedule_p5 expanded to canonical form regarding expanded form of schedule_4
        self.assertEqual(
            "myenv_warm",
            exp.canonical_config["schedule"][3]["phase_3"]["environments"][0][
                "environment"
            ]["uid"],
        )

    @patch("palaestrai.experiment.experiment_run.AgentConductor")
    @patch("palaestrai.experiment.experiment_run.EnvironmentConductor")
    def test__setup_agent_conductor(self, ecmock, acmock):
        er = ExperimentRun(
            uid="test_properties",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        er._setup_schedule("Ptoey")
        acs = er.agent_conductors(0)
        self.assertListEqual(
            list(acs.values())[0].agent_config["termination_conditions"],
            self.schedule[0]["phase_0"]["simulation"]["conditions"],
        )

    def test_setup_one_phase(self):
        """Assert setup"""
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        exp.setup(broker_uri=None)
        self.assertEqual(len(exp.schedule_config), len(exp.schedule))
        self.assertEqual(1, len(exp.environment_conductors(0)))
        self.assertEqual(2, len(exp.agent_conductors(0)))
        self.assertEqual(1, len(exp.simulation_controllers(0)))

    def test_setup_three_phase(self):
        self.schedule.append(self.schedule_p2)
        self.schedule.append(self.schedule_p3)
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        exp.setup(broker_uri=None)
        self.assertEqual(len(exp.schedule_config), len(exp.schedule))
        self.assertEqual(1, len(exp.environment_conductors(0)))
        self.assertEqual(2, len(exp.agent_conductors(0)))
        self.assertEqual(1, len(exp.simulation_controllers(0)))
        self.assertEqual(1, len(exp.environment_conductors(1)))

        # One agent was removed in phase 2
        self.assertEqual(1, len(exp.agent_conductors(1)))
        self.assertEqual(1, len(exp.simulation_controllers(1)))
        self.assertEqual(1, len(exp.environment_conductors(2)))
        self.assertEqual(1, len(exp.agent_conductors(2)))

        # Now we have three workers
        self.assertEqual(3, len(exp.simulation_controllers(2)))

    def test_single_env_has_no_uid_tc1(self):
        """This functions tests the behavior when a single environment
        has no UID.

        TestCase 1
        ----------
        A single environment that is used in two phases. The
        environment re-uses the definition from the first phase.

        Expected outcome
        ----------------
        Setup should fail.

        """
        s2p_single_env_p1_no_uid = [
            {
                "phase_0": {
                    "environments": [
                        {
                            "environment": {
                                "name": "",
                                "params": dict(),
                            },
                            # "reward": {"name": "", "params": dict()},
                        }
                    ],
                    "agents": [
                        {
                            "name": "defender",
                            "brain": {"name": "", "params": dict()},
                            "muscle": {"name": "", "params": dict()},
                            "objective": {"name": "", "params": dict()},
                            "sensors": list(),
                            "actuators": list(),
                        },
                        {
                            "name": "attacker",
                            "brain": {"name": "", "params": dict()},
                            "muscle": {"name": "", "params": dict()},
                            "objective": {"name": "", "params": dict()},
                            "sensors": list(),
                            "actuators": list(),
                        },
                    ],
                    "simulation": {
                        "name": "",
                        "params": dict(),
                        "conditions": list(),
                    },
                    "phase_config": {"mode": "train", "worker": 1},
                }
            },
            {
                "phase_1": {
                    "phase_config": {"mode": "test", "worker": 1},
                }
            },
        ]
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=s2p_single_env_p1_no_uid,
            run_config=self.run_config,
        )
        self.assertRaises(EnvironmentHasNoUIDError, exp.setup, broker_uri=None)

        # We are happy if no exception is raised and don't need an
        # assert here.

    def test_single_env_has_no_uid_tc2(self):
        """This functions tests the behavior when a single environment
        has no UID.

        TestCase 2
        ----------
        A single environment that is used in two phases. However, in
        the definition of the second phase, the UID is missing.

        Expected outcome
        ----------------
        Setup should fail. The connection between the environment in
        the first phase and the environment in the second phase is
        purely on a semantical level. PalaestrAI can't know that those
        are identically (they're probably not, why else is there a
        second definition?).

        """
        s2p_single_env_p1_uid_p2_no_uid = [
            {
                "phase_0": {
                    "environments": [
                        {
                            "environment": {
                                "name": "",
                                "uid": "myenv",
                                "params": dict(),
                            },
                            # "reward": {"name": "", "params": dict()},
                        }
                    ],
                    "agents": [
                        {
                            "name": "defender",
                            "brain": {"name": "", "params": dict()},
                            "muscle": {"name": "", "params": dict()},
                            "objective": {"name": "", "params": dict()},
                            "sensors": list(),
                            "actuators": list(),
                        },
                        {
                            "name": "attacker",
                            "brain": {"name": "", "params": dict()},
                            "muscle": {"name": "", "params": dict()},
                            "objective": {"name": "", "params": dict()},
                            "sensors": list(),
                            "actuators": list(),
                        },
                    ],
                    "simulation": {
                        "name": "",
                        "params": dict(),
                        "conditions": list(),
                    },
                    "phase_config": {"mode": "train", "worker": 1},
                }
            },
            {
                "phase_1": {
                    "environments": [
                        {"environment": {"name": "", "params": dict()}}
                    ]
                }
            },
        ]
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=s2p_single_env_p1_uid_p2_no_uid,
            run_config=self.run_config,
        )
        self.assertRaises(EnvironmentHasNoUIDError, exp.setup, broker_uri=None)

    def test_multi_env_has_no_uid(self):
        pass

    def test_load_from_file(self):
        exp = ExperimentRun.load(self.dummy_exp_path)
        self.assertFalse(hasattr(exp, "schedule"))

    def test_load_from_stream(self):
        with open(self.dummy_exp_path, "r") as stream_:
            exp = ExperimentRun.load(stream_)

        self.assertFalse(hasattr(exp, "schedule"))

    def test_subseeds_are_reproducible(self):
        exp1 = ExperimentRun(
            uid="test_properties",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        exp2 = ExperimentRun(
            uid="test_properties",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )

        for i in range(10):
            sub_seed1 = exp1.create_subseed()
            sub_seed2 = exp2.create_subseed()
            self.assertEqual(sub_seed1, sub_seed2)

    def test_subseeds_from_None_not_equal(self):
        exp1 = ExperimentRun(
            uid="test_properties",
            seed=None,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        exp2 = ExperimentRun(
            uid="test_properties",
            seed=None,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        list1 = []
        list2 = []
        for i in range(10):
            sub_seed1 = exp1.create_subseed()
            list1.append(sub_seed1)
            sub_seed2 = exp2.create_subseed()
            list2.append(sub_seed2)
        self.assertFalse(set(list1) == set(list2))

    def test_subseeds_from_None(self):
        exp1 = ExperimentRun(
            uid="test_properties",
            seed=None,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        list1 = []
        for i in range(10):
            sub_seed1 = exp1.create_subseed()
            list1.append(sub_seed1)
        self.assertTrue(len(list1) == 10)

    def test_load_from_stringio(self):
        with open(self.dummy_exp_path, "r") as stream_:
            experiment_run_document = stream_.read()
        sio = io.StringIO(experiment_run_document)
        try:
            exp = ExperimentRun.load(sio)
        except Exception as e:
            self.fail("ExperimentRun.load(StringIO) raised: %s" % e)
        self.assertIsNotNone(exp)

    def test_valid_syntax_check(self):
        syntax_check = ExperimentRun.check_syntax(self.dummy_exp_path)
        self.assertEqual(syntax_check.is_valid, True)

    def test_invalid_syntax_check(self):
        syntax_check = ExperimentRun.check_syntax(self.invalid_exp_path)
        self.assertEqual(syntax_check.is_valid, False)

    def test_get_phase_name(self):
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        exp.setup(broker_uri=None)
        self.assertEqual("phase_0", exp.get_phase_name(0))

    @patch("palaestrai.environment.EnvironmentConductor._init_environment")
    def test_loads_state_transformer(
        self,
        init_environment_meth_mock,
    ):
        fixtures_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "fixtures",
        )
        schedule = deepcopy(self.schedule)
        schedule[0]["phase_0"]["environments"][0].update(
            {
                "state_transformer": {
                    "name": "tests.unit.palaestrai.experiment.test_experiment_run"
                    ":FourtyTwoStateTransformer",
                    "params": {},
                }
            }
        )
        er = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=schedule,
            run_config=self.run_config,
        )
        er.setup(broker_uri=None)
        ecs = er.environment_conductors(0)
        ec = list(ecs.values())[0]
        env = ec._load_environment()
        self.assertIsNotNone(env._state_transformer)
        self.assertIsInstance(
            env._state_transformer, FourtyTwoStateTransformer
        )

    def test_save(self):
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        session = UnifiedAlchemyMagicMock()
        exp.save(session=session, experiment_uid="4")
        session.add.assert_called()
        experiment = session.add.call_args.args[0]
        self.assertEqual(experiment.name, "4")
        self.assertEqual(experiment.experiment_runs[0].uid, "test_setup")

    def test_hashes(self):
        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        e_hash_1 = exp.hash
        self.assertIsNotNone(e_hash_1)
        self.assertTrue(e_hash_1)

        exp._instance_uid = "4247123"
        e_hash_2 = exp.hash
        self.assertEqual(e_hash_1, e_hash_2)

        exp.uid = "Singapore Sling"
        e_hash_3 = exp.hash
        self.assertEqual(e_hash_1, e_hash_3)

        exp.schedule_config[0]["phase_0"]["agents"][0][
            "name"
        ] = "Bus Captain Woo"
        e_hash_4 = exp.hash
        self.assertNotEqual(e_hash_1, e_hash_4)

    def test_serialize_deserialize(self):
        import jsonpickle as json

        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
        )
        s_exp = json.dumps(exp)
        exp2 = json.loads(s_exp)
        self.assertEqual(exp.canonical_config, exp2.canonical_config)

        exp = ExperimentRun(
            uid="test_setup",
            seed=123,
            version=self.version,
            schedule=self.schedule,
            run_config=self.run_config,
            experiment_uid="T",
        )
        s_exp = json.dumps(exp)
        exp2 = json.loads(s_exp)
        self.assertEqual(exp.canonical_config, exp2.canonical_config)


class TestExperimentRunDump(unittest.TestCase):
    """Needed a separate test to get rid of the patches."""

    def test_dump(self):
        from io import StringIO

        import ruamel.yaml as yml
        from palaestrai.experiment import ExperimentRun

        dummy_exp_path = os.path.realpath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "../../../fixtures/dummy_run.yml",
            )
        )
        sio = StringIO()
        yaml = yml.YAML(typ="safe")
        yaml.register_class(ExperimentRun)
        exp = ExperimentRun.load(dummy_exp_path)
        yaml.dump(exp, sio)

        exp_loaded = yaml.load(sio.getvalue())
        self.assertEqual(sys.getsizeof(exp), sys.getsizeof(exp_loaded))


if __name__ == "__main__":
    unittest.main()
