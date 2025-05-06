"""Serializing targets for dumping the state of a brain."""

from __future__ import annotations

import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO, Optional, List

from palaestrai.types import ExperienceLocation

LOG = logging.getLogger(__name__)


@dataclass
class BrainLocation(ExperienceLocation):
    """Locates a ::`~Brain` dump in terms of agent, experiment run, and phase.

    To dump or load a :class:`~Brain`, it needs to be located. The locator
    is represented by instances of this class. A brain is local to a specific
    agent, is used and/or trained in a particular experiment run and run phase.

    The information for this comes from the experiement run definition, i.e.,
    the experiment run document (usually written down in YAML format). All
    UIDs referenced here are user-readable IDs. Examples are "Dummy run",
    "phase_0", and "valiant_defender" for experiment run, phase, and
    agent UIDs.

    Parameters
    ----------

    agent_name : str
        Unique name (ID) of the agent that housed the :class:`~Brain` this
        locator refers to. The key in the experiment run file is ``agent``.
    experiment_run_uid : str
        UID (user defined, unique ID) of the experiment run the brain is
        located in. The key in the experiment run file is ``experiment_run``.
    experiment_run_phase : int
        Number (index, starting at 0) of the experiment run phase the brain
        is located in. The key in the experiment run file is ``phase``.
    """

    agent_name: str
    experiment_run_uid: str
    experiment_run_phase: int


class NoBrainLocatorError(RuntimeError):
    def __init__(self):
        super().__init__("No brain location specified, cannot store or load")


class NoBrainFoundError(RuntimeError):
    def __init__(self, locator: BrainLocation):
        super().__init__(
            f"No brain data found at the given location {locator}"
        )
        self.locator = locator


class BrainDumper(ABC):
    """Represents a strategy to dump the state of a :class:`~Brain`

    Child classes define concrete methods to :meth:`~BrainDumper.dump` and
    :meth:`~BrainDumper.load` a ::`~Brain`\ 's state.

    The brain dumper is constructed with past and current location of
    brains. These locations are described by a :class:`~BrainLocation` and
    locate a brain in terms of agent, experiment run, and run phase. Within
    these locations, different brain versions can be loaded or stored based
    on tags. Tags can be, e.g., actor and critic networks for certain DRL
    algorthms.
    """

    def __init__(
        self, dump_to: BrainLocation, load_from: Optional[BrainLocation] = None
    ):
        """Construct a new dumper with source and destination locator

        Parameters
        ----------

        dump_to : BrainLocation
            Where to dump a :class:`~Brain` to.
        load_from : BrainLocation
            Where to read the brain from, when a serialized brain state is
            queried.
        """
        self._brain_source = load_from
        self._brain_destination = dump_to

    @abstractmethod
    def save(self, brain_state: BinaryIO, tag: Optional[str] = None):
        """Saves a given ::`~Brain`\ 's state.

        Parameters
        ----------

        brain_state : BinaryIO
            The serialized bytes representation of the brain.
        tag : str, default: None
            A tag for further distinguishing between different versions of
            the brain.
        """
        pass

    def load(self, tag: Optional[str] = None) -> BinaryIO:
        """Loads a serialized brain

        This method loads a serialized brain state. The medium is up to the
        concrete implementation. However, the dumper does not restore the
        brain, i.e., turn it into a Python structure again. That is the
        responsibility of a concrete ::`~Brain` implementation.

        Parameters
        ----------

        tag : Optional[str], default: None
            A tag for further distinguishing between different versions of
            the brain.

        Returns
        -------

        BinaryIO :
            The read (serialized) brain dump
        """
        if self._brain_source is None:
            LOG.error("%s could not load brain: No locator given.", self)
            raise NoBrainLocatorError()
        bio = self._load(self._brain_source, tag)
        bio.seek(0)
        return bio

    @abstractmethod
    def _load(
        self, source_locator: BrainLocation, tag: Optional[str] = None
    ) -> BinaryIO:
        """Implementation of the brain loading

        This is the abstract method that concrete classes must implement in
        order to faciliate loading of brain states. The public
        :meth:`~BrainLoader.load` method acts as wrapper that implements a
        number of convenience checks, such as whether a source locator was
        passed to the constructor.

        Parameters
        ----------

        source_locator : BrainLocation
            Locator information for the brain's whereabouts
        tag : Optional[str], default: None
            A tag for further distinguishing between different versions of
            the brain.

        Returns
        -------

        BinaryIO :
            The read (serialized) brain dump
        """
        pass

    @staticmethod
    def load_brain_dump(
        loaders: List[BrainDumper], tag: Optional[str] = None
    ) -> Optional[BinaryIO]:
        """Iterates over a list of ::`BrainDumper`\ s to load a brain."""
        if not loaders:
            LOG.warning(
                "Should load a previous state, but there are no "
                "loaders available. Intended or a weird case of "
                "amnesia?"
            )
            return io.BytesIO()
        for loader in loaders:
            try:
                bio = loader.load(tag)
                bio.seek(0)  # Just to make sure.
                LOG.info("Reloaded brain dump from %s", loader)
                return bio
            except Exception as e:
                # We catch anything here.
                LOG.warning("Failed to load brain dump from %s: %s", loader, e)
        LOG.warning(
            "We should load a brain dump, "
            "but none of the loaders (%s) could provide any data. I will "
            "suffer from amnesia.",
            loaders,
        )
        return None

    @staticmethod
    def store_brain_dump(
        brain_state: BinaryIO,
        dumpers: List[BrainDumper],
        tag: Optional[str] = None,
    ):
        """Stores the brain dump in all given storage back-ends.

        Given a list of ::`~BrainDumper` implementations, this method will
        store the supplied brain state in all of them, if possible. Failed
        storage backends will be reported, but an error is only raised of no
        storage backend succeeded.

        Parameters
        ----------

        brain_state : BinaryIO
            The state of the brain, in a dumpable format.
        dumpers : List[BrainDumper]
            List of all brain dumpers that should be tried, in order.
        tag : Optional[str]
            An optional string serving as a tag
        """
        failed_dumpers = []
        succeeded_dumpers = []
        for dumper in dumpers:
            brain_state.seek(0)
            try:
                dumper.save(brain_state, tag)
                succeeded_dumpers += [dumper]
            except Exception as e:
                LOG.error("Could not dump to %s: %s", repr(dumper), e)
                failed_dumpers += [dumper]
        if failed_dumpers and succeeded_dumpers:
            LOG.warning(
                "Could not dump to some dumpers: %s. "
                "The following ones succeeded: %s",
                failed_dumpers,
                succeeded_dumpers,
            )
        if failed_dumpers and not succeeded_dumpers:
            LOG.critical(
                "Could not dump with any of the dumpers: %s. "
                "Loading in the next experiment run phase will not work.",
                failed_dumpers,
            )
