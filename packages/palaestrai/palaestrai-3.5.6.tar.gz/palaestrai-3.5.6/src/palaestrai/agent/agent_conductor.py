from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional, List, Dict

from collections import namedtuple

import signal
import logging
import warnings
import setproctitle
import aiomultiprocess
from uuid import uuid4
from copy import deepcopy

from palaestrai.core.protocol import (
    AgentSetupRequest,
    AgentSetupResponse,
    ShutdownRequest,
    ShutdownResponse,
)
from palaestrai.types import ExperienceLocation
from palaestrai.core import EventStateMachine as ESM
from palaestrai.core import BasicState, RuntimeConfig
from palaestrai.util import spawn_wrapper
from palaestrai.util.dynaloader import load_with_params, ErrorDuringImport

from .brain import Brain
from .muscle import Muscle
from .learner import Learner
from .rollout_worker import RolloutWorker
from .brain_dumper import BrainDumper, BrainLocation

if TYPE_CHECKING:
    import multiprocessing
    from palaestrai.agent import Objective


LOG = logging.getLogger(__name__)


ExperimentRunInfo = namedtuple(
    "ExperimentRunInfo",
    ["experiment_run_uid", "experiment_run_phase"],
    defaults=(None, None),
)


async def _run_rollout_brain(learner: Learner):
    """This method starts the rollout brain in a new process and with this the monitoring by the ESM.

    It takes care of proper
    installment of signal handlers, setting of the proctitle, and most
    importantly, error handling. This method should be wrapped in the
    :py:func:`palaestrai.util.spawn_wrapper` function, which, in turn, is the
    target of an :py:func:`aiomultiprocess.Process.run` call.

    Parameters
    ----------
    learner : Learner
        The :class:`Learner` instance that should be run.

    Returns
    -------
    Any
        Whatever the ::`~Learner.run` method returns.
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGABRT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    setproctitle.setproctitle("palaestrAI[Brain-%s]" % learner.uid[-6:])
    try:
        # noinspection PyUnresolvedReferences
        return await learner.run()  # type: ignore[attr-defined]
    except Exception as e:
        LOG.error(
            "%s died from a fatal wound to the head: %s",
            learner,
            e,
        )
        raise


async def _run_rollout_worker(worker: RolloutWorker):
    """This method starts the rollout muscles in new processes and with this the monitoring by the ESM.

    It takes care of proper installment of signal handlers,
    setting of the proctitle, and most importantly, error handling.
    This method should be wrapped in the
    :py:func:`palaestrai.util.spawn_wrapper` function, which, in turn, is the
    target of an :py:func:`aiomultiprocess.Process.run` call.

    Parameters
    ----------
    worker : RolloutWorker
        The :class:`~RolloutWorker` instance that runs

    Returns
    -------
    Any
        Whatever ::`~RolloutMuscle.run` returns
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGABRT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    setproctitle.setproctitle("palaestrAI[Muscle-%s]" % worker.uid[-6:])
    try:
        # noinspection PyUnresolvedReferences
        return await worker.run()  # type: ignore[attr-defined]
    except Exception as e:
        LOG.error(
            "%s (%s) suffers from dystrophy: %s",
            worker,
            worker.uid,
            e,
        )
        raise


@ESM.monitor(is_mdp_worker=True)
class AgentConductor:
    """This creates a new agent conductor (AC).

    The AC receives an agent config, which contains all information for
    the brain and the muscle. Additional information, like the current
    run ID, are part of the AgentSetupRequest.

    Parameters
    ----------
    agent_config: dict
        A *dict* containing information, how to instantiate brain and
        muscle.
    seed: int
        The random seed for this agent conductor.
    uid : str
        The uid (a unique string) for this agent conductor object.
    name : str
        User-visible name as chosen by the user in the experiment run file
    """

    def __init__(
        self,
        agent_config: dict,
        seed: int,
        uid=None,
        name=None,
    ):
        self._state = BasicState.PRISTINE
        self._uid = (
            str(uid) if uid else "AgentConductor-%s" % str(uuid4())[-6:]
        )
        self._name = str(name) if name else f"Nemo-{self._uid[-6:]}"

        self._seed = seed
        self._config = agent_config

        self._brain_dumpers: List[BrainDumper] = []
        self._objective: Optional[Objective] = None
        self._learner: Optional[Learner] = None
        self._rollout_workers: Dict[str, RolloutWorker] = {}

        self._learner_process = None
        self._experiment_info: Optional[ExperimentRunInfo] = None
        self._rollout_worker_processes: Dict[str, aiomultiprocess.Process] = {}

    @property
    def uid(self):
        """Unique, opaque ID of the agent conductor object"""
        return self._uid

    @property
    def name(self):
        """Name as given to the agent by the user in the experiment run file"""
        return self._name

    def _load_brain_dumpers(self):
        """Loads all ::`~BrainDumper` descendants

        Through introspection, all classes that are descendants of
        ::`~BrainDumper` will be loaded. They have to be imported here in
        order for this to work.
        """

        dumpers = []
        previous_location: Optional[BrainLocation] = None
        for subclazz in BrainDumper.__subclasses__():
            try:
                current_location = BrainLocation(
                    agent_name=self._config["name"],
                    experiment_run_uid=self._experiment_info.experiment_run_uid,
                    experiment_run_phase=self._experiment_info.experiment_run_phase,
                )

                lcfg = (
                    {}
                    if self._experiment_info.experiment_run_phase <= 0
                    else {
                        "agent": self.name,
                        "experiment_run": self._experiment_info.experiment_run_uid,
                        "phase": (
                            self._experiment_info.experiment_run_phase - 1
                        ),
                    }
                )
                user_cfg = self._config.get("load", {})
                if not isinstance(user_cfg, dict) or user_cfg is None:
                    LOG.warning(
                        "%s has malformed `load` configuration "
                        "in phase %d of experiment run %s: %s. "
                        "Please use a load key analogue to "
                        "'load: "
                        "{experiment_run: %s, phase: %d, agent: %s }'."
                        "Continueing with defaults.",
                        self.name,
                        self._experiment_info.experiment_run_phase,
                        self._experiment_info.experiment_run_uid,
                        user_cfg,
                        self._experiment_info.experiment_run_uid,
                        self._experiment_info.experiment_run_phase,
                        self._name,
                    )
                    user_cfg = {}

                if user_cfg is not None:
                    lcfg.update(user_cfg)
                else:
                    lcfg = None
                previous_location = (
                    BrainLocation(
                        agent_name=lcfg["agent"],
                        experiment_run_uid=lcfg["experiment_run"],
                        experiment_run_phase=lcfg["phase"],
                    )
                    if (lcfg and lcfg["agent"] is not None)
                    else None
                )

                obj = subclazz(
                    dump_to=current_location, load_from=previous_location
                )
                dumpers.append(obj)
            except TypeError as e:
                LOG.warning(
                    "%s could not register brain dumper %s: %s, skipping",
                    self,
                    subclazz,
                    e,
                )
        LOG.info(
            "%s will load brain dumps from %s.",
            self._name,
            previous_location if previous_location else "nowhere",
        )
        LOG.debug("%s loaded %d dumpers: %s", self, len(dumpers), dumpers)
        return dumpers

    def _load_objective(self) -> Objective:
        return load_with_params(
            self._config["objective"]["name"],
            self._config["objective"].get("params", {}),
        )

    def _load_brain(self, actuators, sensors) -> Brain:
        params = self._config["brain"].get("params", {})
        try:
            brain: Brain = load_with_params(
                self._config["brain"]["name"], params
            )
        except TypeError:
            params.update(
                {
                    "seed": self._seed,
                    "sensors": sensors,
                    "actuators": actuators,
                }
            )
            try:
                brain = load_with_params(self._config["brain"]["name"], params)
                warnings.warn(
                    "Brain constructors with explicit 'muscle_connection', "
                    "'sensors', 'actuators', and 'seed' parameters are "
                    "deprecated in favor of simpler constructors. Please "
                    "just remove them, palaestrAI will take care of the rest.",
                    DeprecationWarning,
                )
            except Exception as e:  # Catch-all for any user code error
                LOG.exception("%s could not load Brain: %s, aborting", self, e)
                raise
        brain._seed = self._seed
        brain._sensors = sensors
        brain._actuators = actuators
        brain._dumpers = self._brain_dumpers
        return brain

    @ESM.spawns
    def _init_brain(self, sensors, actuators):
        """Initialize the brain process.

        Each agent, which is represented by an individual conductor,
        has one brain process. This function initializes the brain
        process.

        The agent conductor allocates the port for the brain-muscle
        interconnection. For this, it binds to a random port given from the OS.
        It passes the port to the brain and closes the socket; the Brain will
        then re-open the socket as ZMQ socket. That works because sockets are
        refcounted and the ref count goes to 0 when the ::`Brain` closes the
        socket before re-opening it. The agent conductor then uses the port
        number (not the socket itself) to pass it to the ::`Muscle` objects,
        which then know where to find their ::`Brain`.

        Parameters
        ----------
        sensors : List[SensorInformation]
            List of available sensors.
        actuators : List[ActuatorInformation]
            List of available actuators.

        Returns
        -------
        str
            The listen URI of the brain.
        """

        brain: Brain = self._load_brain(actuators, sensors)
        self._learner: Learner = Learner(brain, f"{self.uid}.Brain", self.name)
        self._learner._experience_locations = [
            ExperienceLocation(
                agent_name=eloc.get("agent", self.name),
                experiment_run_uid=eloc.get(
                    "experiment_run", self._experiment_info.experiment_run_uid
                ),
                experiment_run_phase=eloc.get(
                    "phase",
                    max(0, self._experiment_info.experiment_run_phase - 1),
                ),
            )
            for eloc in self._config.get("replay", [])
        ]

        # Load specific termination conditions:
        try:
            self._learner._termination_conditions = [
                load_with_params(tc["name"], tc["params"])
                for tc in self._config["termination_conditions"]
            ]
        except KeyError:
            LOG.warning(
                "No termination condition definition present "
                "in the experiment run configuration: %s",
                self._config,
            )
        except Exception as e:  # Any other error from user code:
            LOG.exception(
                "Loading of termination conditions %s failed: %s",
                self._config["termination_conditions"],
                e,
            )
            self.stop(e)

        self._learner_process = aiomultiprocess.Process(
            name=f"{self.uid}.Brain",
            target=spawn_wrapper,
            args=(
                self.uid,
                RuntimeConfig().to_dict(),
                _run_rollout_brain,
                [self._learner],
            ),
        )
        self._learner_process.start()
        LOG.debug(
            "%s started process %s for learner %s",
            self,
            self._learner_process,
            self._learner,
        )
        return self._learner_process

    def _load_muscle(self):
        try:
            params = deepcopy(self._config["muscle"]["params"])
        except KeyError:
            params = {}
        muscle: Muscle = load_with_params(
            self._config["muscle"]["name"], params
        )
        muscle._uid = self._config["name"]
        muscle._model_loaders = self._brain_dumpers
        return muscle

    @ESM.spawns
    def _init_muscle(self, muscle: Muscle, uid: str):
        """Function to run an initialized ::`~Muscle`

        Each agent consists of one ::`~Brain` and at least one ::`~Muscle`.
        Muscles are the inference/rollout workers that act within an
        environment, gathering experiences. Each muscle has a unique name;
        usually, this is the name of the agent in the environment.

        Muscles relay their experiences to their ::`~Brain`, which learns
        from the experiences and updates the inference model of the muscle.
        Thus, an "agent" entitity actually consists of one learner (Brain),
        one or more inference workers (Muscles), and this
        ::`~AgentConductor` that ties it all together.

        For starting the corresponding ::`~RolloutWorker` process that wraps
        the ::`~Muscle` instance given.

        Parameters
        ----------
        muscle : Muscle
            An initialized ::`~Muscle`
        uid : str
            Unique ID of the ::`~RolloutWorker` as the
            ::`~SimulationController` sets it up
        """

        assert self._learner is not None
        assert self._objective is not None

        rollout_worker = RolloutWorker(
            muscle=muscle,
            objective=self._objective,
            uid=uid,
            brain_uid=self._learner.uid,
        )
        self._rollout_workers[uid] = rollout_worker

        rollout_worker_process = aiomultiprocess.Process(
            name=uid,
            target=spawn_wrapper,
            args=(
                uid,
                RuntimeConfig().to_dict(),
                _run_rollout_worker,
                [rollout_worker],
            ),
        )
        rollout_worker_process.start()
        self._rollout_worker_processes[uid] = rollout_worker_process
        LOG.debug(
            "%s started process %s for rollout worker %s.",
            self,
            rollout_worker_process,
            rollout_worker,
        )
        return rollout_worker_process

    @ESM.on(AgentSetupRequest)
    def _handle_agent_setup(self, request: AgentSetupRequest):
        """Handle the agent setup request.

        One setup request will result in one new muscle created.
        The brain will be created if necessary.

        Parameters
        ----------
        request: :class:`.AgentSetupRequest`
            The agent setup request with information for the muscle to
            be created.

        Returns
        -------
        :class:`.AgentSetupResponse`
            The response for the simulation controller.

        """

        LOG.debug("%s got %s", self, request)
        if request.receiver_agent_conductor != self.uid:
            return

        # except (ModuleNotFoundError, ErrorDuringImport, AttributeError) as e:
        if self._learner is None:
            self._experiment_info = ExperimentRunInfo(
                experiment_run_uid=request.experiment_run_id,
                experiment_run_phase=request.experiment_run_phase,
            )
            self._brain_dumpers = self._load_brain_dumpers()
            self._objective = self._load_objective()
            _ = self._init_brain(request.sensors, request.actuators)

        muscle = self._load_muscle()
        rollout_worker_uid = "%s.%s-%s" % (
            self.uid,
            request.muscle_name,
            str(uuid4())[-6:],
        )
        _ = self._init_muscle(muscle, rollout_worker_uid)

        return AgentSetupResponse(
            sender_agent_conductor=self.uid,
            receiver_simulation_controller=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
            rollout_worker_id=rollout_worker_uid,
            muscle_name=request.muscle_name,
        )

    @ESM.on(signal.SIGCHLD)
    def _handle_child(
        self, process: Union[aiomultiprocess.Process, multiprocessing.Process]
    ):
        if process.exitcode == 0:
            LOG.debug("Process %s ended normally.", process.name)
            return
        self._state = BasicState.ERROR
        LOG.error(
            "One of our agents has been terminated: "
            "Process %s, exit code %s; ending all other processes.",
            process.name,
            process.exitcode,
        )
        self.stop()  # type: ignore[attr-defined]

    @ESM.on(ShutdownRequest)
    def _handle_shutdown_request(self, request: ShutdownRequest):
        LOG.debug("%s shutting down...", self)
        self._state = BasicState.STOPPING
        self.stop()  # type: ignore[attr-defined]
        return ShutdownResponse(
            sender=self.uid,
            receiver=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
        )

    def setup(self):
        self._state = BasicState.RUNNING
        self.mdp_service = self.uid
        LOG.info(
            "%s commencing run: Building our future... today!", self._name
        )

    def teardown(self):
        # ESM takes care of the processes, we just clean up:
        self._learner_process = None
        self._rollout_worker_processes = {}

        self._state = BasicState.FINISHED
        LOG.info("%s completed shutdown.", self._name)

    def __str__(self):
        return (
            f"AgentConductor(id={id(self)}, uid={self.uid}, learner="
            f"{self._learner}, workers={self._rollout_workers})"
        )
