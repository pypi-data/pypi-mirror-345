from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional, Dict

import signal
import logging
from uuid import uuid4

import aiomultiprocess

from palaestrai.util import spawn_wrapper
from palaestrai.core import EventStateMachine as ESM
from palaestrai.core import BasicState, RuntimeConfig
from palaestrai.core.protocol import (
    EnvironmentSetupRequest,
    EnvironmentSetupResponse,
    ShutdownRequest,
    ShutdownResponse,
)
from .environment import Environment
from palaestrai.util.dynaloader import load_with_params

if TYPE_CHECKING:
    import multiprocessing


LOG = logging.getLogger(__name__)


@ESM.monitor(is_mdp_worker=True)
class EnvironmentConductor:
    """The environment conductor creates new environment instances.

    There could be multiple simulation runs and each would need a
    separate environment. The environment conductor controls the
    creation of those new environment instances.

    Parameters
    ----------
    env_cfg : dict
        Dictionary with parameters needed by the environment
    seed : uuid4
        Random seed for recreation
    uid : uuid4
        Unique identifier

    """

    def __init__(self, env_cfg, seed: int, uid=None):
        self._uid: str = uid if uid else "EnvironmentConductor-%s" % uuid4()
        self._seed: int = seed
        self._environment_configuration = env_cfg
        self._state = BasicState.PRISTINE

        self._environments: Dict[str, Environment] = {}
        self._environment_processes: Dict[str, aiomultiprocess.Process] = {}

        LOG.debug("%s created.", self)

    @property
    def uid(self) -> str:
        return str(self._uid)

    @property
    def seed(self) -> int:
        return int(self._seed)

    def _load_environment(self) -> Environment:
        """Loads the ::`Environment` and necessary dependent classes."""
        env_name = None
        env_params = {}
        try:
            env_name = self._environment_configuration["environment"].get(
                "uid", "Unknown"
            )
            env_clazz = self._environment_configuration["environment"]["name"]
            env_params = self._environment_configuration["environment"][
                "params"
            ]
            env_uid = "%s.%s-%s" % (self.uid, env_name, str(uuid4())[-6:])
        except KeyError:
            LOG.critical(
                "%s could not load environment: Configuration not present. "
                'Key "environment" is missing in environment configuration. '
                "The configuration currently contains: %s",
                self,
                self._environment_configuration,
            )
            raise
        env_params.update(
            {
                "uid": env_uid,
                "broker_uri": f"tcp://127.0.0.1:{RuntimeConfig().executor_bus_port}",
                "seed": self.seed,
            }
        )

        LOG.debug(
            "%s loading Environment '%s' (UID %s) with params '%s'.",
            self,
            env_name,
            env_uid,
            env_params,
        )
        try:
            environment = load_with_params(env_clazz, env_params)
            environment._uid = env_uid
            environment._name = env_name
            environment.seed = self.seed + len(self._environments)
        except ValueError as e:
            LOG.critical(
                "%s could not load environment '%s': %s. Perhaps a typo in "
                "your configuration? %s",
                self,
                env_name,
                e,
                self._environment_configuration["environment"],
            )
            raise e

        if "state_transformer" in self._environment_configuration:
            environment._state_transformer = load_with_params(
                self._environment_configuration["state_transformer"]["name"],
                self._environment_configuration["state_transformer"]["params"],
            )
            LOG.debug(
                "%s loaded %s for %s",
                self,
                environment._state_transformer,
                environment,
            )
        if "reward" in self._environment_configuration:
            environment.reward = load_with_params(
                self._environment_configuration["reward"]["name"],
                self._environment_configuration["reward"]["params"],
            )
            LOG.debug(
                "%s loaded %s for %s",
                self,
                environment.reward,
                environment,
            )
        return environment

    @ESM.spawns
    def _init_environment(self, env: Environment) -> aiomultiprocess.Process:
        """Initialize a new environment.

        Creates a new environment instance with its own UID.

        Returns
        -------
        str
            The unique identifier of the new environment
        """
        try:
            env_process = aiomultiprocess.Process(
                name=env.uid,
                target=spawn_wrapper,
                args=(
                    env.uid,
                    RuntimeConfig().to_dict(),
                    env.run,  # type: ignore
                ),
            )
            env_process.start()
        except Exception as e:
            LOG.critical(
                "%s encountered a fatal error while executing %s: %s. "
                "Judgement day is nigh!",
                self,
                self._environments,
                e,
            )
            raise e
        return env_process

    def setup(self):
        self._state = BasicState.RUNNING
        self.mdp_service = self.uid
        LOG.info("%s commencing run: creating better worlds.", self.uid)

    @ESM.on(EnvironmentSetupRequest)
    def handle_environment_setup_request(self, request):
        LOG.debug(
            "%s received EnvironmentSetupRequest(experiment_run_id=%s).",
            self,
            request.experiment_run_id,
        )
        env = self._load_environment()
        assert env.uid not in self._environments
        self._environments[env.uid] = env
        LOG.info('Loaded environment "%s", starting subprocess...', env.name)
        assert env.uid not in self._environment_processes
        self._environment_processes[env.uid] = self._init_environment(env)
        return EnvironmentSetupResponse(
            sender_environment_conductor=request.receiver,
            receiver_simulation_controller=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
            environment_id=env.uid,
            environment_name=env.name,
            environment_type=self._environment_configuration["environment"][
                "name"
            ],
            environment_parameters=self._environment_configuration[
                "environment"
            ].get("params", dict()),
        )

    @ESM.on(ShutdownRequest)
    def handle_shutdown_request(self, request: ShutdownRequest):
        self._state = BasicState.STOPPING
        self.stop()  # type: ignore[attr-defined]
        return ShutdownResponse(
            sender=self.uid,
            receiver=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
        )

    @ESM.on(signal.SIGCHLD)
    def _handle_child(
        self, process: Union[aiomultiprocess.Process, multiprocessing.Process]
    ):
        LOG.debug(
            "%s: Environment child process %s endet.", self, process.name
        )
        if process.exitcode != 0:
            self._state = BasicState.ERROR
            LOG.critical(
                "Call Arthur Dent! "
                "The vogons demolished environment process %s "
                "(exited prematurely with rc %s)",
                process,
                process.exitcode,
            )
            self.stop(  # type: ignore[attr-defined]
                RuntimeError(f"Environment process {process.name} died.")
            )

    def teardown(self):
        if self._state != BasicState.ERROR:
            self._state = BasicState.FINISHED
        self._environment_processes.clear()
        LOG.info("%s completed shutdown.", self.uid)

    def __str__(self):
        return f"{self.__class__.__name__}(id=0x{id(self):x}, uid={self.uid})"
