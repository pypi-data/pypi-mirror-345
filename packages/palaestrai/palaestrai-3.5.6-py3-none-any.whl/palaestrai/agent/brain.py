"""This module contains the abstract class :class:`Brain` that is used
to implement the thinking part of agents.

"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Dict

import logging
import warnings
from pathlib import Path
from abc import ABC, abstractmethod

from .brain_dumper import BrainDumper
from .memory import Memory
from palaestrai.types import Mode
from palaestrai.core import RuntimeConfig

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from . import SensorInformation, ActuatorInformation, Objective


class Brain(ABC):
    """Baseclass for all brain implementation

    The brain is the central learning instance. It coordinates all
    muscles (if multiple muscles are available). The brain does all
    (deep) learning tasks and delivers a model to the muscles.

    The brain has one abstract method :meth:`.thinking` that has to be
    implemented.

    Brain objects store their state and can re-load previous states by using
    the infrastructure provided by the :class:`~BrainDumper` infrastructure.
    For this, concrete Brain classes need to provide implementations of
    :meth:`~Brain.load` and :meth:`~Brain.store`.
    """

    def __init__(self):
        self._seed: int = -1
        self._name: str = ""
        self._memory = Memory()
        self.mode: Mode = Mode.TRAIN
        self._statistics: Dict[str, Any] = {}
        self._sensors: List[SensorInformation] = []
        self._actuators: List[ActuatorInformation] = []

        # Some IO object to which we can dump ourselves for a freeze:
        self._dumpers: List[BrainDumper] = list()

    @property
    def name(self) -> str:
        """Name of this agent"""
        return self._name

    @property
    def seed(self) -> int:
        """Returns the random seed applicable for this brain instance."""
        return self._seed

    @property
    def sensors(self) -> List[SensorInformation]:
        """All sensors the Brain (and its Muscles) know about"""
        return self._sensors

    @property
    def actuators(self) -> List[ActuatorInformation]:
        """All actuators a Muscle can act with."""
        return self._actuators

    @property
    def memory(self) -> Memory:
        """The Brain's memory"""
        return self._memory

    def setup(self):
        """Brain setup method

        This method is called by the :class:`~AgentConductor` just before
        the main loop is intered (:meth:`~Brain.run`). In the base Brain class,
        it is empty and does nothing. However, any derived class may implement
        it to do local setup before the main loop is entered.

        Potential tasks that could be done in this method is to set the
        size limit of the :class:`Memory` via ::`Memory.size_limit`,
        or anything that needs to access the ::`Brain.seed`, ::`Brain.sensors`,
        or ::`Brain.actuators`, as they're not yet available in the constructor.


        This method is guaranteed to be called in the same process space as
        the main loop method, :meth:`Brain.run`.
        """
        pass

    @abstractmethod
    def thinking(
        self,
        muscle_id: str,
        data_from_muscle: Any,
    ) -> Any:
        """Think about a response using the provided information.

        The :meth:`.thinking` method is the place for the
        implementation of the agent's/brain's logic. The brain can
        use the current sensor readings, review the actions of the
        previous thinking and consider the reward (provided by the
        objective).

        Usually, this is the place where machine learning happens,
        but other solutions are possible as well (like a set of rules
        or even random based results).

        The method receives only the name of the :class:`Muscle` that is
        sending data, along with whatever data this :class:`Muscle` wants to
        send to the Brain. As this is completely implementation-specific,
        this method does not impose any restrictions.

        Any data that is available to palaestrAI, such as the actual sensor
        readings, setpoints a Muscle provided, rewards, the objective
        function's value (goal/utility function), and whether the simulation is
        *done* or not, is available via the Brain's :class:`Memory`
        (cf. ::`Brain.memory`).

        Parameters
        -------
        muscle_id : str
            This is the ID of the muscle which requested the update
        data_from_muscle: Any
            Any data the :class:`Muscle` sends to the Brain

        Returns
        -------
        Any
            Any update that the :class:`Muscle`. If this value does not
            evaluate to ``True`` (i.e., ``bool(update) == False``), then the
            :class:`Muscle` will not be updated.
        """
        pass

    def pretrain(self):
        """Pretrains the Brain *before* an experiment begins (Offline Learning)

        The :class:`~Learner` will have filled the Brain's :class:`Memory` with
        previous trajectories it can access.
        These trajectories are loaded according to the ``replay`` key in the
        experiment run file.
        How the pretraining (in DRL parley, known as *Offline Learning*) is
        actually conducted is up to the algorithm.
        I.e., concrete algorithm implementations may overwrite this method
        if they wish to implement pretraining/offline training.
        """
        LOG.debug(
            "%s could pretrain now, but no implementation was "
            "provided. The Brain's memory size is: %d",
            self,
            len(self._memory),
        )

    def try_load_brain_dump(self):
        LOG.debug(
            "%s tries to load a previous braindump from any of %s.",
            self,
            self._dumpers,
        )
        if any(d for d in self._dumpers if d._brain_source):
            try:
                self.load()
            except AttributeError:
                # This happens because somebody forgot to check whether loader
                # returned None...
                LOG.error(
                    "%s tried to load a brain dump, but that seemed to have "
                    "failed. However, instead of a sane reboot, the brain "
                    "never checked whether the loader returned 'None'. So, "
                    "the loading failed completely. Don't blame me, blame the "
                    "implementor. My brain will go on, but don't expect a "
                    "happy-end from me.",
                    self,
                )

    def store(self):
        """Stores the current state of the model

        This method is called whenever the current state of the brain should
        be saved. How a particular model is serialized is up to the concrete
        implementation. Also, brains may be divided into sub-models (e.g.,
        actor and critic), whose separate storage is relized via tags.
        Implementing this method allows for a versatile implementation of this.

        It is advisable to use the storage facilities of palaestrAI. They are
        available through the method
        :meth:`~BrainDumper.store_brain_dump(binary_io, self._dumpers, tag)`.
        This function calls all available dumpers to store the serialized
        brain dump provided in the parameter ``binary_io`` and optionally
        attaches a ``tag`` to it. The attribute ::`~Brain._dumpers` is
        initialized to a list of available dumpers and can be used directly.
        """
        try:
            # Try to be backwards compatible and call the old store_model
            # method as a default implementation
            if self._dumpers:
                locator = self._dumpers[0]._brain_destination
                path = (
                    Path(RuntimeConfig().data_path).resolve()
                    / "brains"
                    / locator.experiment_run_uid
                    / str(locator.experiment_run_phase)
                    / str(locator.agent_name)
                )
            else:
                path = RuntimeConfig().data_path
            path.mkdir(parents=True, exist_ok=True)
            self.store_model(path)
            LOG.warning(
                "%s uses deprecated storage API, please upgrade to "
                "store()/load().",
                self,
            )
        except Exception as e:
            # This okay, sorts of. It means that the brain does not implement
            # any way of storing its state, which might be okay as well...
            LOG.warning(
                "%s does not implement store(); its current state "
                "cannot be saved. Please provide an implementation of "
                "%s.store(). Providing an empty one silences this "
                "warning. (Error message was: %s)",
                self,
                self,
                e,
            )
            pass

    def load(self):
        """Loads the current state of the model

        This method is called whenever the current state of the brain should
        be restored. How a particular model is deserialized is up to the
        concrete implementation. Also, brains may be divided into sub-models
        (e.g., actor and critic), whose separate storage is relized via tags.
        Implementing this method allows for a versatile implementation of this.

        It is advisable to use the storage facilities of palaestrAI. They are
        available through the method
        :meth:`~BrainDumper.load_brain_dump(self._dumpers, tag)`.
        This function calls all available dumpers to restore the serialized
        brain dump (optionally identified via a ``tag``). It returns a
        BinaryIO object that can then be used in the implementation. The
        attribute ::`~Brain._dumpers` is initialized to the list of available
        dumpers/loaders.
        """
        try:
            # Try to be backwards compatible and call the old load_model
            # method as a default implementation
            if self._dumpers and self._dumpers[0]._brain_source:
                locator = self._dumpers[0]._brain_source
                path = (
                    Path(RuntimeConfig().data_path).resolve()
                    / "brains"
                    / locator.experiment_run_uid
                    / str(locator.experiment_run_phase)
                )
            else:
                path = RuntimeConfig().data_path
            self.load_model(path)
            LOG.warning(
                "%s uses deprecated storage API, please upgrade to "
                "store()/load().",
                self,
            )
        except Exception as e:
            # This okay, sorts of. It means that the brain does not implement
            # any way of storing its state, which might be okay as well...
            LOG.warning(
                "%s does not implement load(); its current state cannot"
                " be loaded. Please provide an implementation of "
                "%s.load(). Providing an empty one silences this "
                "warning. (Error message was: %s)",
                self,
                self,
                e,
            )
            pass

    def load_model(self, path):
        warnings.warn(
            "Brain.load_model is deprecated and will be removed in "
            "palaestrAI 4.0. Please use the new store()/load() "
            "infrastructure instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )

    def store_model(self, path):
        warnings.warn(
            "Brain.store_model is deprecated and will be removed in "
            "palaestrAI 4.0. Please use the new store()/load() "
            "infrastructure instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )

    def add_statistics(self, key: str, value: Any, allow_overwrite=False):
        """Add statistics for later analysis

        Each Brain can have its own statistic metrics, which are calculated
        for a step (i.e., a call to ::`~thinking`). This can be used to
        store training error or any other value you'd later want to analyze
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
        return "%s(id=0x%x)" % (self.__class__, id(self))
