from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Tuple, Dict

import uuid
import logging
from abc import ABC, abstractmethod

from palaestrai.types import Mode
from .memory import Memory
from .brain_dumper import BrainDumper

if TYPE_CHECKING:
    from palaestrai.agent import (
        SensorInformation,
        ActuatorInformation,
    )

LOG = logging.getLogger(__name__)


class Muscle(ABC):
    """An acting entity in an environment.

    Each Muscle is an acting entity in an environment: Given a sensor input,
    it proposes actions. Thus, Muscles implement input-to-action mappings.
    A muscle does, however, not learn by itself; for that, it needs a
    :class:`Brain`. Every time a Muscle acts, it sends the following inputs
    to a :class:`Brain`:

    * Sensor inputs it received
    * actuator set points it provided
    * reward received from the proposed action.

    When implementing an algorithm, you have to derive from the Muscle ABC and
    provide the following methods:

    #. :func:`~propose_actions`, which implements the input-to-action mapping
    #. :func:`~update`, which handles how updates from the :class:`Brain` are
       incorporated into the muscle.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._uid: str = f"Muscle-{str(uuid.uuid4())[-6:]}"
        self._mode: Mode = Mode.TRAIN
        self._memory: Memory = Memory()
        self._model_loaders: List[BrainDumper] = []
        self._statistics: Dict[str, Any] = {}

    @property
    def uid(self):
        """Unique user-defined ID of this Muscle

        This is the name of the agent, i.e., what has been defined by a
        user in an :class:`ExperimentRun` file.

        Returns
        -------
        uid: str
            The user-defined name of the Muscle
        """
        return self._uid

    @property
    def name(self):
        """User-defined name of this Muscle, as given in the experiment run"""
        return self._uid  # There should be no difference.

    @property
    def mode(self) -> Mode:
        """Internal mode of operations

        Usually, an agent operates under the assumption of a certain modus
        operandi.
        This can be, for example, the distinction between training (
        ::`Mode.TRAIN`) and testing (::`Mode.TEST`).

        Returns
        -------
        ::`Mode`
            The agent's operations mode
        """
        return self._mode

    @property
    def memory(self) -> Memory:
        """Muscle :class:`Memory`.

        Each Muscle can have its own, personal :class:`Memory`.
        Internally, the memory stores sensor readings, actuator setpoints
        provided by the Muscle, as well as rewards from the environment and
        the result of the Muscle's (i.e., Agent's) objective function.

        Return
        ------
        Memory
            The Muscle :class:`Memory`.
        """
        assert self._memory is not None
        return self._memory

    def setup(self):
        """Generic setup method, called just before ::`~Muscle.run`

        This method is called just before the main loop in ::`~Muscle.run`
        commences. It can be used for any setup tasks. The method is
        guranteed to be called in the same process as the main loop. Also, the
        communications link to the brain will already be established.
        However, there are no information about the environment available yet.

        There is no need to load the muscle's inference model here;
        refer to ::`~Muscle.prepare_model` for this.
        """
        pass

    @abstractmethod
    def propose_actions(
        self,
        sensors: List[SensorInformation],
        actuators_available: List[ActuatorInformation],
    ) -> Tuple[List[ActuatorInformation], Any]:
        """Process new sensor information and produce actuator setpoints.

        This method provides the essential inference task of the Muscle:
        It takes current sensor information and is expected to produce a
        list of actuator setpoints that can be applied in the ::`Environment`.
        How the actuator values are produced and how the sensor information
        are processed is up to the developer.

        This is the essential abstract method that needs to be implemented by
        every Muscle.

        Sensor readings and the list of available actuators are valid for the
        current time.
        Previous sensor readings, rewards, and objective value can be
        retrieved from the Muscle's ::`Memory`,
        which is accessible through the ::`Muscle.memory` property.

        Parameters
        ----------
        sensors : list of SensorInformation
            List of new SensorInformation for all available sensors
        actuators_available : list of ActuatorInformation
            List of all actuators that are *currently* available to the agent

        Returns
        -------
        tuple of two elements
            A Tuple containing: (1) The actual setpoints (an list of
            ::`ActuatorSetpoint` objects), for which it is allowed to simply
            use the objects that are passed as parameters, deep-copying is not
            necessary; (2) any other data that should be sent to the
            Muscle's ::`Brain`.
        """
        pass

    def update(self, update: Any):
        """Update the Muscle.

        This method is called if the brain sends an update.
        What is to be updated is up to the specific implementation.
        However, this method should update all necessary components.

        There might be implementations of :class:`Brain` and Muscles where
        updates do not happen.
        Simple, static bots never learn, and, therefore, do not need a
        mechanism for updates.
        Therefore, the default implementation of this method is simply to
        not do anything.

        Parameters
        ----------
        update: any
            Any data that a :class:`Brain` would send to its Muscles upon an
            update. Implementation-specific.
        """
        pass

    def reset(self):
        """Called in order to reset the Muscle.

        There is a number of occasions in which the Muscle should stay active,
        but reset.
        For example, when a new episode of the same experiment run phase is
        started.
        Then, the Muscle is allowed (or better, encouraged) to keep its state,
        but acknowledge that a reset has occured and the Muscle does not expect
        the seamless continuation of an episode.
        Implementing this method is optional; if it is not implemented, nothing
        will happen on reset and the Muscle will also be kept as-is.
        """
        pass

    def teardown(self):
        """Called just before the Muscle is shut down

        Just before the ::`~RolloutWorker` shuts down, it calls this method
        on the Muscle.
        If the method is not implemented, nothing happens; i.e., implementing
        this method is optional.
        However, in cases where some last-minute cleanups need to be done,
        this method is the right place to do it.
        """
        pass

    def load(self, tag: str) -> Any:
        bio = BrainDumper.load_brain_dump(self._model_loaders, tag)
        try:
            assert bio is not None
            bio.seek(0)
        except Exception:
            # We just want to be nice and serviceable. If it isn't possible,
            #   don't fret, no harm done.
            pass
        return bio

    def prepare_model(self):
        """Loading a trained model for testing

        This method loads dumped brain states from a given previous phase, or
        even experiment run. For details, see the documentation on experiment
        run files (the ``load`` key).

        This method is called whenever the current state of a muscle model
        should be restored. How a particular model is deserialized is up to the
        concrete implementation. Also, brains may be divided into sub-models
        (e.g., actor and critic), whose separate storage is realized via tags.
        Implementing this method allows for a versatile implementation of this.

        It is advisable to use the storage facilities of palaestrAI.
        These are available through ::`Muscle.load`. The model location has
        then been pre-set from the experiment run file.
        """
        pass

    def add_statistics(self, key: str, value: Any, allow_overwrite=False):
        """Statistics dict

        Each Muscle can have its own statistic metrics, that are calculated
        with each step, i.e., after each call of :func:`propose_actions`.
        The :class:`Brain` can provide occasionally calculated statistics via
        an update to the Muscle. The Muscle then can choose to update its
        statistics for storing.
        """
        assert self._statistics is not None and isinstance(
            self._statistics, Dict
        ), (
            f"Invalid internal variable Muscle._statistics format:"
            f" {type(self._statistics)}, expected non-None 'Dict'"
        )
        assert key is not None and isinstance(
            key, str
        ), f"Invalid key format: {type(key)}, expected 'str'"

        assert allow_overwrite or key not in self._statistics, (
            f"Tried to overwrite statistics for {key}. "
            f"Use 'allow_overwrite' to replace values."
        )
        self._statistics[key] = value

    def pop_statistics(self) -> Dict[str, Any]:
        """Returning current statistics and resetting it

        This method returns the statistics dict and clears it afterwards.

        Because the statistics dict should contain metrics that refer
        to one step, it is stored and cleared after each one.

        Returns
        -------
        Dict
            The dict contains a mapping of metric keys to values. This
            dynamically allows various implementation-dependent statistics
            metrics.
        """
        statistics = self._statistics
        self._statistics = {}

        return statistics

    def __str__(self):
        return f"{self.__class__}(id=0x{id(self):x}, uid={self.uid})"
