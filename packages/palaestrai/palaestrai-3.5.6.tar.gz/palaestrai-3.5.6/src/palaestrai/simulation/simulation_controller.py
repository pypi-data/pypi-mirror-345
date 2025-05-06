from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Sequence,
    Dict,
    List,
    Set,
    Union,
    Tuple,
    Optional,
)

import re
import asyncio
import logging
import uuid
from asyncio import Future
from collections import defaultdict
from itertools import product, chain

from palaestrai.agent import Agent
from palaestrai.core import BasicState
from palaestrai.util import mapping_update_r
from palaestrai.types import SimulationFlowControl
from palaestrai.core import EventStateMachine as ESM
from palaestrai.core.protocol import (
    SimulationStartRequest,
    SimulationStartResponse,
    EnvironmentSetupRequest,
    EnvironmentSetupResponse,
    EnvironmentStartRequest,
    EnvironmentStartResponse,
    AgentSetupRequest,
    AgentSetupResponse,
    AgentUpdateRequest,
    AgentUpdateResponse,
    EnvironmentUpdateRequest,
    EnvironmentUpdateResponse,
    ErrorIndicator,
    SimulationControllerTerminationRequest,
    SimulationControllerTerminationResponse,
    EnvironmentResetRequest,
    EnvironmentResetResponse,
    EnvironmentResetNotificationRequest,
    EnvironmentResetNotificationResponse,
    AgentShutdownRequest,
    AgentShutdownResponse,
    EnvironmentShutdownRequest,
    EnvironmentShutdownResponse,
    ShutdownRequest,
    ShutdownResponse,
    SimulationShutdownRequest,
    SimulationShutdownResponse,
)

# from palaestrai.util.exception import SimulationSetupError
from palaestrai.types import SimTime
from palaestrai.util.dynaloader import load_with_params

if TYPE_CHECKING:
    from palaestrai.types import Mode
    from palaestrai.experiment import TerminationCondition
    from palaestrai.agent import (
        SensorInformation,
        ActuatorInformation,
        RewardInformation,
    )

LOG = logging.getLogger(__name__)


class FlowControlChange(Exception):
    """Raised to immediately abort the simulation loop on flow change"""

    def __init__(self, flow_interrupts):
        super().__init__()
        self.flow_interrupts = flow_interrupts


@ESM.monitor(is_mdp_worker=True)
class SimulationController:
    """
    A simulation execution strategy where agents take turns.

    In this simulation controller, updates are applied to all environments
    simulataneuously. Agents take turn in acting:

    1. All environments update
    2. agent 1 acts
    3. all environment update
    4. agent 2 acts
    5. etc. ad infinitum

    For each agent action and subsequent environment update, simulated time
    advances.

    Parameters
    ----------
    agent_conductor_ids : Sequence[str]
        Unique IDs (service IDs) of all :class:`~AgentConductor`s
        this simulation controller talks to
    environment_conductor_ids : Sequence[str]
        Unique IDs (service IDs) of all :class:`~EnvironmentConductor`s
        this simulation controller talks to
    agents : Dict[str, Any]
        Configuration of all :class:`~Agent`s that participate in this
        simulation
    mode : palaestrai.types.Mode
        Mode of the simulation, e.g., training or testing
    termination_conditions : Dict[str, Any]
        Configuration of simulation :class:`~TerminationCondition`s.
        A termination condition indicates when a simulation should end, e.g.,
        when the environment terminates. The simulation controller instanciates
        all termination conditions.

    Attributes
    ----------
    uid : str
        Unique ID of this simulation controller (MDP service ID).
        Auto-generated upon instanciation.
    """

    def __init__(
        self,
        agent_conductor_ids: Sequence[str],
        environment_conductor_ids: Sequence[str],
        agents: Dict[str, Dict],
        mode: Mode,
        termination_conditions: Sequence[Dict[str, Any]],
        *args,
        **kwargs,
    ):  # *args, **kwargs for compatibility
        self.uid = f"{self.__class__.__name__}-{str(uuid.uuid4())[-6:]}"
        self._state = BasicState.PRISTINE

        # UIDs:
        self._run_governor_uid: str = str()
        self._agent_conductor_ids = list(agent_conductor_ids)
        assert len(self._agent_conductor_ids) == len(
            set(self._agent_conductor_ids)
        ), "Some Agent Conductor UIDs are duplicated"
        self._environment_conductor_ids = list(environment_conductor_ids)
        assert len(self._environment_conductor_ids) == len(
            set(self._environment_conductor_ids)
        ), "Some Environment Conductor UIDs are duplicated"
        self._termination_condition_configurations = termination_conditions

        # Identification of the experiment run:
        self._experiment_run_id: str = str()
        self._experiment_run_instance_id: str = str()
        self._experiment_run_phase: int = 0
        self._mode = mode

        # Configuration (list of agents, sensors available, etc.):
        self._agents: Dict[str, Optional[Agent]] = {}
        self._agent_configurations: Dict[str, Dict] = agents
        self._agents_requested: List[AgentUpdateRequest] = []
        self._agents_ready: List[
            Union[
                AgentSetupResponse,
                AgentUpdateResponse,
                EnvironmentResetNotificationResponse,
            ]
        ] = []
        self._sensors_available: Dict[str, SensorInformation] = {}
        self._actuators_available: Dict[str, ActuatorInformation] = {}
        self._termination_conditions: List[TerminationCondition] = []
        self._environment_conductor_map: Dict[str, str] = {}
        self._active_environments: Set[str] = set()
        self._conductors_shut_down: List[ShutdownResponse] = []

        # Current state of the simulation
        self._simtimes: Dict[str, SimTime] = defaultdict(SimTime)
        self._environment_update_responses: List[EnvironmentUpdateResponse] = (
            []
        )
        self._current_sensor_readings: List[SensorInformation] = list()
        self._rewards_per_agent: Dict[str, List[RewardInformation]] = (
            defaultdict(list)
        )
        self._flow_control_indicator = SimulationFlowControl.CONTINUE
        self._flow_control_data: Dict[
            str, Tuple[SimulationFlowControl, Any]
        ] = {}

        # Futures for synchronization:
        self._future_init: Optional[Future] = None
        self._future_agents_environments_end: Optional[Future] = None
        self._future_agent_actions: Optional[Future] = None
        self._future_environment_status: Optional[Future] = None

    @property
    def is_running(self) -> bool:
        """Checks whether the main loop should be running."""
        return self._state == BasicState.RUNNING

    @property
    def state(self) -> BasicState:
        """Gets the current state of the simulation"""
        return self._state

    @property
    def agents(self) -> List[Agent]:
        """Returns information about all agents we work with

        Returns
        -------
        List of ::`~Agent` :
            List of agents (along with their agent conductors and rollout
            workers) that this simulation controller works with. Using this
            property guarantees that the list of agents is returned in exactly
            the order in which they were defined.
        """
        agents = [a for a in self._agents.values() if a is not None]
        return agents

    @property
    def environments(self) -> List[str]:
        """Returns a list of UIDs of all known environments

        Returns
        -------
        List of str:
            List of UIDs for environments relevant for this controller
        """
        return list(self._environment_conductor_map.keys())

    @property
    def sensor_readings(self) -> List[SensorInformation]:
        """Current sensor readings"""
        return self._current_sensor_readings

    @property
    def rewards(self) -> Dict[str, List[RewardInformation]]:
        """Gives current rewards per agent"""
        return self._rewards_per_agent

    @property
    def termination_conditions(self) -> List[TerminationCondition]:
        """All loaded ::`~TerminationCondition` instances"""
        return self._termination_conditions

    def setup(self):
        self._state = BasicState.PRISTINE
        self._load_termination_conditions()
        self._future_init = asyncio.get_running_loop().create_future()
        self._future_agents_environments_end = (
            asyncio.get_running_loop().create_future()
        )
        self.mdp_service = self.uid
        self._rewards_per_agent.clear()
        LOG.info("Simulation controller is ready: Follow the white rabbit.")

    def _load_termination_conditions(self):
        """
        Load (instanciate) all termination conditions.

        Raises an exception if a termination condition could not be loaded,
        which needs to be handled by the caller.
        """
        try:
            self._termination_conditions = [
                load_with_params(cond["name"], cond["params"])
                for cond in self._termination_condition_configurations
            ]
        except Exception as e:
            LOG.exception("%s could not load termination condition", self)
            raise

    @ESM.on(SimulationStartRequest)
    async def _handle_simulation_start_request(
        self, request: SimulationStartRequest
    ) -> Union[SimulationStartResponse, ErrorIndicator]:
        LOG.info(
            "Starting simulation for "
            "experiment run %s, phase %s (#%d) in mode %s: "
            "Knock, knock -- the matrix has you.",
            request.experiment_run_id,
            request.experiment_run_phase_id,
            request.experiment_run_phase,
            self._mode,
        )
        self._state = BasicState.INITIALIZING
        self._run_governor_uid = request.sender_run_governor_id
        self._experiment_run_id = request.experiment_run_id
        self._experiment_run_instance_id = request.experiment_run_instance_id
        self._experiment_run_phase = request.experiment_run_phase

        _ = self._send_environment_setup_requests()

        assert self._future_init is not None
        try:
            await self._future_init
            self._state = BasicState.INITIALIZED
        except Exception:
            self._state = BasicState.ERROR

            async def _raise():
                raise self._future_init.exception()

            await asyncio.get_running_loop().create_task(_raise())
            return ErrorIndicator(
                self.uid,
                request.sender,
                str(self._future_init.exception()),
                self._future_init.exception(),
            )
        await self._start_simulation_task()
        return SimulationStartResponse(
            sender_simulation_controller=self.uid,
            receiver_run_governor=request.sender_run_governor_id,
        )

    @ESM.requests
    def _send_environment_setup_requests(self):
        LOG.info(
            "Reqesting setup of environments from environment conductors: %s",
            self._environment_conductor_ids,
        )
        return [
            EnvironmentSetupRequest(
                receiver_environment_conductor_id=ec_id,
                sender_simulation_controller_id=self.uid,
                experiment_run_phase=self._experiment_run_phase,
                experiment_run_id=self._experiment_run_id,
                experiment_run_instance_id=self._experiment_run_instance_id,
            )
            for ec_id in self._environment_conductor_ids
        ]

    @ESM.on(EnvironmentSetupResponse)
    async def _handle_environment_setup_response(
        self, response: EnvironmentSetupResponse
    ):
        LOG.debug(
            "%s environment (#%s) started for "
            "experiment run %s, phase (#%s): "
            "Kcnok, kcnok -- the matrix returned.",
            self,
            response.environment_id,
            response.experiment_run_id,
            response.experiment_run_phase,
        )
        self._environment_conductor_map[response.environment_id] = (
            response.sender_environment_conductor
        )

        _ = self._try_start_environments()

    @ESM.requests
    def _try_start_environments(self):
        if set(self._environment_conductor_ids) != set(
            self._environment_conductor_map.values()
        ):
            return []
        LOG.debug(
            "%s sending EnvironmentStartRequest to %s",
            self,
            self._environment_conductor_map.keys(),
        )
        return [
            EnvironmentStartRequest(
                sender_simulation_controller=self.uid,
                receiver_environment=env_id,
                experiment_run_id=self._experiment_run_id,
                experiment_run_instance_id=self._experiment_run_instance_id,
                experiment_run_phase=self._experiment_run_phase,
            )
            for env_id in self._environment_conductor_map.keys()
        ]

    @ESM.on(EnvironmentStartResponse)
    async def _handle_environment_start_response(
        self, response: EnvironmentStartResponse
    ):
        LOG.debug(
            "%s environment %s reports that it started...",
            self,
            response.sender,
        )
        self._sensors_available.update(
            {sensor.uid: sensor for sensor in response.sensors}
        )
        self._actuators_available.update(
            {actuator.uid: actuator for actuator in response.actuators}
        )
        self._simtimes[response.sender_environment] = response.simtime
        self._active_environments |= {response.sender_environment}
        _ = self._try_setup_agents()

    @ESM.requests
    def _try_setup_agents(self):
        if self._active_environments != set(
            self._environment_conductor_map.keys()
        ):
            LOG.debug(
                "%s != %s",
                self._active_environments,
                self._environment_conductor_map.keys(),
            )
            return []

        unassigned = self._unassigned_sensors_actuators()
        if unassigned:
            LOG.critical(
                "%s"
                "found sensor/actuator assignments in the definition of "
                "ExperimentRun(id=%s), which could not be matched with the "
                "sensors/actuators actually provided by the environments: "
                "%s. "
                "The environments provide the following sensors: %s "
                "and the following actuators: %s",
                self,
                self._experiment_run_id,
                unassigned,
                list(self._sensors_available.keys()),
                list(self._actuators_available.keys()),
            )
            assert self._future_init is not None
            self._future_init.set_exception(
                # TODO: Debug why SimulationSetupError is not working
                RuntimeError(
                    # experiment_run_id=self._experiment_run_id,
                    # message=
                    "Sensor/actuator assignments not possible: %s"
                    % (unassigned)
                )
            )
            return []

        requests = []
        for acuid in self._agent_conductor_ids:
            self._agents[acuid] = None
            conf = self._agent_configurations[acuid]
            agent_name = conf["name"] if "name" in conf else "Nemo"
            sensors = [
                self._sensors_available[sen_uid]
                for sen_uid in self._sensors_available.keys()
                if sen_uid in conf.get("sensors", [])
            ]
            actuators = [
                self._actuators_available[act_uid]
                for act_uid in self._actuators_available.keys()
                if act_uid in conf.get("actuators", [])
            ]
            requests.append(
                AgentSetupRequest(
                    sender_simulation_controller=self.uid,
                    receiver_agent_conductor=acuid,
                    experiment_run_id=self._experiment_run_id,
                    experiment_run_instance_id=self._experiment_run_instance_id,
                    experiment_run_phase=self._experiment_run_phase,
                    muscle_name=agent_name,
                    sensors=sensors,
                    actuators=actuators,
                    configuration=conf,
                )
            )
            LOG.info('Requesting setup of agent "%s".', agent_name)
            LOG.debug("%s sending AgentSetupRequest to %s", self, acuid)
        return requests

    @ESM.on(AgentSetupResponse)
    def _handle_agent_setup_response(self, response: AgentSetupResponse):
        conf = self._agent_configurations[response.sender_agent_conductor]
        agent = Agent(
            uid=response.muscle_name,
            brain=None,
            brain_classname=conf["brain"]["name"],
            brain_params=conf["brain"]["params"],
            muscle_classname=conf["muscle"]["name"],
            muscle_params=conf["muscle"]["params"],
            muscles={response.rollout_worker_id: None},
            sensors=[
                self._sensors_available[sen_uid]
                for sen_uid in self._sensors_available.keys()
                if sen_uid in conf.get("sensors", [])
            ],
            actuators=[
                self._actuators_available[act_uid]
                for act_uid in self._actuators_available.keys()
                if act_uid in conf.get("actuators", [])
            ],
        )
        assert response.sender_agent_conductor in self._agents
        self._agents[response.sender_agent_conductor] = agent
        LOG.debug(
            "Agent '%s' has UID '%s'; sensors: %s; actuators: %s",
            agent.uid,
            response.rollout_worker_id,
            agent.sensors,
            agent.actuators,
        )
        self._agents_ready.append(response)
        LOG.info(
            'Rollout worker "%s" for agent "%s" is set up (%d/%d).',
            response.rollout_worker_id,
            response.sender_agent_conductor,
            len(self._agents_ready),
            len(self._agent_conductor_ids),
        )
        if len(self._agents_ready) == len(self._agent_conductor_ids):
            assert self._future_init is not None
            self._future_init.set_result(True)

    async def _start_simulation_task(self):
        self._future_agents_environments_end = (
            asyncio.get_running_loop().create_future()
        )
        self._state = BasicState.RUNNING
        self._current_sensor_readings = list(self._sensors_available.values())
        LOG.info("Starting simulation.")
        self._simulation_task = asyncio.create_task(self.simulate())
        self._simulation_task.add_done_callback(self._handle_simulation_end)

    async def act(
        self, agents: List[Agent], done: bool = False
    ) -> List[AgentUpdateResponse]:
        """
        Lets the given agents act, returning their setpoint responses.

        Parameters
        ----------
        agents : list of ::`~.Agent`
            The agents we should query for their decisions. The simulation
            controller will automatically provide the last environment state.
        done : bool, default: False
            If true, agents are only notified as the sensor readings
            represent the terminal state.

        Returns
        -------
        List of ::`~.AgentUpdateResponse`
            Setpoint responses of the agents
        """
        self._future_agent_actions = asyncio.get_running_loop().create_future()
        self._agents_ready.clear()
        self._agents_requested = [
            self._request_agent_actions(
                agent,
                SimulationController.filter_sensors_for_agent(
                    self._current_sensor_readings, agent
                ),
                self._rewards_per_agent[agent.uid],
                done=done,
            )
            for agent in agents
        ]
        await self._future_agent_actions
        rsps: List[AgentUpdateResponse] = self._future_agent_actions.result()
        self._update_flow_data_and_raise_on_flow_change(rsps)
        return rsps

    async def step(
        self, agents: List[Agent], setpoints: List[ActuatorInformation]
    ):
        """Updates known environments, returning new sensor readings

        Parameters
        ----------
        agents : List of ::`~Agent`
            The agents who act
        setpoints : List of ::`~ActuatorInformation`
            New setpoints for the environments

        Returns
        -------
        List of ::`~SensorInformation
            New sensor readings
        """
        # First, step the environment:

        self._future_environment_status = (
            asyncio.get_running_loop().create_future()
        )
        self._environment_update_responses.clear()
        _ = self._request_environment_updates(setpoints)
        await self._future_environment_status
        env_updates: List[EnvironmentUpdateResponse] = (
            self._future_environment_status.result()
        )

        # Update simtimes and sensor readings. For the sensor readings, we
        # assume that there might be readings from other environments, so we
        # only update those whose UID is in the list of new readings.

        self._simtimes.update(
            {
                eu.sender_environment_id: (
                    eu.simtime
                    if eu.simtime is not None
                    # This allows to change the default_factory in the
                    # self._simtimes definition
                    else self._simtimes[eu.sender_environment_id]
                )
                for eu in env_updates
            }
        )

        new_sensor_readings = [
            si for si in chain.from_iterable(eu.sensors for eu in env_updates)
        ]
        new_sensor_reading_uids = [si.uid for si in new_sensor_readings]
        self._current_sensor_readings = [
            r
            for r in self._current_sensor_readings
            if r.uid not in new_sensor_reading_uids
        ]
        self._current_sensor_readings += new_sensor_readings

        # Update rewards, but only for those agents who acted this turn.
        # The rewards for the applied actions gets stored for the
        # current agent in order to present it to this agent in the
        # next loop iteration

        rewards = [
            r for r in chain.from_iterable(eu.rewards for eu in env_updates)
        ]
        for agent in agents:
            self._rewards_per_agent[agent.uid] = rewards

        # Update flow control status:
        self._update_flow_data_and_raise_on_flow_change(env_updates)

        return env_updates

    async def advance(
        self,
    ):
        """Advances the whole simulation one time step

        This method advances the state of the simulation by one step.
        What precisely one step is depends on the simulation control paradigm
        the individual controller implements, but often it means that at least
        one agent has acted and at least one environment was updated.
        So this method calls ::`.act` to let one or more agents act, and
        ::`.step` to evaluate the given environments.
        The corresponding properties most often needed are:

        * ::`.agents` and ::`.environments` for data about all known
          agents and environments, respectively
        * ::`.sensor_readings` for current data from all environments
        * ::`.rewards` for current agent rewards.

        The ::`.act` and ::`.step` methods update
        all relevant state information.
        In addtion, the two methods also handle flow control:
        If an agent or an environment interrupt the normal simulation flow,
        the ::`FlowControlChange` exception is thrown.
        You don't have to catch it in this method, as usually a change in
        simulation control flow should be propagated further.
        Should you ever want to interrupt the simulation control flow yourself
        outside of the usual termination conditions handling, you are free to
        raise the ::`FlowControlChange` exception yourself.
        However, this should be rarely needed. In case of errors, please
        raise any other exception that makes sense, i.e., mostly a
        ``RuntimeError``.

        Advance is a simpler version of the ::`.simulate` method.
        While overwriting ::`.simulate` allows complete control over the loop,
        this method is called for every time step and can update agents
        and environments however they please.
        On call to this method implies that time has advanced.

        Advance does not return anything.
        """
        pass

    async def simulate(self):
        """Main simulation task

        This method is usually scheduled as a task at the end of the simulation
        setup phase. It can be overwritten by descendant classes to excert
        complete control over the simulation.

        Otherwise, it calls ::`.advance` until this method signals that the
        simulation should be interrupted.
        """
        LOG.debug("%s starting main simulation loop.", self)
        while self.is_running:
            try:
                await self.advance()
            except FlowControlChange:
                LOG.debug("%s: flow control was changed.", self)
                self._state = BasicState.STOPPING
        self.flow_control()

    def _update_flow_data_and_raise_on_flow_change(
        self,
        responses: Union[
            List[EnvironmentUpdateResponse], List[AgentUpdateResponse]
        ],
    ):
        """Checks flow control and raises ::`FlowControlChange` on change"""

        # Update flow control status:

        for rsp in responses:
            self._flow_control_indicator = SimulationFlowControl(
                max(
                    self._flow_control_indicator.value,
                    rsp.flow_control_indicator.value,
                )
            )

            self._flow_control_data = mapping_update_r(
                self._flow_control_data, rsp.flow_control_data
            )

        terminations = {  # Old style TCs:
            tc.__class__.__name__: tc.check_termination(msg)
            for tc, msg in product(self._termination_conditions, responses)
            if tc.check_termination(msg)
        }
        terminates = (
            any(terminations.values())
            or self._flow_control_indicator != SimulationFlowControl.CONTINUE
        )
        terminations.update(self._flow_control_data)
        if terminates:
            raise FlowControlChange(terminations)

    def _handle_simulation_end(self, task: asyncio.Task):
        e = task.exception()
        if e is not None:
            LOG.critical(
                "%s: simulation exited with error: %s",
                self,
                e,
                exc_info=(type(e), e, e.__traceback__),
            )
            raise e

    def _unassigned_sensors_actuators(self):
        """
        Sanity check of sensors/actuators between agents and environments.

        Sensors and actuators are returned from an ::`Environment` as part of
        the ::`EnvironmentSetupResponse`. The configuration of an experiment
        run contains a mapping of these sensors/actuators to agents. This
        method checks whether the mapping is correct. It catches typos or
        sensors specified that are not present in an environment.

        Returns
        -------
        Dict[str, Tuple[Set, Set]]
            For an agent, a Tuple containing the list of unmatched sensors,
            and the list of unmatched actuators. E.g.,
            ``{"my_agent": (["snesor_with_typo"], [])}``
        """
        result = dict()
        all_sensor_ids = set(self._sensors_available.keys())
        all_actuator_ids = set(self._actuators_available.keys())
        for acuid, conf in self._agent_configurations.items():
            agent_assigned_sensor_ids = set(conf.get("sensors", []))
            agent_assigned_actuator_ids = set(conf.get("actuators", []))
            missing_sensors = agent_assigned_sensor_ids - all_sensor_ids
            missing_actuators = agent_assigned_actuator_ids - all_actuator_ids
            if missing_sensors or missing_actuators:
                result[conf.get("name", acuid)] = (
                    missing_sensors,
                    missing_actuators,
                )
        return result

    @staticmethod
    def filter_sensors_for_agent(
        current_sensor_readings: List[SensorInformation], agent: Agent
    ) -> List[SensorInformation]:
        return [
            r
            for r in current_sensor_readings
            if r.uid in [s.uid for s in agent.sensors]
        ]

    @ESM.requests
    def _request_agent_actions(
        self,
        agent: Agent,
        sensor_readings: List[SensorInformation],
        rewards: Optional[List[RewardInformation]],
        done: bool,
    ) -> List[AgentUpdateRequest]:
        requests = [
            AgentUpdateRequest(
                sender_simulation_controller_id=self.uid,
                receiver_rollout_worker_id=rollout_worker_uid,
                experiment_run_id=self._experiment_run_id,
                experiment_run_instance_id=self._experiment_run_instance_id,
                experiment_run_phase=self._experiment_run_phase,
                sensors=sensor_readings,
                actuators=agent.actuators,
                rewards=rewards,
                simtimes=dict(self._simtimes),
                is_terminal=done,
                mode=self._mode,
            )
            for rollout_worker_uid in agent.muscles.keys()
        ]
        LOG.debug("Requesting updates from agent: %s", requests)
        return requests

    @ESM.on(AgentUpdateResponse)
    def _handle_agent_update(self, response: AgentUpdateResponse):
        LOG.debug("Got %s", response)
        self._agents_ready += [response]
        if len(self._agents_requested) == len(self._agents_ready):
            assert self._future_agent_actions is not None
            self._future_agent_actions.set_result(self._agents_ready)

    @ESM.requests
    def _request_environment_updates(
        self, setpoints: List[ActuatorInformation]
    ):
        requests = [
            EnvironmentUpdateRequest(
                sender_simulation_controller=self.uid,
                receiver_environment=env_uid,
                experiment_run_id=self._experiment_run_id,
                experiment_run_instance_id=self._experiment_run_instance_id,
                experiment_run_phase=self._experiment_run_phase,
                actuators=[
                    s
                    for s in setpoints
                    if s.uid.split(".")[0] == re.split(r"[-.]", env_uid)[-2]
                ],
            )
            for env_uid in self._active_environments
        ]
        LOG.debug(
            "%s posting setpoints "
            "and requesting new state from environments %s",
            self,
            requests,
        )
        return requests

    @ESM.on(EnvironmentUpdateResponse)
    def _handle_environment_update(self, response: EnvironmentUpdateResponse):
        self._environment_update_responses += [response]
        LOG.debug("Received environment update response: %s", response)

        if len(self._environment_update_responses) == len(
            self._active_environments
        ):
            assert self._future_environment_status is not None
            self._future_environment_status.set_result(
                self._environment_update_responses
            )

    @ESM.on(SimulationShutdownRequest)
    async def _handle_external_stop_request(
        self, request: SimulationShutdownRequest
    ):
        LOG.info("Shutting down the simulation due to external request")
        self._state = BasicState.STOPPING
        assert self._future_agents_environments_end is not None
        await self._future_agents_environments_end
        self.stop()  # type: ignore[attr-defined]
        return SimulationShutdownResponse(
            sender=self.uid,
            receiver=request.sender,
            experiment_run_id=self._experiment_run_id,
            experiment_run_instance_id=self._experiment_run_instance_id,
            experiment_run_phase=self._experiment_run_phase,
        )

    @ESM.requests
    def _request_control_flow_change(self):
        LOG.debug(
            "%s indicates flow control: %s.",
            self,
            self._flow_control_indicator,
        )
        return SimulationControllerTerminationRequest(
            sender_simulation_controller_id=self.uid,
            receiver_run_governor_id=self._run_governor_uid,
            experiment_run_id=self._experiment_run_id,
            flow_control_indicator=self._flow_control_indicator,
            flow_control_data=self._flow_control_data,
        )

    def flow_control(self):
        """Requests a change in flow control from the run governor"""
        if self._flow_control_indicator == SimulationFlowControl.CONTINUE:
            return  # Well, CONTINUE is not really a change in the flow.
        _ = self._request_control_flow_change()

    @ESM.on(SimulationControllerTerminationResponse)
    async def _handle_termination_response(
        self, response: SimulationControllerTerminationResponse
    ):
        LOG.debug("%s received %s.", self, response)

        # Regardless of what happens now, we update agents one last time to
        # tell them that we're changing the flow:

        try:
            await self.act(self.agents, done=True)
        except FlowControlChange:
            pass  # This doesn't change anything now.

        if (
            response.flow_control.value <= SimulationFlowControl.RESET.value
            or response.restart
        ):
            # Do not shut down, everything stays intact, but gets reset.
            # This is even true if the run governor sends us a CONTINUE
            # flow control indicator, as we've already signalled the need to
            # change flow control - resetting is the least we can do
            await self._restart()
            return

        # Everything else *must* be a shutdown.
        await self._shutdown()

    async def _shutdown(self):
        LOG.info(
            "Simulation controller %s shutting down...",
            self.uid,
        )
        for agent in self._agents.values():
            reqs = self._request_agent_shutdown(agent)
            LOG.debug("%s requesting shutdown of agent(s): %s", self, reqs)
        for env in self._active_environments:
            reqs = self._request_environment_shutdown(env)
            LOG.debug(
                "%s requesting shutdown of environment(s): %s", self, reqs
            )
        assert self._future_agents_environments_end is not None
        await self._future_agents_environments_end
        self._state = self._future_agents_environments_end.result()
        self._state = BasicState.FINISHED
        LOG.debug("%s finished.", self)
        self.stop()

    async def _restart(self):
        LOG.info("Simulation controller %s restarting simulation...", self.uid)
        self._sensors_available.clear()
        self._actuators_available.clear()
        self._active_environments.clear()
        self._flow_control_data.clear()
        self._flow_control_indicator = SimulationFlowControl.CONTINUE
        self._future_init = asyncio.get_running_loop().create_future()
        for env_uid in self._environment_conductor_map.keys():
            LOG.debug("Requesting reset of environment '%s'", env_uid)
            _ = self._request_environment_reset(env_uid)
        await self._future_init

        self._agents_ready.clear()
        self._future_init = asyncio.get_running_loop().create_future()
        for agent in self._agents.values():
            LOG.debug(
                "Requesting reset of rollout worker(s) %s",
                list(agent.muscles.keys()),
            )
            _ = self._request_agent_reset(agent)
        await self._future_init

        # We can continue, now
        await self._start_simulation_task()

    @ESM.requests
    def _request_environment_reset(self, env_uid):
        return EnvironmentResetRequest(
            sender_simulation_controller_id=self.uid,
            receiver_environment_id=env_uid,
            experiment_run_id=self._experiment_run_id,
            experiment_run_phase=self._experiment_run_phase,
            experiment_run_instance_id=self._experiment_run_instance_id,
        )

    @ESM.on(EnvironmentResetResponse)
    def _handle_environment_reset_response(
        self, response: EnvironmentResetResponse
    ):
        if response.create_new_instance:
            LOG.error(
                "Environment '%s' requests that we create a new "
                "instance, but this feature is not yet implemented.",
                response.sender_environment_id,
            )
            return
        self._active_environments |= {response.sender_environment_id}
        self._sensors_available.update(
            {sensor.uid: sensor for sensor in response.sensors}
        )
        self._actuators_available.update(
            {actuator.uid: actuator for actuator in response.actuators}
        )
        self._simtimes[response.sender_environment_id] = response.simtime
        if len(self._active_environments) == len(
            self._environment_conductor_map
        ):
            assert self._future_init is not None
            self._future_init.set_result(self._active_environments)

    @ESM.requests
    def _request_agent_reset(self, agent: Agent):
        return [
            EnvironmentResetNotificationRequest(
                sender_simulation_controller_id=self.uid,
                receiver_agent_id=rwuid,
            )
            for rwuid in agent.muscles.keys()
        ]

    @ESM.on(EnvironmentResetNotificationResponse)
    def _handle_environment_reset_notification_response(
        self, response: EnvironmentResetNotificationResponse
    ):
        self._agents_ready += [response]
        if len(self._agents_ready) == len(self._agents):
            assert self._future_init is not None
            self._future_init.set_result(self._agents_ready)

    @ESM.requests
    def _request_agent_shutdown(self, agent: Agent):
        return [
            AgentShutdownRequest(
                sender=self.uid,
                receiver=rollout_worker_uid,
                experiment_run_id=self._experiment_run_id,
                experiment_run_phase=self._experiment_run_phase,
                experiment_run_instance_id=self._experiment_run_instance_id,
            )
            for rollout_worker_uid in agent.muscles.keys()
        ]

    @ESM.on(AgentShutdownResponse)
    def _handle_agent_shutdown_response(self, response: AgentShutdownResponse):
        LOG.debug("%s saw agent end: %s", self, response)
        acuid, agent = next(
            (k, v)
            for k, v in self._agents.items()
            if v is not None and response.sender in v.muscles
        )
        del self._agents[acuid]
        if len(self._agents) == 0 and len(self._active_environments) == 0:
            LOG.debug("%s: I'm done.")
            assert self._future_agents_environments_end is not None
            self._future_agents_environments_end.set_result(
                BasicState.STOPPING
            )

    @ESM.requests
    def _request_environment_shutdown(self, environment_uid: str):
        return EnvironmentShutdownRequest(
            sender=self.uid,
            receiver=environment_uid,
            experiment_run_id=self._experiment_run_id,
            experiment_run_instance_id=self._experiment_run_instance_id,
            experiment_run_phase=self._experiment_run_phase,
        )

    @ESM.on(EnvironmentShutdownResponse)
    def _handle_environment_shutdown_response(
        self, response: EnvironmentShutdownResponse
    ):
        LOG.debug("%s saw environment end: %s", self, response)
        self._active_environments -= {response.environment_id}
        if len(self._agents) == 0 and len(self._active_environments) == 0:
            LOG.debug("%s: I'm done.", self)
            assert self._future_agents_environments_end is not None
            self._future_agents_environments_end.set_result(
                BasicState.STOPPING
            )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(uid={self.uid}, agents="
            f"{self._agents}, environments={self._active_environments})"
        )
