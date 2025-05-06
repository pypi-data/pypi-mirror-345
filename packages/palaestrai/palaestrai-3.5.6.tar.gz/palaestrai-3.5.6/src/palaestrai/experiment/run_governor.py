from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Set, Optional, Union

import uuid
import signal
import logging
import asyncio
from collections import defaultdict

from aiomultiprocess import Process

from palaestrai.core.protocol import (
    ExperimentRunStartRequest,
    ExperimentRunStartResponse,
    SimulationStartRequest,
    SimulationStartResponse,
    SimulationControllerTerminationRequest,
    SimulationControllerTerminationResponse,
    ErrorIndicator,
    SimulationShutdownRequest,
    SimulationShutdownResponse,
    ExperimentRunShutdownRequest,
    ExperimentRunShutdownResponse,
    ShutdownRequest,
    ShutdownResponse,
)
from palaestrai.util import spawn_wrapper
from palaestrai.types import SimulationFlowControl
from palaestrai.core import EventStateMachine as ESM
from palaestrai.core import BasicState, RuntimeConfig
from palaestrai.util.exception import ExperimentAlreadyRunningError

if TYPE_CHECKING:
    import aiomultiprocess
    import multiprocessing
    from palaestrai.experiment import TerminationCondition
    from palaestrai.experiment.experiment_run import ExperimentRun

LOG = logging.getLogger(__name__)


@ESM.monitor(is_mdp_worker=True)
class RunGovernor:
    """
    This class implements the Run-Governor.

    Upon receiving requests from the executor, a RunGovernor instance
    handles a single experiment run by starting it, initialize the
    simulation controllers, the environment and the agent conductors,
    and, finally, shutting the experiment run down.

    The RunGovernor is implemented as state machine and this class
    provides the context for the distinct state classes. A freshly
    initialized RunGovernor waits in the state PRISTINE until the run
    method is called by the executor. See the distinct state classes
    for more information.

    Parameters
    ----------
    uid : str
        The universally unique ID that identifies this run governor

    Attributes
    ----------
    uid: str
        The UUID of this RunGovernor
    termination_condition: :class:`.TerminationCondition`
        A reference to the TerminationCondition instance.
    run_broker: :class:`.MajorDomoBroker`
        The broker for the communication with the simulation
        controller, the agents, and the environments.
    experiment_run_id: str
        The UUID of the current experiment run.
    tasks: List[aiomultiprocess.Process]
        A list of tasks the RunGovernor has started and that it has
        to shutdown in the end.
    worker: :class:`.MajorDomoWorker`
        The major domo worker for handling incoming requests
    client: :class:`.MajorDomoClient`
        The major domo client for sending requests to other workers.
    shutdown: bool
        The major kill switch of the RunGovernor. Setting this to false
        will stop the RunGovernor after the current state.
    state: :class:`.RunGovernorState`
        Holds the current state instance. The first state is PRISTINE.
    errors: List[Exception]
        A list that is used to collect errors raised in the states.
    """

    def __init__(self, uid: Optional[str] = None):
        self.uid = uid if uid else "RunGovernor-%s" % str(uuid.uuid4())
        self._state = BasicState.PRISTINE

        # Experiment control:
        self.current_phase: int = 0
        self.current_episode_counts: Dict[str, int] = {}
        self.experiment_run: Optional[ExperimentRun] = None
        self._termination_condition: Optional[TerminationCondition] = None

        # Receiver information:
        self._simulation_controllers: List[str] = []
        self._environment_conductors: List[str] = []
        self._agent_conductors: List[str] = []

        # Receiver synchronization:
        self._simulation_controllers_active: Set[str] = set()
        self._future_simulation_controllers_down: Optional[asyncio.Future] = (
            None
        )
        self._future_shutdown: Optional[asyncio.Future] = None
        self._future_next_phase: Optional[asyncio.Future] = None
        self._phase_launcher_task: Optional[asyncio.Task] = None
        self._shutdown_conductors_task: Optional[asyncio.Task] = None

        # Subprocess management:
        self._processes: List[aiomultiprocess.Process] = []

    def setup(self):
        self._state = BasicState.PRISTINE
        self.mdp_service = self.uid  # type: ignore[attr-defined]
        LOG.debug("%s ready.", self)
        self._state = BasicState.INITIALIZING

    @ESM.on(ExperimentRunStartRequest)
    async def _handle_experiment_run_start_request(
        self, request: ExperimentRunStartRequest
    ):
        if self.experiment_run is not None:
            LOG.warning(
                '%s got request to start experiment run "%s", '
                'but experiment run "%s" is already running. '
                "Reporting error and continueing. Elect somebody "
                "else instead!",
                self,
                self.experiment_run.uid,
                request.experiment_run.uid,
            )
            self.stop()  # type: ignore[attr-defined]
            return ExperimentRunStartResponse(
                sender_run_governor_id=request.receiver,
                receiver_executor_id=request.sender,
                experiment_run_id=request.experiment_run_id,
                experiment_run=request.experiment_run,
                successful=False,
                error=ExperimentAlreadyRunningError(self.experiment_run),
            )

        self.current_phase = 0
        self.experiment_run = request.experiment_run

        LOG.debug("%s setting up %s", self, self.experiment_run)

        try:
            await self._setup_run()
            self._state = BasicState.INITIALIZED
        except Exception as e:
            LOG.exception("%s encountered exception during setup: %s", self, e)
            self.stop(e)  # type: ignore[attr-defined]
            return ExperimentRunStartResponse(
                sender_run_governor_id=request.receiver,
                receiver_executor_id=request.sender,
                experiment_run_id=request.experiment_run_id,
                experiment_run=request.experiment_run,
                successful=False,
                error=e,
            )
        self._phase_launcher_task = asyncio.create_task(self._run_all_phases())
        return ExperimentRunStartResponse(
            sender_run_governor_id=request.receiver,
            receiver_executor_id=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run=request.experiment_run,
            successful=True,
            error=None,
        )

    async def _run_all_phases(self):
        self._state = BasicState.RUNNING
        n_phases = self.experiment_run.num_phases
        while self.current_phase < n_phases:
            self._future_next_phase = (
                asyncio.get_running_loop().create_future()
            )
            self._future_simulation_controllers_down = (
                asyncio.get_running_loop().create_future()
            )
            self._future_shutdown = asyncio.get_running_loop().create_future()
            LOG.debug(
                'Setting up phase %d/%d in experiment run "%s"...',
                self.current_phase + 1,  # +1 for display purposes
                n_phases,
                self.experiment_run.uid,
            )
            await self._setup_phase()
            LOG.debug(
                "%s sending start request(s) to simulation controllers...",
                self,
            )
            ssrq = self._send_simulation_start_requests()
            LOG.debug("%s sent simulation start requests: %s", self, ssrq)
            LOG.debug("%s waiting for phase to end", self)
            await self._future_next_phase
            # Wait for all processes to really end:
            LOG.debug(
                "%s waiting for processes to end: %s", self, self._processes
            )
            for p in self._processes:
                await p.join()
            self.current_phase += 1
        LOG.info(
            'Executed all phases in run "%s", shutting down.',
            self.experiment_run.uid,
        )
        try:
            await asyncio.wait_for(self._future_shutdown, timeout=15)
        except TimeoutError:
            LOG.error(
                "%s timed out while waiting for all processes to end. "
                "Conductors still active: %s",
                self,
                self._agent_conductors + self._environment_conductors,
            )
        await self._request_simulation_controllers_shutdown()
        self.stop()  # type: ignore[attr-defined]

    async def _setup_run(self):
        self.experiment_run.setup(
            f"tcp://127.0.0.1:{RuntimeConfig().executor_bus_port}"
        )
        assert (
            self.experiment_run.run_governor_termination_condition is not None
        )
        self._termination_condition = (
            self.experiment_run.run_governor_termination_condition
        )

    async def _setup_phase(self):
        self.current_episode_counts = defaultdict(int)  # Default value: 0
        ps = await asyncio.gather(
            self._start_environment_conductors(),
            self._start_agent_conductors(),
            self._start_simulation_controllers(),
        )  # Returns a nested list
        self._processes = [p for pl in ps for p in pl]  # Flatten "ps" list
        LOG.debug(
            "%s has processes this phase: %s",
            self,
            [p.name for p in self._processes],
        )

    @ESM.spawns
    async def _start_simulation_controllers(self):
        simulation_controllers = (
            self.experiment_run.simulation_controllers(self.current_phase)
        ).values()
        LOG.debug(
            "%s lauching simulation controller processes: %s",
            self,
            list(simulation_controllers),
        )
        sc_processes = [
            Process(
                name=f"SimulationController-{sc.uid}",
                target=spawn_wrapper,
                args=(
                    f"SimulationController-{sc.uid[-6:]}",
                    RuntimeConfig().to_dict(),
                    sc.run,
                ),
            )
            for sc in simulation_controllers
        ]
        self._simulation_controllers = [
            sc.uid for sc in simulation_controllers
        ]
        for p in sc_processes:
            p.start()
        return sc_processes

    @ESM.spawns
    async def _start_environment_conductors(self):
        environment_conductors = (
            self.experiment_run.environment_conductors(self.current_phase)
        ).values()
        LOG.debug(
            "%s lauching environment conductor processes: %s",
            self,
            list(environment_conductors),
        )
        ec_processes = [
            Process(
                name=f"EnvironmentConductor-{ec.uid}",
                target=spawn_wrapper,
                args=(
                    f"EnvironmentConductor-{ec.uid[-6:]}",
                    RuntimeConfig().to_dict(),
                    ec.run,
                ),
            )
            for ec in environment_conductors
        ]
        self._environment_conductors = [
            ec.uid for ec in environment_conductors
        ]
        for p in ec_processes:
            p.start()
        return ec_processes

    @ESM.spawns
    async def _start_agent_conductors(self):
        agent_conductors = (
            self.experiment_run.agent_conductors(self.current_phase)
        ).values()
        LOG.debug(
            "%s lauching agent conductor processes: %s",
            self,
            list(agent_conductors),
        )
        ac_processes = [
            Process(
                name=f"AgentConductor-{ac.uid}",
                target=spawn_wrapper,
                args=(
                    f"AgentConductor-{ac.uid[-6:]}",
                    RuntimeConfig().to_dict(),
                    ac.run,
                ),
            )
            for ac in agent_conductors
        ]
        self._agent_conductors = [ac.uid for ac in agent_conductors]
        for p in ac_processes:
            p.start()
        return ac_processes

    @ESM.requests
    def _send_simulation_start_requests(self):
        self._simulation_controllers_active = set()
        return [
            SimulationStartRequest(
                sender_run_governor_id=self.uid,
                receiver_simulation_controller_id=sc_uid,
                experiment_run_id=self.experiment_run.uid,
                experiment_run_instance_id=self.experiment_run.instance_uid,
                experiment_run_phase=self.current_phase,
                experiment_run_phase_id=self.experiment_run.get_phase_name(
                    self.current_phase
                ),
                experiment_run_phase_configuration=self.experiment_run.phase_configuration(
                    self.current_phase
                ),
            )
            for sc_uid in self._simulation_controllers
        ]

    @ESM.on(SimulationStartResponse)
    def _handle_simulation_start_response(
        self, response: SimulationStartResponse
    ):
        LOG.debug(
            "%s got simulation start response from %s", self, response.sender
        )
        self._simulation_controllers_active |= {response.sender}

    @ESM.on(SimulationControllerTerminationRequest)
    async def _handle_simulation_controller_termination_request(
        self, request: SimulationControllerTerminationRequest
    ):
        LOG.debug(
            "%s, workers: %s", request, self._simulation_controllers_active
        )
        assert self.experiment_run is not None
        assert self._termination_condition is not None
        self.current_episode_counts[request.sender] += 1
        flow, _ = self._termination_condition.phase_flow_control(self, request)

        if flow == SimulationFlowControl.CONTINUE:
            return SimulationControllerTerminationResponse(
                sender_run_governor_id=request.receiver,
                receiver_simulation_controller_id=request.sender,
                experiment_run_instance_id=self.experiment_run.instance_uid,
                experiment_run_id=request.experiment_run_id,
                experiment_run_phase=self.current_phase,
                restart=False,
                complete_shutdown=False,
                flow_control=flow,
            )

        if flow.value <= SimulationFlowControl.RESTART.value:
            # Restart/soft-reset of this particular worker:
            LOG.info(
                'Restarting simulation worker "%s" '
                'in phase %d of experiment run "%s"',
                request.sender,
                self.current_phase + 1,
                self.experiment_run.uid,
            )
            return SimulationControllerTerminationResponse(
                sender_run_governor_id=request.receiver,
                receiver_simulation_controller_id=request.sender,
                experiment_run_instance_id=self.experiment_run.instance_uid,
                experiment_run_id=request.experiment_run_id,
                experiment_run_phase=self.current_phase,
                restart=True,
                complete_shutdown=False,
                flow_control=flow,
            )
        LOG.info(
            'Signalling simulation worker "%s" to shut down '
            'for phase %d in experiment run "%s"',
            request.sender,
            self.current_phase + 1,  # +1 for display purposes only.
            self.experiment_run.uid,
        )

        # Potentially shut down all workers, so sending
        # SimulationShutdownRequest to all running simulation controllers,
        # also the SimController that requests the termination, because
        # itself did not or has not been shutdown yet

        if flow == SimulationFlowControl.STOP_PHASE:
            # Create task to ask next step, shutdown all conductors.
            # Its only a matter of time until the last one goes down...
            # We start this task here, but we try to wait for the
            # SC process to actually end using a future…
            # The future is set in the SIGCHLD event handler.
            self._simulation_controllers_active -= {request.sender}
            self._shutdown_conductors_task = asyncio.create_task(
                self._request_conductors_shutdown()
            )

        return SimulationControllerTerminationResponse(
            sender_run_governor_id=request.receiver,
            receiver_simulation_controller_id=request.sender,
            experiment_run_instance_id=self.experiment_run.instance_uid,
            experiment_run_id=request.experiment_run_id,
            experiment_run_phase=self.current_phase,
            restart=False,
            complete_shutdown=True,
            flow_control=flow,
        )

    async def _request_conductors_shutdown(self):
        LOG.debug("%s waiting to shut down all conductors...", self)
        if self._future_simulation_controllers_down is not None:
            await self._future_simulation_controllers_down
        _ = self._send_agent_conductor_shutdown_requests()
        _ = self._send_environment_conductor_shutdown_requests()

    async def _request_simulation_controllers_shutdown(self):
        _ = self._send_simulation_shutdown_requests()

    @ESM.requests
    def _send_agent_conductor_shutdown_requests(self):
        LOG.debug(
            "%s requesting shut down of %s", self, self._agent_conductors
        )
        return [
            ShutdownRequest(
                sender=self.uid,
                receiver=acuid,
                experiment_run_id=self.experiment_run.uid,
                experiment_run_instance_id=self.experiment_run.instance_uid,
                experiment_run_phase=self.current_phase,
            )
            for acuid in self._agent_conductors
        ]

    @ESM.requests
    def _send_environment_conductor_shutdown_requests(self):
        LOG.debug(
            "%s requesting shutdown of %s", self, self._environment_conductors
        )
        return [
            ShutdownRequest(
                sender=self.uid,
                receiver=ecuid,
                experiment_run_id=self.experiment_run.uid,
                experiment_run_instance_id=self.experiment_run.instance_uid,
                experiment_run_phase=self.current_phase,
            )
            for ecuid in self._environment_conductors
        ]

    @ESM.on(ShutdownResponse)
    def _handle_shutdown_response(self, response: ShutdownResponse):
        self._agent_conductors = [
            acuid
            for acuid in self._agent_conductors
            if not acuid == response.sender
        ]
        self._environment_conductors = [
            ecuid
            for ecuid in self._environment_conductors
            if not ecuid == response.sender
        ]
        LOG.debug(
            "%s got %s, conductors still up: %s",
            self,
            response,
            self._agent_conductors + self._environment_conductors,
        )
        if (
            len(self._agent_conductors) + len(self._environment_conductors)
            == 0
        ):
            assert self._future_next_phase is not None
            assert self._future_shutdown is not None
            self._future_next_phase.set_result(True)
            self._future_shutdown.set_result(True)

    @ESM.requests
    def _send_simulation_shutdown_requests(self):
        LOG.debug(
            "%s sending SimulationShutdownRequest(s) to %s",
            self,
            self._simulation_controllers_active,
        )
        if self._future_simulation_controllers_down is None:
            # This can happen if we get this before a phase is started.
            # In this case, we're probably not returning any shutdown
            # request, as there's simply no simulation controller active.
            # Still, we have to stay consistent:
            self._future_simulation_controllers_down = (
                asyncio.get_running_loop().create_future()
            )
        return [
            SimulationShutdownRequest(
                sender=self.uid,
                receiver=sc_uid,
                experiment_run_id=self.experiment_run.uid,
                experiment_run_instance_id=self.experiment_run.instance_uid,
                experiment_run_phase=self.current_phase,
            )
            for sc_uid in self._simulation_controllers_active
        ]

    @ESM.on(SimulationShutdownResponse)
    def _handle_simulation_shutdown_response(
        self, response: SimulationShutdownResponse
    ):
        self._simulation_controllers_active -= {response.sender}
        if len(self._simulation_controllers_active) == 0:
            assert self._future_simulation_controllers_down is not None
            self._future_simulation_controllers_down.set_result(True)

    @ESM.on(ExperimentRunShutdownRequest)
    async def _handle_shutdown_request(
        self, request: ExperimentRunShutdownRequest
    ):
        LOG.info(
            'Shutdown of experiment run "%s" requested',
            self.experiment_run.uid if self.experiment_run else "(no run)",
        )
        if self._phase_launcher_task is not None:
            self._phase_launcher_task.cancel()
        # Create the future to make sure we have not dead tasks:
        if not self._future_simulation_controllers_down:
            self._future_simulation_controllers_down = (
                asyncio.get_running_loop().create_future()
            )
        await self._request_simulation_controllers_shutdown()
        await self._future_simulation_controllers_down
        self.stop()  # type: ignore[attr-defined]
        return ExperimentRunShutdownResponse(
            sender_run_governor_id=self.uid,
            receiver_executor_id=request.sender,
            experiment_run_id=request.experiment_run_id,
            successful=True,
            error=None,
        )

    @ESM.on(ErrorIndicator)
    def _raise_error_indicator(self, error: ErrorIndicator):
        self._state = BasicState.ERROR
        LOG.critical(
            "%s received error from %s: %s",
            self,
            error.sender,
            error.error_message,
        )
        # TODO: Shutdown everything
        if error.exception is not None:
            raise error.exception
        raise RuntimeError(error.error_message)

    @ESM.on(signal.SIGCHLD)
    def _handle_child(
        self, process: Union[aiomultiprocess.Process, multiprocessing.Process]
    ):
        LOG.debug("%s saw process %s end.", self, process.name)
        if process.exitcode != 0:
            self._state = BasicState.ERROR
            LOG.critical(
                "Subprocess %s exited prematurely with rc %s). "
                "Cannot continue simulation.",
                process.name,
                process.exitcode,
            )
            self.stop(  # type: ignore[attr-defined]
                RuntimeError(
                    f"Subprocess {process.name} ended prematurely "
                    f"with rc {process.exitcode}"
                )
            )

        self._processes = [p for p in self._processes if p.pid != process.pid]
        if (
            process.name.startswith("SimulationController-")
            and len(
                [
                    p
                    for p in self._processes
                    if p.name.startswith("SimulationController-")
                ]
            )
            == 0
        ):
            LOG.debug("%s saw last simulation controller end.", self)
            # If this was the last SC, we can shutdown all conductors.
            # To let the respective task continue, set this future:
            assert self._future_simulation_controllers_down is not None
            self._future_simulation_controllers_down.set_result(True)

    def __str__(self):
        return (
            f"RunGovernor(uid={self.uid}, state={self._state.name}, "
            f"experiment_run_uid="
            f"{self.experiment_run.uid if self.experiment_run is not None else '(None)'}, "
            f"phase={self.current_phase})"
        )
