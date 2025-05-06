"""This module contains the class :class:`ExperimentRun` that defines
an experiment run and contains all the information needed to execute
it.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, IO, Union, Optional, Any

import io
import copy
import uuid
import pprint
import hashlib
import logging
import collections.abc
from io import StringIO
from os import PathLike
from pathlib import Path
import importlib.resources

import sqlalchemy
from importlib.metadata import (
    version as importlib_version,
)  # had to be renamed because else it would clash with the ExperimentRun class version
import ruamel.yaml as yml
import simplejson as json
from semver import Version
from numpy.random import RandomState
from ruamel.yaml.constructor import ConstructorError

from ..agent import AgentConductor
from ..environment import EnvironmentConductor
from ..types.mode import Mode
from ..util import seeding
from ..util.dynaloader import load_with_params
from ..util.exception import UnknownModeError, EnvironmentHasNoUIDError
from ..util.syntax_validation import (
    SyntaxValidationResult,
    SyntaxValidationError,
)
from palaestrai.store import database_model as dbm
from palaestrai.store.session import Session
from sqlalchemy import select

if TYPE_CHECKING:
    from palaestrai.simulation import SimulationController
    from palaestrai.experiment import TerminationCondition
    import sqlalchemy.orm

LOG = logging.getLogger(__name__)


class RunDefinitionError(RuntimeError):
    def __init__(self, run: ExperimentRun, message):
        super().__init__(message)

        self.message = message
        self.run = run

    def __str__(self):
        return "%s (%s)" % (self.message, self.run)


class ExperimentRun:
    """Defines an experiment run and stores information.

    The experiment run class defines a run in palaestrAI. It contains
    all information needed to execute the run. With the setup function
    the experiment run can be build.

    Parameters
    ----------

    """

    SCHEMA_FILE = "run_schema.yaml"

    def __init__(
        self,
        uid: Union[str, None],
        seed: Union[int, None],
        version: Union[str, None],
        schedule: List[Dict],
        run_config: dict,
        experiment_uid: Optional[str] = None,
    ):
        if seed is None:
            # numpy expects a seed between 0 and 2**32 - 1
            self.seed: int = seeding.create_seed(max_bytes=4)
        else:
            self.seed = seed
        self.rng: RandomState = seeding.np_random(self.seed)[0]

        if uid is None:
            self.uid = f"ExperimentRun-{uuid.uuid4()}"
            LOG.warning(
                "Experiment run has no uid, please set one to "
                "identify it (assign the 'uid' key). Generated: "
                "'%s', so that you can find it in the store.",
                self.uid,
            )
        else:
            self.uid = uid
        self.experiment_uid = experiment_uid or (
            f"Dummy experiment record for experiment run {self.uid}"
        )

        self.version = version
        palaestrai_version = importlib_version("palaestrai")
        if self.version is None:
            self.version = palaestrai_version
            LOG.warning(
                "No version has been specified. There is no guarantee "
                "that this run will be executed without errors. Please "
                "set the version (assign the 'version' key) in the run "
                "file. Current palaestrAI version is '%s'.",
                self.version,
            )
        version_parsed = Version.parse(
            self.version, optional_minor_and_patch=True
        )
        palaestrai_version_parsed = Version.parse(palaestrai_version)
        if version_parsed.major != palaestrai_version_parsed.major or (
            version_parsed.major == palaestrai_version_parsed.major
            and version_parsed.minor != palaestrai_version_parsed.minor
        ):
            LOG.warning(
                "Your palaestrAI installation has version %s but your "
                "run file uses version %s, which may be incompatible.",
                palaestrai_version,
                version,
            )

        yaml = yml.YAML(typ="safe")
        yaml.representer.add_representer(
            RandomState, ExperimentRun.repr_randomstate
        )
        yaml.constructor.add_constructor(
            "rng", ExperimentRun.constr_randomstate
        )

        self.schedule_config = schedule
        self.run_config = run_config
        self.run_governor_termination_condition: TerminationCondition
        self.schedule: List
        self._instance_uid = str(uuid.uuid4())
        self._canonical_config: Dict[str, Any] = {}

    @property
    def instance_uid(self):
        """The unique ID of this particular experiment run instance

        As an ::`ExperimentRun` object is transferred via network, stored in
        the DB, etc., it still remains the same instance, but it becomes
        different objects in memory. This UID identifies it even if it travels
        over the network.

        Returns
        -------

        str
            The instances unique ID
        """
        return self._instance_uid

    @property
    def canonical_config(self):
        # We can never be sure whether something was changed or not.
        # Simply checking for the canonical config to be None does not
        # help, its actually dangerous. So expand it every time and just
        # hope that we're not calling this too often:
        self._canonical_config = self._expand_config()
        return self._canonical_config

    @property
    def hash(self) -> str:
        ccfg = copy.deepcopy(self.canonical_config)
        del ccfg["uid"]  # User-specified ID does not make a difference.
        del ccfg["experiment_uid"]  # dto.
        ecfg_json = json.dumps(ccfg, separators=(",", ":"), sort_keys=True)
        return hashlib.sha512(ecfg_json.encode("utf-8")).hexdigest()

    def create_subseed(self) -> int:
        """uses the seeded random number generator to create reproducible sub-seeds"""
        # number 5000 is arbitrary, for the numpy RandomState, could be any integer between 0 and 2**32 - 1
        a = self.rng.randint(0, 5000)
        return a

    @staticmethod
    def repr_randomstate(representer, data):
        """Custom serializer and deserializer so we can dump our subseed
        Data = rng"""
        serializedData = str(data)
        return representer.represent_scalar("rng", serializedData)

    @staticmethod
    def constr_randomstate(constructor, node):
        value = yml.loader.Constructor().construct_scalar(node)
        a = map(int, value.split(" "))
        return map(RandomState, a)

    def _expand_config(self) -> Dict:
        """Expanding the experiment run phases.
        Experiment run definition implements a cascading hierarchy.

        """
        from palaestrai.version import __version__

        canonical_config = dict()  # type: Dict[Any, Any]
        expanded_schedule = list()
        config = dict()  # type: Dict[Any, Any]
        canonical_config.update(
            {
                "uid": self.uid,
                "experiment_uid": self.experiment_uid,
                "seed": self.seed,
                "version": __version__,
            }
        )
        for (
            phase
        ) in self.schedule_config:  # cascade expansion of the schedule phases
            phase_name = list(phase.keys())[0]
            expanded_schedule.append(
                {
                    phase_name: copy.deepcopy(
                        update_dict(config, phase[phase_name])
                    )
                }
            )
        canonical_config.update({"schedule": expanded_schedule})
        canonical_config.update({"run_config": self.run_config})

        return canonical_config

    def _setup_termination_condition(self):
        """Set up the termination condition.."""
        rgtc = self.run_config["condition"]
        LOG.debug(
            "ExperimentRun(id=0x%x, uid=%s) loading RunGovernor "
            "TerminationCondition: %s.",
            id(self),
            self.uid,
            rgtc["name"],
        )
        try:
            rgtc = load_with_params(rgtc["name"], rgtc["params"])
        except Exception as err:
            LOG.critical(
                "Could not load termination condition '%s' with params "
                "%s for RunGovernor: %s",
                rgtc["name"],
                rgtc["params"],
                err,
            )
            raise err
        self.run_governor_termination_condition = rgtc

    def _setup_schedule(self, broker_uri: str):
        """Initialize the run time schedule

        Setup the schedule objects.
        """
        self.schedule = list()
        for num, phase in enumerate(self.canonical_config["schedule"]):
            if len(phase) > 1:
                raise RunDefinitionError(
                    self,
                    (
                        "Only one phase per phase allowed but "
                        f"found {len(phase)} phases."
                    ),
                )
            elif len(phase) < 1:
                LOG.warning(
                    "ExperimentRun(id=0x%x, uid=%s) found empty phase: "
                    "%d, skipping this one.",
                    id(self),
                    self.uid,
                    num,
                )
                continue
            phase_name = list(phase.keys())[0]
            config = phase[phase_name]
            agent_configs = dict()  # type: Dict[Any,Any]
            self.schedule.append(dict())
            self.schedule[num]["phase_config"] = config["phase_config"].copy()
            self._setup_environment_conductor(
                num, phase_name, config, broker_uri
            )
            self._setup_agent_conductor(num, phase_name, config, agent_configs)
            self._setup_simulation_controller(
                num, phase_name, config, agent_configs, broker_uri
            )

    def _setup_environment_conductor(
        self, phase_num: int, phase_name: str, config, broker_uri
    ):
        """Initialize an :class:`~EnvironmentConductor` for current phase."""
        for env_config in config["environments"]:
            self.schedule[phase_num].setdefault(
                "environment_conductors", dict()
            )

            env_uid = env_config["environment"].get("uid", None)
            if env_uid is None or env_uid == "":
                LOG.critical(
                    "ExperimentRun(id=0x%x, uid=%s): One of your "
                    "environments has no UID configured. Please "
                    "provide UIDs for all of your environments. "
                    "PalaestrAI, over and out!",
                    id(self),
                    self.uid,
                )
                raise EnvironmentHasNoUIDError()

            ec = EnvironmentConductor(
                env_config,
                self.create_subseed(),
            )
            self.schedule[phase_num]["environment_conductors"][ec.uid] = ec

        LOG.debug(
            "ExperimentRun(id=0x%x, uid=%s) set up %d "
            "EnvironmentConductor object(s) for phase %d: '%s'",
            id(self),
            self.uid,
            len(self.schedule[phase_num]["environment_conductors"]),
            phase_num,
            phase_name,
        )
        if len(self.schedule[phase_num]["environment_conductors"]) == 0:
            raise RunDefinitionError(
                self, f"No environments defined for phase {phase_num}."
            )

    def _setup_agent_conductor(
        self,
        phase_num: int,
        phase_name: str,
        config,
        agent_configs: Dict[Any, Any],
    ):
        """Initialize an :class:`~AgentConductor` for current phase."""
        for agent_config in config["agents"]:
            self.schedule[phase_num].setdefault("agent_conductors", dict())

            ac_conf = {key: value for key, value in agent_config.items()}
            ac_conf.update(
                {"termination_conditions": config["simulation"]["conditions"]}
            )
            ac = AgentConductor(
                agent_config=ac_conf,
                seed=self.create_subseed(),
                name=agent_config["name"],
                # Ok: uid is auto-generated by the AC
            )
            self.schedule[phase_num]["agent_conductors"][ac.uid] = ac
            agent_configs[ac.uid] = ac_conf

        num_agent_definitions = len(config["agents"])
        num_agent_conductors = len(
            self.schedule[phase_num]["agent_conductors"]
        )
        LOG.debug(
            "ExperimentRun(id=0x%x, uid=%s) set up %d AgentConductor "
            "object(s) for phase %d: '%s'.",
            id(self),
            self.uid,
            num_agent_conductors,
            phase_num,
            phase_name,
        )
        if num_agent_conductors == 0:
            raise RunDefinitionError(
                self, f"No agents defined for phase {phase_num}."
            )
        if num_agent_conductors != num_agent_definitions:
            raise RunDefinitionError(
                self,
                f"Your experiment run configuration for phase {phase_num} "
                f"contains ambiguities: "
                f"{num_agent_definitions} agent definitions spawned "
                f"{num_agent_conductors} unique agents. "
                f"Please check that all agent names are unique.",
            )

    def _setup_simulation_controller(
        self,
        phase_num: int,
        phase_name: str,
        config,
        agent_configs: Dict[Any, Any],
        broker_uri,
    ):
        """Initialize a :class:`~SimulationController` for current phase."""
        for _ in range(int(config["phase_config"].get("worker", 1))):
            self.schedule[phase_num].setdefault(
                "simulation_controllers", dict()
            )
            try:
                mode = Mode[
                    config["phase_config"].get("mode", "train").upper()
                ]
            except KeyError as err:
                raise UnknownModeError(err)

            if not config["simulation"]["name"].endswith(
                "SimulationController"
            ):
                config["simulation"]["name"] += "SimulationController"
            sc: SimulationController = load_with_params(
                config["simulation"]["name"],
                {
                    "sim_connection": broker_uri,
                    "rungov_connection": broker_uri,
                    "agent_conductor_ids": list(
                        self.schedule[phase_num]["agent_conductors"].keys()
                    ),
                    "environment_conductor_ids": list(
                        self.schedule[phase_num][
                            "environment_conductors"
                        ].keys()
                    ),
                    "termination_conditions": config["simulation"][
                        "conditions"
                    ],
                    "agents": agent_configs,
                    "mode": mode,
                },
            )
            self.schedule[phase_num]["simulation_controllers"][sc.uid] = sc
        LOG.debug(
            "ExperimentRun(id=0x%x, uid=%s) set up %d "
            "SimulationController object(s) for phase %d: '%s'.",
            id(self),
            self.uid,
            len(self.schedule[phase_num]["simulation_controllers"]),
            phase_num,
            phase_name,
        )
        if len(self.schedule[phase_num]["simulation_controllers"]) == 0:
            raise RunDefinitionError(
                self,
                "No simulation controller defined. Either "
                "'workers' < 1 or 'name' of key 'simulation' is "
                "not available.",
            )

    def setup(self, broker_uri):
        """Set up an experiment run.

        Creates and configures relevant actors.
        """
        LOG.debug("ExperimentRun(id=0x%x, uid=%s) setup.", id(self), self.uid)
        self._setup_termination_condition()
        self._setup_schedule(broker_uri)
        LOG.info(
            "ExperimentRun(id=0x%x, uid=%s) setup complete.",
            id(self),
            self.uid,
        )

    def environment_conductors(
        self, phase=0
    ) -> Dict[str, EnvironmentConductor]:
        return self.schedule[phase]["environment_conductors"]

    def agent_conductors(self, phase=0):
        return self.schedule[phase]["agent_conductors"]

    def simulation_controllers(self, phase=0):
        return self.schedule[phase]["simulation_controllers"]

    def get_phase_name(self, phase: int):
        return list(self.schedule_config[phase].keys())[0]

    def get_episodes(self, phase: int):
        return self.schedule[phase]["phase_config"]["episodes"]

    def phase_configuration(self, phase: int):
        return self.schedule[phase]["phase_config"]

    @property
    def num_phases(self):
        """The number of phases in this experiment run's schedule."""
        return len(self.schedule)

    def has_next_phase(self, current_phase):
        """Return if this run has a subsequent phase.

        Parameters
        ----------
        current_phase: int
            Index of the phase that is being executed.

        Returns
        -------
        bool
            True if at least one phase is taking place after
            the current phase.
        """
        return current_phase + 1 < self.num_phases

    @staticmethod
    def check_syntax(
        path_or_stream: Union[str, IO[str], PathLike]
    ) -> SyntaxValidationResult:
        """Checks if the provided experiment configuration conforms
        with our syntax.

        Parameters
        ----------
        path_or_stream: 1. str - Path to an experiment configuration file
                        2. Path - Same as above
                        3. Any text stream

        Returns
        ----------
        SyntaxValidationResult:
        Custom object that contains the following information:

            1. SyntaxValidationResult.is_valid: Whether the provided experiment
                is valid or not (::`bool`).
            2. SyntaxValidationResult.error_message: Contains ::`None` if the
                experiment is valid or the corresponding error message
                if it is invalid.

        """
        with importlib.resources.path(
            __package__, ExperimentRun.SCHEMA_FILE
        ) as path:
            validation_result = SyntaxValidationResult.validate_syntax(
                path_or_stream, path
            )
        return validation_result

    @staticmethod
    def load(str_path_stream_or_dict: Union[str, Path, Dict, IO[str]]):
        """Load an ::`ExerimentRun` object from a serialized representation.

        This method serves as deserializing constructor. It takes a
        path to a file, a dictionary representation, or a stream and creates
        a new ::`ExperimentRun` object from it.

        This method also validates the string/stream representation.

        Parameters
        ----------
        str_path_stream_or_dict : Union[str, Path, Dict, IO[str]]
            * If `str`, it is interpreted as a file path, and the file is
              resolved and loaded;
            * if `Path`, the same happens as above;
            * if `Dict`, the ::`ExperimentRun` object is initialized directly
              from the values of the `Dict`;
            * if `TextIO`, the method assumes that it is a serialzed
              representation of the ::`ExperimentRun` object (e.g., from an
              open file stream) and interprets it as YAML (with a prior
              syntax/schema check).

        Returns
        -------
        ExperimentRun
            An initialized, de-serialized ::`ExperimentRun` object
        """
        LOG.debug("Loading configuration from %s.", str_path_stream_or_dict)

        # If we get a dict directly, we syntax check nevertheless.
        if isinstance(str_path_stream_or_dict, dict):
            sio = StringIO()
            yml.YAML(typ="safe", pure=True).dump(str_path_stream_or_dict, sio)
            str_path_stream_or_dict = sio

        if isinstance(str_path_stream_or_dict, (str, Path)):
            try:
                str_path_stream_or_dict = open(str_path_stream_or_dict, "r")
            except OSError as err:
                LOG.error("Could not open run configuration: %s.", err)
                raise err

        # Load from YAML + schema check:

        validation_result = ExperimentRun.check_syntax(str_path_stream_or_dict)
        if not validation_result:
            LOG.error(
                "ExperimentRun definition did not schema validate: %s",
                validation_result.error_message,
            )
            raise SyntaxValidationError(validation_result)
        try:
            str_path_stream_or_dict.seek(0)
            conf = yml.YAML(typ="safe", pure=True).load(
                str_path_stream_or_dict
            )
            str_path_stream_or_dict.close()
        except ConstructorError as err:
            LOG.error("Could not load run configuration: %s.", err)
            raise err
        finally:
            if isinstance(str_path_stream_or_dict, io.TextIOBase):
                str_path_stream_or_dict.close()

        LOG.debug("Loaded configuration: %s.", conf)
        return ExperimentRun(
            uid=conf.get("uid", conf.get("id", None)),
            seed=conf.get("seed", None),
            version=conf.get("version", None),
            schedule=conf["schedule"],
            run_config=conf["run_config"],
            experiment_uid=conf.get("experiment_uid", None),
        )

    @staticmethod
    def from_dict(state: Dict) -> ExperimentRun:
        er = ExperimentRun(
            uid=state["uid"],
            seed=state["seed"],
            version=state["version"],
            schedule=state["schedule"],
            run_config=state["run_config"],
            experiment_uid=state.get("experiment_uid", None),
        )
        er.__setstate__(state)
        return er

    def save(
        self,
        experiment_uid: Optional[str] = None,
        session: Optional[sqlalchemy.orm.Session] = None,
    ):
        """Save an ::`ExerimentRun` object to the store.

        This method saves an experiment run and adds it to the database.
        Connection credentials are taken from the runtime config.
        If an ``experiment_uid`` is supplied, then the experiment run is also
        associated with it in the database.
        A session instance can also be supplied in order ot reuse an open database connection.
        Otherwise, a new connection will be opened.

        Parameters
        ----------
        experiment_uid : Optional[str]
            The unique ID of this particular experiment run instance
        session : Optional[Session]
            Creates a new, connected database session to run queries on.

        """

        _session = session
        if not _session:
            _session = Session()
        if experiment_uid is None:
            experiment_uid = (
                "Dummy Experiment record " "for ExperimentRun %s" % self.uid
            )
        query = select(dbm.Experiment).where(
            dbm.Experiment.name == experiment_uid
        )
        experiment_hack_record = _session.execute(query).scalars().first()
        if not experiment_hack_record:
            experiment_hack_record = dbm.Experiment(name=experiment_uid)
            yaml = yml.YAML(typ="safe")
            yaml.register_class(ExperimentRun)
            yaml.representer.add_representer(
                RandomState, ExperimentRun.repr_randomstate
            )
            yaml.constructor.add_constructor(
                "rng", ExperimentRun.repr_randomstate
            )
            _session.add(experiment_hack_record)

        query = select(dbm.ExperimentRun).where(
            dbm.ExperimentRun.uid == self.uid
        )
        result = _session.execute(query).scalars().all()
        if len(result) > 1:
            LOG.warning(
                "Found %d entries for ExperimentRun(uid=%s) "
                "when there should be at most one. I'm going to use the first "
                "one, but if strange things happen, don't blame it on me.",
                len(result),
                self.uid,
            )
        try:
            experiment_run_record = result[0]
        except IndexError:
            experiment_run_record = dbm.ExperimentRun(
                uid=self.uid,
                document=self,
            )
            experiment_hack_record.experiment_runs.append(
                experiment_run_record
            )
        finally:
            if not session:
                _session.close()

        try:
            _session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            LOG.exception(
                "%s was not possible to run properly: It "
                "was not possible to save the runs of Experiment (uid=%s)! Perhaps "
                "your environment does not provide enough entropy, or we have "
                "a resend. I'm going to ignore this error and continue as "
                "best as I can. (%s)",
                self.uid,
                e,
            )
        finally:
            if not session:
                _session.close()
        if not session:
            _session.close()

    def __getstate__(self):
        state = dict(_rng=self.rng, _instance_uid=self._instance_uid)
        state.update(copy.deepcopy(self.canonical_config))
        return state

    def __setstate__(self, state: Dict):
        self.uid = state["uid"]
        self.experiment_uid = state.get(
            "experiment_uid",
            f"Dummy experiment record for experiment run {self.uid}",
        )
        self.seed = state["seed"]
        self._canonical_config = state
        self._instance_uid = state.get("_instance_uid") or str(uuid.uuid4())
        self.run_config = state["run_config"]
        self.schedule_config = state["schedule"]
        self.rng = state.get("_rng", None) or seeding.np_random(self.seed)[0]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ExperimentRun) and self.hash == other.hash

    def __repr__(self):
        return pprint.pformat(self.canonical_config, indent=4)

    def __str__(self):
        return f"ExperimentRun(uid={self.uid}, hash={self.hash})"


def update_dict(src, upd):
    """Recursive update of dictionaries.

    See stackoverflow:

        https://stackoverflow.com/questions/3232943/
        update-value-of-a-nested-dictionary-of-varying-depth

    """
    for key, val in upd.items():
        if isinstance(val, collections.abc.Mapping):
            src[key] = update_dict(src.get(key, {}), val)
        else:
            src[key] = val
    return src
