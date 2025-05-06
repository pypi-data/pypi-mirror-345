from __future__ import annotations

import inspect
import logging
import typing
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Sequence,
    Union,
)
from warnings import warn

from palaestrai.core import EventStateMachine as ESM
from palaestrai.core.protocol import (
    EnvironmentResetRequest,
    EnvironmentResetResponse,
    EnvironmentShutdownRequest,
    EnvironmentShutdownResponse,
    EnvironmentStartRequest,
    EnvironmentStartResponse,
    EnvironmentUpdateRequest,
    EnvironmentUpdateResponse,
)
from palaestrai.types import SimTime, SimulationFlowControl

from .environment_baseline import EnvironmentBaseline
from .environment_state import EnvironmentState

if TYPE_CHECKING:
    from ..agent import (
        ActuatorInformation,
        RewardInformation,
        SensorInformation,
    )
    from .environment_state_transformer import EnvironmentStateTransformer
    from .reward import Reward

LOG = logging.getLogger(__name__)


@ESM.monitor(is_mdp_worker=True)
class Environment(ABC):
    """Abstract class for environment implementation

    This abstract calls provides all necessary functions needed
    to implement a new environment. The developer only has to
    implement the functions start_environment and update.

    Parameters
    ----------
    uid : str
        Unique identifier to identify an environment

    Attributes
    ----------
    reward : ::`Reward`
        If present, this method calculates the reward of the environment (
        ("external reward"). See ::`EnvironmentState.world_state`.
    _sensor_ids: List[str]
        A list of sensor IDs including the UID of the environment.
    _actuator_ids: List[str]
        A list of actuator IDs including the UID of the environment.
    """

    def __init__(
        self,
        uid: str,
        *args,
        **kwargs,
    ):
        self._uid = uid
        self._name: str = ""
        self._done = False
        if "seed" in kwargs:
            self.seed = kwargs["seed"]
        elif len(args) > 0 and isinstance(
            args[1], int
        ):  # very hacky, just to see if MosaikEnvironment still breaks
            self.seed = args[1]

        if "broker_uri" in kwargs:
            warn(
                "broker_uri is deprecated, please update your environment.",
                DeprecationWarning,
            )
        self.reward: Optional[Reward] = None
        self.sensors: List[SensorInformation] = []
        self.actuators: List[ActuatorInformation] = []
        self._state_transformer: Optional[EnvironmentStateTransformer] = None

        # Filter lists for incoming actuators
        self._sensor_ids: List[str] = list()
        self._actuator_ids: List[str] = list()

        self._tick = 0

        LOG.debug("%s created", self)

    @property
    def done(self) -> bool:
        """Checks whether the environment has terminated"""
        return self._done

    @property
    def uid(self) -> str:
        """The unique identifier of the Environment object"""
        return str(self._uid)

    @property
    def name(self) -> str:
        """User-given name of this environment"""
        return self._name

    def setup(self):
        self.mdp_service = self.uid
        LOG.debug("%s started", self)

    def _remove_uid(
        self, actuator_information_list: List[ActuatorInformation]
    ):
        for i in actuator_information_list:
            if isinstance(i, (int, float)):
                continue
            if i.uid.startswith(f"{self._name}."):
                # Sensor/Actuators themselves may also contain a dot. Only up
                # to the first dot we have the environment's UID:
                i.uid = ".".join(i.uid.split(".", 1)[1:])

    def _prepend_uid(
        self,
        sensor_actuator_information_list: Sequence[
            Union[SensorInformation, ActuatorInformation]
        ],
    ):
        for i in sensor_actuator_information_list:
            if isinstance(i.uid, (int, float)):
                i.id = f"{i.uid}"

            if isinstance(i.uid, str) and i.uid.startswith(f"{self._name}."):
                continue

            i.uid = f"{self._name}.{i.uid}"

    @ESM.on(EnvironmentStartRequest)
    async def _handle_setup(
        self, request: EnvironmentStartRequest
    ) -> EnvironmentStartResponse:
        """Handle an environment start request.

        The :meth:`.start_environment` is called that can be used by
        environments for setup purposes and that should provide the
        available sensors and actuators.

        Finally, a start response is prepared.

        Parameters
        ----------
        request: EnvironmentStartRequest
            The start request from the simulation controller.

        Returns
        -------
        EnvironmentStartResponse
            The answer from the environment, contains the available
            sensors and actuators.

        """
        LOG.debug(
            "Environment %s received a %s",
            self,
            repr(request),
        )

        # Start environment, return baseline; then,
        # prepend our UID to it to allow a sensor/actuator to be
        # distinguished by its containing environment.

        simtime = (
            inspect.signature(EnvironmentStartResponse)
            .parameters["simtime"]
            .default
        )
        if inspect.iscoroutinefunction(self.start_environment):
            baseline = await self.start_environment()
        else:
            baseline = self.start_environment()
        if isinstance(baseline, tuple):
            sensors, actuators = baseline
        elif isinstance(baseline, EnvironmentBaseline):
            sensors = baseline.sensors_available
            actuators = baseline.actuators_available
            simtime = baseline.simtime
        else:  # Wtf?!
            raise RuntimeError(
                "Unknown return value from environment start: %s "
                % (str(baseline))
            )
        sensors = deepcopy(sensors)
        actuators = deepcopy(actuators)
        self._prepend_uid([*sensors, *actuators])

        self._sensor_ids = [sen.uid for sen in sensors]
        self._actuator_ids = [act.uid for act in actuators]
        self._done = False

        LOG.info("Environment %s has been set up.", self)

        return EnvironmentStartResponse(
            sender_environment=self.uid,
            receiver_simulation_controller=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
            sensors=sensors,
            actuators=actuators,
            simtime=simtime,
        )

    @ESM.on(EnvironmentUpdateRequest)
    async def _handle_update(
        self, request: EnvironmentUpdateRequest
    ) -> EnvironmentUpdateResponse:
        """Handle an environment update request.

        The request contains current actuator values and the
        environment receives the actuator values in the update method.
        The environment answers with updated sensor readings, an
        environment reward, and the done flag, whether the
        environment has finished or not.

        Finally, an update response is prepared.

        Parameters
        ----------
        request: EnvironmentUpdateRequest
            The update request from the simulation controller, contains
            the current actuator values from one or more agent.

        Returns
        -------
        EnvironmentUpdateResponse
            The response for the simulation controller, containing the
            updated sensor values, a reward, and the done flag.

        """
        if self._done:
            LOG.critical(
                "Environment worker %s received an update even though it "
                "is already done! Bailing out.",
                self.uid,
            )
            raise RuntimeError(
                f"Environment {self.uid} updated "
                f"even though it is already done."
            )
        actuators = [
            act for act in request.actuators if act.uid in self._actuator_ids
        ]
        actuators = deepcopy(actuators)
        self._remove_uid(actuators)

        self._tick += 1
        if inspect.iscoroutinefunction(self.update):
            state = await self.update(actuators)
        else:
            state = self.update(actuators)

        if isinstance(state, tuple):  # Handle old-style updates by upgrade:
            state = EnvironmentState(
                sensor_information=deepcopy(state[0]),
                world_state=deepcopy(state[0]),
                rewards=state[1],
                done=state[2],
                simtime=SimTime(simtime_ticks=self._tick),
            )
        elif isinstance(state, EnvironmentState):
            pass  # No conversion to do
        else:  # Wtf?!
            raise RuntimeError(
                "Unknown return value from environment update: %s "
                % (str(state))
            )

        self._prepend_uid(state.sensor_information)
        if self._state_transformer:
            state = self._state_transformer(state)

        LOG.debug("%s got stepped on: %s", self, request)

        self._done = state.done
        fci = (
            SimulationFlowControl.RESET
            if self._done
            else SimulationFlowControl.CONTINUE
        )
        return EnvironmentUpdateResponse(
            sender_environment_id=self.uid,
            receiver_simulation_controller_id=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
            environment_name=self._name,
            sensors=state.sensor_information,
            rewards=state.rewards,
            world_state=state.world_state,
            done=state.done,
            flow_control_indicator=fci,
            flow_control_data={
                "EnvironmentTerminationCondition": (
                    fci,
                    {self.uid: fci},
                )
            },  # TODO: Add termination conditions to envs
            simtime=state.simtime,
        )

    @ESM.on(EnvironmentResetRequest)
    async def _handle_reset(
        self, request: EnvironmentResetRequest
    ) -> EnvironmentResetResponse:
        """Handle an environment reset request.

        The actual behavior of the restart is delegated to the method
        :meth:`reset`.

        Parameters
        ----------
        request: EnvironmentResetRequest
            The reset request send by the simulation controller.

        Returns
        -------
        EnvironmentResetResponse
            The response for the simulation controller.

        """
        LOG.info(
            'Environment worker "%s" for environment "%s" resetting.',
            self.uid,
            self.name,
        )
        self._tick = 0
        self._done = False
        if inspect.iscoroutinefunction(self.reset):
            state = await self.reset(request)
        else:
            state = self.reset(request)  # type: ignore[assignment]
        return state

    @ESM.on(EnvironmentShutdownRequest)
    async def _handle_shutdown(
        self, request: EnvironmentShutdownRequest
    ) -> EnvironmentShutdownResponse:
        """Handle an environment shutdown request.

        The :meth:`shutdown` is called that handles the shutdown of the
        environment. Finally, a shutdown response is prepared.

        Parameters
        ----------
        request: EnvironmentShutdownRequest
            The shutdown request from the simulation controller.

        Returns
        -------
        EnvironmentShutdownResponse
            The shutdown response for the simulation controller.

        """
        LOG.info("Environment %s now handling shutdown.", self)
        if inspect.iscoroutinefunction(self.shutdown):
            await self.shutdown()
        else:
            self.shutdown()
        self.stop()  # type: ignore
        return EnvironmentShutdownResponse(
            sender=self.uid,
            receiver=request.sender,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
        )

    @abstractmethod
    def start_environment(
        self,
    ) -> Union[
        EnvironmentBaseline,
        typing.Tuple[List[SensorInformation], List[ActuatorInformation]],
    ]:
        """Launches execution of an environment.

        If the environment uses a simulation tool, this function
        can be used to initiate the simulation tool. In addion, this
        function is used to prepare the environment for the simulation.
        It must be able to provide initial sensor information.

        On a reset, this method is called to restart a new environment
        run. Therefore, it also must provide initial values for all
        variables used!

        Returns
        -------
        Union[EnvironmentBaseline,
        typing.Tuple[List[SensorInformation], List[ActuatorInformation]]]
            An :class:`~EnvironmentBaseline` object containing all initial data
            from the environment. For backwards compatibility, it is also
            possible (though deprecated) to return a tuple containing a list
            of available sensors and a list of available actuators.
        """
        pass

    @abstractmethod
    def update(self, actuators: List[ActuatorInformation]) -> Union[
        EnvironmentState,
        typing.Tuple[List[SensorInformation], List[RewardInformation], bool],
    ]:
        """Function to update the environment

        This function receives the agent's actions and has to respond
        with new sensor information. This function should create a
        new simulation step.

        Parameters
        ----------
        actuators : List[ActuatorInformation]
            List of actuators with values

        Returns
        -------
        Union[EnvironmentState,
        typing.Tuple[List[SensorInformation], List[RewardInformation], bool]]
            An :class:`~EnvironmentState` object; for backwards compatibility,
            environments can return a tuple containing a list of
            sensor readings (:class:`~SensorInformation`), a list of rewards
            (:class:`~RewardInformation`), and a flag whether the
            environment has terminated. Returning a tuple is considered
            deprecated.
        """
        pass

    def shutdown(self) -> None:
        """Function to handle shutdown procedure of the environment

        This function allows to perform a graceful shutdown of the
        current environment process. It does not prevent another
        call of :meth:`start_environment` in case of a reset.

        An implementation is optional.
        """
        pass

    async def reset(
        self, request: EnvironmentResetRequest
    ) -> EnvironmentResetResponse:
        """Resets the environment in-place.

        The default behavior for a reset comprises:

        * calling shutdown to allow a graceful shutdown of
          environment simulation processes
        * calling :meth:`~.start_environment` again
        * preparing the :class:`EnvironmentResetResponse`

        If an environment requires a more special reset procedure,
        this method can be overwritten.

        Parameters
        ----------
        request : EnvironmentResetRequest
            The reset request send by the simulation controller.

        Returns
        -------
        EnvironmentResetResponse
            The response for the simulation controller.
        """
        LOG.debug(
            "Environment %s stopped the leftovers "
            "of the previous run. Initiating a new run now.",
            self,
        )

        simtime = (
            inspect.signature(EnvironmentResetResponse)
            .parameters["simtime"]
            .default
        )
        if inspect.iscoroutinefunction(self.shutdown):
            await self.shutdown()
        else:
            self.shutdown()
        if inspect.iscoroutinefunction(self.start_environment):
            baseline = await self.start_environment()
        else:
            baseline = self.start_environment()
        if isinstance(baseline, tuple):
            sensors, actuators = baseline
        elif isinstance(baseline, EnvironmentBaseline):
            sensors = baseline.sensors_available
            actuators = baseline.actuators_available
            simtime = baseline.simtime
        else:  # Wtf?!
            raise RuntimeError(
                "Unknown return value from environment start: %s "
                % (str(baseline))
            )

        sensors = deepcopy(sensors)
        actuators = deepcopy(actuators)
        self._prepend_uid([*sensors, *actuators])

        LOG.info('Environment worker "%s" restarted.', self.uid)

        return EnvironmentResetResponse(
            receiver_simulation_controller_id=request.sender,
            sender_environment_id=self.uid,
            experiment_run_id=request.experiment_run_id,
            experiment_run_instance_id=request.experiment_run_instance_id,
            experiment_run_phase=request.experiment_run_phase,
            create_new_instance=False,
            environment_name=self.name,
            sensors=sensors,
            actuators=actuators,
            simtime=simtime,
        )

    def __str__(self):
        return f"{self.__class__.__name__}(id=0x{id(self):x}, uid={self.uid}, tick={self._tick})"
