from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ExperienceLocation:
    """Location information for experiences, e.g., ::`~Brain`dumps)

    Agents gather experiences during simulations. These experiences can
    be stored (e.g., in the results database) and later retrieved.
    This way, agents can, e.g., load previously saved policy networks
    (so-called ::`~Brain` dumps) or trajectories.

    To dump or load a :class:`~Brain` or query the store for previous
    trajectories, they need to be located. The locator is represented
    by instances of this class. It identifies experiences by
    experiment run UID, agent name, and experiment run phase number.

    The information for this comes from the experiement run definition, i.e.,
    the experiment run document (usually written down in YAML format).

    Parameters
    ----------

    agent_name : str
        Unique name (ID) of the agent that housed the :class:`~Brain` this
        locator refers to. The key in the experiment run file is ``agent``.
    experiment_run_uid : str
        UID (user defined, unique ID) of the experiment run the experiences
        are located in. The key in the experiment run file is
        ``experiment_run``.
    experiment_run_phase : int
        Number (index, starting at 0) of the experiment run phase the
        experiences are located in. In the experiment run file, the key
        is named ``phase``.
    """

    agent_name: str
    experiment_run_uid: str
    experiment_run_phase: int
