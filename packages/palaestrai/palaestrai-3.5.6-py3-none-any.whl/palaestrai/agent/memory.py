from __future__ import annotations
from typing import (
    Any,
    List,
    Tuple,
    Optional,
    Dict,
    Set,
    Union,
    DefaultDict,
)


import itertools
import logging
from dataclasses import dataclass, field, fields
from collections import deque, OrderedDict, defaultdict
import numpy as np
import pandas as pd

from .actuator_information import ActuatorInformation
from .reward_information import RewardInformation
from .sensor_information import SensorInformation

LOG = logging.getLogger(__name__)


@dataclass
class MemoryShard:
    """Collected data from one muscle

    Attributes
    ----------

    sensor_readings : pd.DataFrame
        Column-wise (original) sensor readings as they are provided by the
        environments. Each sensor name is a column; the
        :class:`SensorInformation` objects are stored as-is.
    actuator_setpoints : pd.DataFrame
        Column-wise (original) actuator setpoints. Each actuator name is a
        column; this data frame stores the :class:`ActuatorInformation`
        objects as-is.
    rewards : pd.DataFrame
        Column-wise environment rewards; stores the :class:`RewardInformation`
        objects as-is, with each reward having its own column
    observations : np.ndarray
        Transformed observations: Any data :class:`Muscle` and :class:`Brain`
        want to store
    actions : np.ndarray
        Transformed observations: Any data :class:`Muscle` and :class:`Brain`
        want to store
    objective : np.ndarray
        Result of calling the agent's objective function
    dones : np.ndarray
        Whether the simulation was done at the respective time index or not.
    additional_data : pd.DataFrame
        Any additional data a :class:`Muscle` shares with is :class:`Brain`
    """

    sensor_readings: pd.DataFrame
    actuator_setpoints: pd.DataFrame
    rewards: pd.DataFrame
    dones: np.ndarray
    observations: np.ndarray
    actions: np.ndarray
    objective: np.ndarray
    additional_data: list

    def __len__(self):
        """Number of usable entries in this particular muscle memory

        "Usable" entries are entries that have at least sensor inputs,
        actuator setpoints, and related rewards.
        """
        return len(self.rewards)

    @staticmethod
    def concat(
        memories: Union[List[MemoryShard], Tuple[MemoryShard]]
    ) -> MemoryShard:
        """Concatenate a number of ::`MemoryShard` objects

        All attributes are concatenated in order.
        """

        # Handle special case with len == 0:

        if len(memories) == 0:
            return MemoryShard(
                sensor_readings=pd.DataFrame(),
                actuator_setpoints=pd.DataFrame(),
                rewards=pd.DataFrame(),
                dones=np.array([]),
                observations=np.array([]),
                actions=np.array([]),
                objective=np.array([]),
                additional_data=[],
            )

        # Make sure to keep semantics with the NumPy arrays:

        return MemoryShard(
            sensor_readings=pd.concat(
                [m.sensor_readings for m in memories], ignore_index=True
            ),
            actuator_setpoints=pd.concat(
                [m.actuator_setpoints for m in memories], ignore_index=True
            ),
            rewards=pd.concat(
                [m.rewards for m in memories], ignore_index=True
            ),
            dones=np.concatenate([m.dones for m in memories]),
            observations=np.vstack(
                [
                    np.resize(
                        m.observations,
                        np.max([y.observations.shape[1] for y in memories]),
                    )
                    for m in memories
                ]
            ),
            actions=np.vstack(
                [
                    np.resize(
                        m.actions,
                        np.max([y.actions.shape[1] for y in memories]),
                    )
                    for m in memories
                ]
            ),
            objective=np.concatenate([m.objective for m in memories]),
            additional_data=[
                x
                for x in itertools.chain.from_iterable(
                    m.additional_data for m in memories
                )
            ],
        )


@dataclass
class _MuscleMemory:
    sensor_readings: deque[List[SensorInformation]] = field(
        default_factory=deque
    )
    actuator_setpoints: deque[List[ActuatorInformation]] = field(
        default_factory=deque
    )
    rewards: deque[List[RewardInformation]] = field(default_factory=deque)
    dones: deque[bool] = field(default_factory=deque)
    observations: deque[np.ndarray] = field(default_factory=deque)
    actions: deque[np.ndarray] = field(default_factory=deque)
    objective: deque[np.ndarray] = field(default_factory=deque)
    additional_data: deque[Any] = field(default_factory=deque)

    @staticmethod
    def _get_from_deque(d: deque, item: int, default=None):
        try:
            return d[item]
        except IndexError:
            return default

    @staticmethod
    def _infos_to_df(
        infos: Union[
            List[SensorInformation],
            List[ActuatorInformation],
            List[RewardInformation],
        ]
    ) -> pd.DataFrame:
        data = defaultdict(list)
        for i in infos:
            data[i.uid].append(i.value)
        # The values have to be wrapped into np.ndarrays, because pandas
        # does not infer plain lists with zero dim np.ndarray as np.ndarrays
        # which can cause problems.
        # This is done after the collection of the values, because even though
        # the information uids should be unique, they may be set, which does
        # not guarantee the uniqueness. So the length of the lists may be
        # greater than one.
        wrapped_data: Dict[str, np.ndarray] = {}
        for key, value in data.items():
            # The reshaping only keeps one dimension
            wrapped_data[key] = np.reshape(np.array(value), -1)
        return pd.DataFrame(wrapped_data)

    def __getitem__(self, item: int) -> MemoryShard:
        """Receives a "full row" from the MuscleMemory

        A full row is defined by Rewards being present; other values are either
        retrieved from the memory if present or substituted with (empty)
        default values.

        Returns
        -------
        shard : MemoryShard
            A fully expanded :class:`MemoryShard`
        """
        rewards = self.rewards[item]  # Better fail here directly, if needed.
        sensor_readings = _MuscleMemory._get_from_deque(
            self.sensor_readings, item, []
        )
        actuator_setpoints = _MuscleMemory._get_from_deque(
            self.actuator_setpoints, item, []
        )
        dones = _MuscleMemory._get_from_deque(self.dones, item, [False])
        observations = _MuscleMemory._get_from_deque(
            self.observations, item, [np.NAN]
        )
        actions = _MuscleMemory._get_from_deque(self.actions, item, [np.NAN])
        objective = _MuscleMemory._get_from_deque(
            self.objective, item, [np.NAN]
        )
        additional_data = _MuscleMemory._get_from_deque(
            self.additional_data, item, []
        )
        return MemoryShard(
            sensor_readings=_MuscleMemory._infos_to_df(sensor_readings),
            actuator_setpoints=_MuscleMemory._infos_to_df(actuator_setpoints),
            rewards=_MuscleMemory._infos_to_df(rewards),
            dones=np.array([dones]),
            objective=np.array(objective),  # Shape (1,)
            observations=np.array([observations]),
            actions=np.array([actions]),
            additional_data=additional_data,
        )


class Memory:
    """An in-memory data structure to store experinences in a ::`~Brain`.

    Each agent needs a memory to store experiences, regardless of the training
    algorithm that is used. This class represents this memory. It is an
    in-memory data strcture that uses pandas DataFrames for its public API.
    The memory stores observations, actions, rewards given from the
    envrionment, and the internal reward of the agent (objective value). The
    memory is passed to an :class:`~Objective` to calculate the objective value
    from rewards.

    Parameters
    ----------

    size_limit : int = 1e6
        Maximum size the memory is allowed to grow to until old entries are
        overwritten by new ones.
    """

    def __init__(self, size_limit: int = int(1e6)):
        self.size_limit = size_limit

        self._data: DefaultDict[str, _MuscleMemory] = defaultdict(
            _MuscleMemory
        )
        self._index: deque[str] = deque()

    @property
    def tags(self) -> Set[str]:
        """All tags known to this memory"""
        return set(self._data.keys())

    def append(
        self,
        muscle_uid: str,
        sensor_readings: Optional[List[SensorInformation]] = None,
        actuator_setpoints: Optional[List[ActuatorInformation]] = None,
        rewards: Optional[List[RewardInformation]] = None,
        done: Optional[bool] = None,
        observations: Optional[np.ndarray] = None,
        actions: Optional[np.ndarray] = None,
        objective: Optional[np.ndarray] = None,
        additional_data: Optional[Dict] = None,
    ):
        """Stores a new item in the agent's memory (append)

        An agent has experiences throughout its existence. The memory stores
        those by appending them.
        The memory stores at least those pieces of information that come from
        an environment, which are:

        * sensor readings
        * actuator setpoints (as issued by the agent)
        * rewards
        * whether the simulation has terminated (is "done")

        Readings, setpoints, and rewards are stored in their palaestrAI-native
        objects: :class:`SensorInformation`, :class:`ActuatorInformation`, and
        :class:`RewardInformation`.
        Additionally, an agent (i.e., its muscle) may store its own view in
        terms of transformed values.

        Parameters
        ----------

        muscle_uid : str
            UID of the agent (:class:`Muscle`) whose experiences we store
        sensor_readings : List[SensorInformation]
            A muscle's sensor readings as provided by the environment
        actuator_setpoints : List[ActuatorInformation]
            A muscle's setpoints as provided to an environment
        rewards : List[RewardInformation]
            Rewards issued by the environment. It is not necessary that
            sensor readings, setpoints, and rewards belong to the same
            time step; usually, rewards at a time step ``t`` belong to the
            sensor readings and actions from ``t-1``. This memory class
            correctly correlates rewards to the previous readings/actions.
        done : bool = False
            Whether this was the last action executed in the environment
        observations : Optional[np.ndarray] = None
            Observations the :class:`Muscle` wants to share with its
            :class:`Brain`, e.g., transformed/scaled values
        actions: Optional[np.ndarray] = None,
            Action-related data a :class:`Muscle` emitted, such as
            probabilities, or other data. Can be fed directly to the
            corresponding :class:`Brain`, as with ``observations``
        objective: Optional[np.ndarray] = None
            The agent's objective value describing its own goal. Optional,
            because the agent might calculate such a value separately.
        additional_data : Optional[Dict] = None
            Any additional data a :class:`Muscle` wants to store
        """

        muscle_memory: _MuscleMemory = self._data[muscle_uid]

        # Add everything that we've been supplied with to the respective
        #   muscle memery:

        if sensor_readings is not None:
            muscle_memory.sensor_readings.append(sensor_readings)
        if actuator_setpoints is not None:
            muscle_memory.actuator_setpoints.append(actuator_setpoints)
        if rewards is not None:
            muscle_memory.rewards.append(rewards)
        if additional_data is not None:
            muscle_memory.additional_data.append(additional_data)
        if done is not None:
            muscle_memory.dones.append(done)
        if observations is not None:
            muscle_memory.observations.append(observations)
        if actions is not None:
            muscle_memory.actions.append(actions)
        if objective is not None:
            muscle_memory.objective.append(objective)

        # A "full row" is defined by having rewards supplied. In order to
        #   remember which muscle supplied which values, we index full rows
        #   in self._index. We simply append the muscle name (aka tag) to that
        #   self._index deque.

        if rewards is not None:
            self._index.append(muscle_uid)
        self.truncate(self.size_limit)

    def tail(
        self, n=1, include_only: Optional[List[str]] = None
    ) -> MemoryShard:
        """Returns the n last full entries

        This method returns a nested data frame that returns the n last entries
        from the memory. This method constructs a multi-indexed data frame,
        i.e., a dataframe that contains other dataframes. You access each
        value through the hierarchy, e.g.,

            df = memory.tail(10)
            df.observations.uid.iloc[-1]

        Parameters
        ----------

        n : int = 1
            How many data items to return, counted from the latest addition.
            Defaults to 1.
        include_only : Optional list of str, default: None
            If set, include only data from the given muscles in the list.

        Returns
        -------

        MemoryShard :
            A dataclass that contains the *n* last full entries, i.e.,
            *all* entries where the
            (observations, actions, rewards, objective)
            quadruplet is fully set. I.e., you can be sure that the all
            indexes correspond to each other, and that calling ``iloc``
            with an index really gives you the n-th observation, action, and
            reward for it.
            However, if for whatever reason the environment returned an
            empty reward, this will also be included. This is in contrast to
            the ::`~.sample` method, which will return only entries with where
            an associated reward is also present.
        """

        def yield_tags():
            i = 0
            for t in reversed(self._index):
                if i == n:
                    return
                if include_only and t not in include_only:
                    continue
                yield t
                i += 1

        tags = [t for t in yield_tags()]
        tag_cur_idx: Dict[str, int] = defaultdict(lambda: -1)
        tags_to_query: deque[Tuple[str, int]] = deque()

        for tag in tags:  # reversed(tags):
            idx = tag_cur_idx[tag]
            tags_to_query.append((tag, idx))
            tag_cur_idx[tag] = idx - 1
        return MemoryShard.concat(
            [self._data[t][i] for t, i in reversed(tags_to_query)]
        )

    def truncate(self, n: int):
        """Truncates the memory: Only the last *n* entries are retained.

        Parameters
        ----------
        n : int
            How many of the most recent entries should be retained. Negative
            values of n are treated as ``abs(n)``.
        """
        n = abs(n)
        if len(self) <= n:
            return
        upto_exc = len(self) - n
        for _ in range(upto_exc):
            tag = self._index.popleft()
            mem = self._data[tag]
            _ = mem.rewards.popleft()  # If this crashes, we're in trouble.
            for f in [x for x in fields(mem) if x.name != "rewards"]:
                try:
                    _ = mem.__dict__[f.name].popleft()
                except:
                    pass  # Ok, this may fail

    def __len__(self) -> int:
        """Returns the number of fully usable entries in the memory.

        "Fully usable entries" are those returned by, e.g., ::`~sample()`.
        I.e., the quadruplet of (observation, action, reward, objective).
        """
        return len(self._index)
