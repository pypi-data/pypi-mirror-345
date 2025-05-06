"""
Store Query API.

palaestrAI provides a hierarchical database schema where experiments,
experiment runs, agent/environment configurations, as well as states,
actions, and rewards are stored.
The ::`palaestrai.store.query` module provides convenience methods for the data
that is requested most of the time, such as experiment configuration or agent
rewards.
All data is returned either as pandas DataFrame or dask DataFrame, depending on
the expected size of the data and query options.

All query functions offer some parameters to filte the query.
The easiest option is to pass a data frame via the ``like_dataframe``
parameter. This constructs the query according to the contents of the data
frame:
The column names are the table's attributes and all data frame contents are
used as filter predicate in to construct a query using the schema of
``WHERE column_name IN [cell1, cell2, cell3] AND column_name_2 IN ...``.
More colloquially, this means that the data frame passed via the
``like_dataframe`` parameter contains the data used for filtering.
If a data frame contains the columns ``experiment_run_uid`` and
``agent_name``, and the contents are ``1``, ``2``, and ``a1`` and ``a2``,
respectively, then the results from the database contain only those rows where
the experiment run UID is either ``1`` or ``2``, and the agent name is
either ``a1`` or ``a2``.
In addition, each query function also has explicitly spelled out parameters
for filtering.
E.g., with ``experiment_run_uids``, only the mentioned experiment run UIDs
are being queried.
If multiple parameters are specified, they are joined with an implicit
logical *and*.
E.g., if both ``experiment_run_uids`` and ``experiment_run_phase_uids`` are
specified, then the database is queried for data that belongs to the
specified experiment runs AND the specified experiment run phases.
The resulting query that is rendered is equivalent to
``... experiment_run.uid IN ... AND experiment_run_phase.uid IN ...``.

In addition, each query function allows for a user-defined predicate to be
passed. This parameter, ``predicate``, is expected to be a callable (e.g., a
lambda expression) that receives the query object *after* all other query
options are applied. It is expected to return the (modified) query object.
For example::

    df: pandas.DataFrame = experiments_and_runs_configurations(
        predicate=lambda query: query.limit(5)
    )

This would select only five entries from the database.

All results are ordered in *descending* order, such that the newest entries
are always first.
I.e., the ``limit(5)`` example above would automatically select the five newest
entries.

In order to avoid confusion, relation names and attributes are joined by an
underscore (``_``).
E.g., the ID of an environment is represented by the ``environment_id``
attribute in the resulting data frame.

Each function expects a :class:`~Session` object as first argument.
I.e., the access credentials will be those that are stored in the current
runtime configuration.
If the ``session`` parameter is not supplied, a new session will be
automatically created.
However, the store API does not take care of cleaning sessions. I.e., running
more than one query function without explicitly supplying a session object will
most likely lead to dangling open connections to the database.
The best solution is to use a context manager, e.g.::

    from palaestrai.store import Session
    import palaestrai.store.query as palq

    with Session() as session:
        ers = palq.experiments_and_runs_configurations(session)

.. warning::
    The query API is currently in *beta state*. That means that it is currently
    caught in the impeding API changes. This includes the way the
    :class:`~.SensorInformation`, :class:`~.ActuatorInformation`, and
    :class:`~.RewardInformation` classes are serialized.
    If you encounter bugs, please report them at the
    `palaestrAI issue tracker <https://gitlab.com/arl2/palaestrai/-/issues>`_
    for the *store* subsystem.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
    List,
    Union,
    Callable,
    Tuple,
    Dict,
    Generator,
)

import pandas as pd
import dask.config as dc
import dask.dataframe as dd

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy

import sqlalchemy.orm
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm.attributes import QueryableAttribute

from .database_model import (
    Experiment,
    ExperimentRun,
    ExperimentRunInstance,
    ExperimentRunPhase,
    Agent,
    Environment,
    MuscleAction,
)
from .session import Session
from palaestrai.core import RuntimeConfig

if TYPE_CHECKING:
    Predicate = Callable[[sqlalchemy.sql.select], sqlalchemy.sql.select]
    AttribPredicate = Union[
        Callable[
            [Dict[str, QueryableAttribute]],
            Union[
                Generator[QueryableAttribute, None, None],
                Tuple[QueryableAttribute],
            ],
        ],
    ]


def make_deserialization_session():
    jsonpickle_numpy.register_handlers()
    _db_engine = sqlalchemy.create_engine(
        RuntimeConfig().store_uri,
        json_deserializer=jsonpickle.loads,
    )
    _db_session_maker = sqlalchemy.orm.sessionmaker()
    _db_session_maker.configure(bind=_db_engine)
    dbh = _db_session_maker()
    return dbh


def _default_attrib_func(query_attribute_dict: Dict[str, QueryableAttribute]):
    return (
        query_attribute
        for query_attribute_label, query_attribute in query_attribute_dict.items()
    )


def experiments_and_runs_configurations(
    session: Optional[sqlalchemy.orm.Session] = None,
    attrib_func: Optional[AttribPredicate] = None,
    predicate: Predicate = lambda query: query,
    index_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Known Experiments, Experiment Runs, Instances, and Phases.

    Creates a comprehensive list containing information about

    * experiments
    * experiment runs
    * experiment run instances
    * experiment run phases.

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    attrib_func :  Callable[[Dict[str, QueryableAttribute]], Tuple[QueryableAttribute]]
        A function that can modify each ::`sqlalchemy.orm.attributes.QueryableAttribute`
        for the select statement.
        This can be done by e.g. adding sqlalchemy functions when mapping from the dict
        to attributes. The dict thereby maps the corresponding labels to the attributes.
        For an example on how to get the max experiment_run_instance_id, see the Examples section.
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query
    index_col : Optional[str] = "experiment_run_instance_uid"
        The column used as the index for the returned DataFrame
    Returns
    -------
    pandas.DataFrame:
        A dataframe containing the following columns:
        * experiment_id
        * experiment_name
        * experiment_document
        * experiment_run_id
        * experiment_run_uid
        * experiment_run_document
        * experiment_run_instance_id
        * experiment_run_instance_uid
        * experiment_run_phase_id
        * experiment_run_phase_uid
        * experiment_run_phase_mode
    Examples
    -------
    >>> from sqlalchemy import func
    >>> import palaestrai.store.query as palq
    >>> from palaestrai.store.database_model import (
    ...     Experiment,
    ...     ExperimentRun,
    ... )
    >>> experiment_run_uid = "Dummy experiment run where the agents take turns"
    >>> erc = palq.experiments_and_runs_configurations(
    ...     dbh, # Session needs to be defined
    ...     attrib_func=lambda query_attribute_dict: (
    ...         func.max(query_attribute)
    ...         if query_attribute_label == "experiment_run_instance_id"
    ...         else query_attribute
    ...         for query_attribute_label, query_attribute in query_attribute_dict.items()
    ...     ),
    ...     predicate=lambda query: query.filter(
    ...         Experiment.name
    ...         == "Dummy Experiment record for ExperimentRun "
    ...         + str(experiment_run_uid),
    ...         ExperimentRun.uid == experiment_run_uid,
    ...     ),
    ... )
    """
    if session is None:
        session = Session()

    if attrib_func is None:
        attrib_func = _default_attrib_func

    query_attribute_dict = {
        "experiment_id": Experiment.id,
        "experiment_name": Experiment.name,
        "experiment_document": Experiment.document,
        "experiment_run_id": ExperimentRun.id,
        "experiment_run_uid": ExperimentRun.uid,
        "experiment_run_document": ExperimentRun.document,
        "experiment_run_instance_id": ExperimentRunInstance.id,
        "experiment_run_instance_uid": ExperimentRunInstance.uid,
        "experiment_run_phase_id": ExperimentRunPhase.id,
        "experiment_run_phase_uid": ExperimentRunPhase.uid,
        "experiment_run_phase_mode": ExperimentRunPhase.mode,
    }

    query_attribute_dict = {
        query_attribute_label: query_attribute.label(query_attribute_label)
        for query_attribute_label, query_attribute in query_attribute_dict.items()
    }

    query = (
        sa.select(*attrib_func(query_attribute_dict))
        .select_from(Experiment)
        .join(ExperimentRun)
        .join(ExperimentRunInstance)
        .join(ExperimentRunPhase)
    )
    query = predicate(query)
    return pd.read_sql_query(query, session.bind, index_col=index_col)


def get_max_experiment_run_instance_uid(
    session: Optional[sqlalchemy.orm.Session] = None,
    experiment_name: str = "",
    experiment_run_uid: str = "",
) -> Tuple[str, pd.DataFrame]:
    if session is None:
        session = Session()

    erc_instance_id: pd.DataFrame = experiments_and_runs_configurations(
        session,
        attrib_func=lambda query_attribute_dict: (
            func.max(query_attribute_dict["experiment_run_instance_id"]).label(
                "experiment_run_instance_id"
            ),
        ),
        predicate=lambda query: query.filter(
            Experiment.name == experiment_name,
            ExperimentRun.uid == experiment_run_uid,
        ),
        index_col=None,
    )
    experiment_run_instance_id: int = (
        erc_instance_id.experiment_run_instance_id.iloc[0]
    )
    erc_instance_uid: pd.DataFrame = experiments_and_runs_configurations(
        session,
        predicate=lambda query: query.filter(
            Experiment.name == experiment_name,
            ExperimentRun.uid == experiment_run_uid,
            ExperimentRunInstance.id == str(experiment_run_instance_id),
        ),
        index_col=None,
    )
    experiment_run_instance_uid: str = (
        erc_instance_uid.experiment_run_instance_uid.iloc
    )[0]
    return experiment_run_instance_uid, erc_instance_uid


def agents_configurations(
    session: Optional[sqlalchemy.orm.Session] = None,
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> pd.DataFrame:
    """
    Configurations of agents.

    Creates a composite list containing information about

    * agents
    * associated experiment run phases
    * associated experiment run instances
    * associated experiment runs
    * associated experiments

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. If any of
        the columns ``experiment_uid``, ``experiment_run_uid``, and/or
        ``experiment_run_phase_uid`` are given, then the data in the frame
        is used in a ``WHERE ... IN ...``-style clause. If more than one of
        these columns are present, they are joined by ``AND``. Note the
        singular form, e.g., ``experiment_uid`` (singular),
        not ``experiment_run_uids`` (plural). The reason for this seemingly
        inconsistent naming is that the singular form is used in the column
        headers of the data frames that are returned by all query functions.
        Thus, the ``like_dataframe`` parameter allows to pass a data frame from
        another query function (e.g., ::`~experiments_and_runs_configurations`)
        for filtering.
        Note that the index of the data frame is *not* used.
    experiment_ids : Optional[List[str]]
        An interable containing experiment IDs to filter for
    experiment_run_uids :  Optional[List[str]]
        An interable containing experiment run UIDs to filter for
    experiment_run_instance_uids :  Optional[List[str]]
        An interable containing experiment run instance UIDs to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    pandas.DataFrame
        A dataframe containing the following columns:
        * agent_id
        * agent_uid
        * agent_name
        * agent_configuration
        * experiment_run_phase_id
        * experiment_run_phase_uid
        * experiment_run_phase_configuration
        * experiment_run_phase_configuration
        * experiment_run_instance_uid
        * experiment_run_id
        * experiment_run_uid
        * experiment_id
        * experiment_name
    """
    if session is None:
        session = Session()

    experiment_ids = (experiment_ids or []) + list(
        like_dataframe.get("experiment_ids", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_uids = (experiment_run_uids or []) + list(
        like_dataframe.get("experiment_run_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_instance_uids = (experiment_run_instance_uids or []) + list(
        like_dataframe.get("experiment_run_instance_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_phase_uids = (experiment_run_phase_uids or []) + list(
        like_dataframe.get("experiment_run_phase_uid", [])
        if like_dataframe is not None
        else []
    )

    query = (
        sa.select(
            Agent.id.label("agent_id"),
            Agent.uid.label("agent_uid"),
            Agent.name.label("agent_name"),
            Agent.configuration.label("agent_configuration"),
            ExperimentRunPhase.id.label("experiment_run_phase_id"),
            ExperimentRunPhase.uid.label("experiment_run_phase_uid"),
            ExperimentRunPhase.configuration.label(
                "experiment_run_phase_configuration"
            ),
            ExperimentRunInstance.uid.label("experiment_run_instance_uid"),
            ExperimentRun.id.label("experiment_run_id"),
            ExperimentRun.uid.label("experiment_run_uid"),
            Experiment.id.label("experiment_id"),
            Experiment.name.label("experiment_name"),
        )
        .select_from(Agent)
        .join(ExperimentRunPhase)
        .join(ExperimentRunInstance)
        .join(ExperimentRun)
        .join(Experiment)
        .order_by(Agent.id.desc())
    )
    if experiment_run_phase_uids:
        query = query.where(
            ExperimentRunPhase.uid.in_(experiment_run_phase_uids)
        )
    if experiment_run_instance_uids:
        query = query.where(
            ExperimentRunInstance.uid.in_(experiment_run_instance_uids)
        )
    if experiment_run_uids:
        query = query.where(ExperimentRun.uid.in_(experiment_run_uids))
    if experiment_ids:
        query = query.where(Experiment.id.in_(experiment_ids))
    query = predicate(query)
    return pd.read_sql_query(query, session.bind, index_col="agent_id")


def environments_configurations(
    session: Optional[sqlalchemy.orm.Session] = None,
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_uids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> pd.DataFrame:
    """
    Configurations of Environments.

    Creates a composite list containing information about

    * agents
    * associated experiment run phases
    * associated experiment run instances
    * associated experiment runs
    * associated experiments

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_uids : Optional[List[str]]
        An interable containing experiment UIDs to filter for
    experiment_run_uids :  Optional[List[str]]
        An interable containing experiment run UIDs to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    pandas.DataFrame
        A dataframe containing the following columns:
        * environment_id
        * environment_uid
        * environment_type
        * environment_parameters
        * experiment_run_phase_id
        * experiment_run_phase_uid
        * experiment_run_phase_configuration
        * experiment_run_phase_configuration
        * experiment_run_instance_uid
        * experiment_run_id
        * experiment_run_uid
        * experiment_id
        * experiment_name
    """
    if session is None:
        session = Session()

    experiment_uids = (experiment_uids or []) + list(
        like_dataframe.get("experiment_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_uids = (experiment_run_uids or []) + list(
        like_dataframe.get("experiment_run_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_phase_uids = (experiment_run_phase_uids or []) + list(
        like_dataframe.get("experiment_run_phase_uid", [])
        if like_dataframe is not None
        else []
    )

    query = (
        sa.select(
            Environment.id.label("environment_id"),
            Environment.uid.label("environment_uid"),
            Environment.type.label("environment_type"),
            Environment.parameters.label("environment_parameters"),
            ExperimentRunPhase.id.label("experiment_run_phase_id"),
            ExperimentRunPhase.uid.label("experiment_run_phase_uid"),
            ExperimentRunPhase.configuration.label(
                "experiment_run_phase_configuration"
            ),
            ExperimentRunInstance.uid.label("experiment_run_instance_uid"),
            ExperimentRun.id.label("experiment_run_id"),
            ExperimentRun.uid.label("experiment_run_uid"),
            Experiment.id.label("experiment_id"),
            Experiment.name.label("experiment_name"),
        )
        .select_from(Environment)
        .join(Agent.experiment_run_phase)
        .join(ExperimentRunPhase.experiment_run_instance)
        .join(ExperimentRunInstance.experiment_run)
        .join(ExperimentRun.experiment)
        .order_by(Environment.id.desc())
    )

    if experiment_run_phase_uids:
        query = query.where(
            ExperimentRunPhase.uid.in_(experiment_run_phase_uids)
        )
    if experiment_run_uids:
        query = query.where(ExperimentRun.uid.in_(experiment_run_uids))
    if experiment_uids:
        query = query.where(ExperimentRun.uid.in_(experiment_uids))
    query = predicate(query)
    return pd.read_sql_query(query, session.bind, index_col="environment_id")


def _muscle_actions_query(
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> sqlalchemy.sql.expression.Select:
    query = (
        sa.select(
            MuscleAction.id.label("muscle_action_id"),
            MuscleAction.walltime.label("muscle_action_walltime"),
            MuscleAction.simtimes.label("muscle_action_simtimes"),
            MuscleAction.rollout_worker_uid.label("rollout_worker_uid"),
            MuscleAction.sensor_readings.label("muscle_sensor_readings"),
            MuscleAction.actuator_setpoints.label("muscle_actuator_setpoints"),
            MuscleAction.rewards.label("muscle_action_rewards"),
            MuscleAction.objective.label("muscle_action_objective"),
            MuscleAction.done.label("muscle_action_done"),
            Agent.id.label("agent_id"),
            Agent.uid.label("agent_uid"),
            Agent.name.label("agent_name"),
            ExperimentRunPhase.id.label("experiment_run_phase_id"),
            ExperimentRunPhase.uid.label("experiment_run_phase_uid"),
            ExperimentRunPhase.configuration.label(
                "experiment_run_phase_configuration"
            ),
            ExperimentRunInstance.uid.label("experiment_run_instance_uid"),
            ExperimentRun.id.label("experiment_run_id"),
            ExperimentRun.uid.label("experiment_run_uid"),
            Experiment.id.label("experiment_id"),
            Experiment.name.label("experiment_name"),
        )
        .select_from(MuscleAction)
        .join(Agent)
        .join(ExperimentRunPhase)
        .join(ExperimentRunInstance)
        .join(ExperimentRun)
        .join(Experiment)
        .where(MuscleAction.actuator_setpoints != sa.JSON.NULL)
    )

    if experiment_ids:
        query = query.where(Experiment.id.in_(experiment_ids))

    if experiment_run_uids:
        query = query.where(ExperimentRun.uid.in_(experiment_run_uids))

    if experiment_run_instance_uids:
        query = query.where(
            ExperimentRunInstance.uid.in_(experiment_run_instance_uids)
        )

    if experiment_run_phase_uids:
        query = query.where(
            ExperimentRunPhase.uid.in_(experiment_run_phase_uids)
        )

    if agent_uids:
        query = query.where(Agent.name.in_(agent_uids))
    query = predicate(query)
    return query


def _query_to_dataframe(
    session: sqlalchemy.orm.Session, query: sqlalchemy.sql.select
) -> Union[pd.DataFrame, dd.DataFrame]:
    # TODO: Fix deserialisation for cte-select-wrapped queries?
    # cte = query.cte()
    # q = sa.select("*").select_from(cte)
    if query._limit_clause is not None or query._offset_clause is not None:
        return pd.read_sql_query(
            query,
            session.bind,
            index_col="muscle_action_id",
        )
    else:
        dc.set({"dataframe.convert-string": False})
        return dd.read_sql_query(
            query,
            session.bind.url.render_as_string(hide_password=False),
            index_col="muscle_action_id",
            engine_kwargs={"json_deserializer": jsonpickle.loads},
        ).compute()


def make_muscle_actions_query(
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> sqlalchemy.sql.expression.Select:
    return _muscle_actions_query(
        experiment_ids=experiment_ids,
        experiment_run_uids=experiment_run_uids,
        experiment_run_instance_uids=experiment_run_instance_uids,
        experiment_run_phase_uids=experiment_run_phase_uids,
        agent_uids=agent_uids,
        predicate=predicate,
    )


def muscle_actions(
    session: Optional[sqlalchemy.orm.Session] = None,
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> Union[pd.DataFrame, dd.DataFrame]:
    """All action data of a ::`~.Muscle`: readings, setpoints, and rewards

    The resulting dataframe contains information about:

    * muscle sensor readings
    * muscle actuator setpoints
    * muscle rewards
    * experiment run phases
    * experiment run instances
    * experiment runs
    * experiments

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_ids : Optional[List[str]]
        An interable containing experiment IDs to filter for
    experiment_run_uids :  Optional[List[str]]
        An interable containing experiment run UIDs to filter for
    experiment_run_instance_uids :  Optional[List[str]]
        An interable containing experiment run instance UIDs to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    agent_uids : Optional[List[str]] = None
        An interable containing agent UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    Union[pd.DataFrame, dd.DataFrame]:
        This method returns a dask dataframe by default, unless the predicate
        adds a ``LIMIT`` or ``OFFSET`` clause. The dataframe contains the
        following columns:
        * muscle_action_id
        * muscle_action_walltime
        * muscle_action_simtimes
        * muscle_sensor_readings
        * muscle_actuator_setpoints
        * muscle_action_rewards
        * muscle_action_objective
        * agent_id
        * agent_uid
        * agent_name
        * rollout_worker_uid
        * experiment_run_phase_id
        * experiment_run_phase_uid
        * experiment_run_phase_configuration
        * experiment_run_instance_uid
        * experiment_run_id
        * experiment_run_uid
        * experiment_id
        * experiment_name
    """
    if session is None:
        session = Session()

    experiment_ids = (experiment_ids or []) + list(
        like_dataframe.get("experiment_id", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_uids = (experiment_run_uids or []) + list(
        like_dataframe.get("experiment_run_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_instance_uids = (experiment_run_instance_uids or []) + list(
        like_dataframe.get("experiment_run_instance_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_phase_uids = (experiment_run_phase_uids or []) + list(
        like_dataframe.get("experiment_run_phase_uid", [])
        if like_dataframe is not None
        else []
    )
    query = make_muscle_actions_query(
        experiment_ids,
        experiment_run_uids,
        experiment_run_instance_uids,
        experiment_run_phase_uids,
        agent_uids,
        predicate,
    )
    return _query_to_dataframe(session, query)


def latest_muscle_action_values(
    session: Optional[sqlalchemy.orm.Session] = None,
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_name: Optional[str] = None,
    experiment_run_uid: Optional[str] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> Union[pd.DataFrame, dd.DataFrame]:
    """The latest (max run instance id) action data of a ::`~.Muscle`: readings, setpoints, and rewards
    with the plain values of the information objects

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_name : Optional[str]
        An str for the experiment name to filter for
    experiment_run_uid : Optional[str]
        An str for the run uid to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    agent_uids : Optional[List[str]] = None
        An interable containing agent UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    Union[pd.DataFrame, dd.DataFrame]:
        This method returns a dask dataframe by default, unless the predicate
        adds a ``LIMIT`` or ``OFFSET`` clause. The dataframe contains the
        following columns:
        * muscle_action_id
        * muscle_action_walltime
        * muscle_action_simtimes
        * muscle_action_simtime_ticks
        * muscle_action_simtime_timestamp
        * muscle_sensor_readings
        * muscle_actuator_setpoints
        * muscle_action_rewards
        * muscle_action_objective
        * agent_id
        * agent_uid
        * agent_name
        * experiment_run_phase_id
        * experiment_run_phase_uid
        * experiment_run_phase_configuration
        * experiment_run_instance_uid
        * experiment_run_id
        * experiment_run_uid
        * experiment_id
        * experiment_name
    """

    assert experiment_name is not None
    assert experiment_run_uid is not None
    if session is None:
        session = Session()

    (
        max_experiment_run_instance_uid,
        erc_max_experiment_run_instance_uid,
    ) = get_max_experiment_run_instance_uid(
        session, experiment_name, experiment_run_uid
    )

    experiment_ids = [
        str(erc_max_experiment_run_instance_uid.experiment_id.iloc[0])
    ]
    experiment_run_uids = [
        str(erc_max_experiment_run_instance_uid.experiment_run_uid.iloc[0])
    ]
    experiment_run_instance_uids = [
        str(
            erc_max_experiment_run_instance_uid.experiment_run_instance_uid.iloc[
                0
            ]
        )
    ]

    erc: Union[pd.DataFrame, dd.DataFrame] = muscle_actions(
        session,
        like_dataframe=like_dataframe,
        experiment_ids=experiment_ids,
        experiment_run_uids=experiment_run_uids,
        experiment_run_instance_uids=experiment_run_instance_uids,
        experiment_run_phase_uids=experiment_run_phase_uids,
        agent_uids=agent_uids,
        predicate=predicate,
    )

    def value_dict_extract_func(information_object_list):
        return (
            {
                information_object.uid: information_object.value
                for information_object in information_object_list
            }
            if information_object_list is not None
            else None
        )

    erc.muscle_sensor_readings = erc.muscle_sensor_readings.apply(
        value_dict_extract_func
    )
    erc.muscle_actuator_setpoints = erc.muscle_actuator_setpoints.apply(
        value_dict_extract_func
    )
    erc.muscle_action_rewards = erc.muscle_action_rewards.apply(
        value_dict_extract_func
    )

    # Try to extract nicely formatted timestamps:

    ticks_envs = [
        k
        for k, v in erc.muscle_action_simtimes.iloc[0].items()
        if v["simtime_ticks"] is not None
    ]
    if ticks_envs:
        ticks_env = ticks_envs[0]
        erc["muscle_action_simtime_ticks"] = erc.muscle_action_simtimes.apply(
            lambda muscle_action_simtime: muscle_action_simtime[ticks_env][
                "simtime_ticks"
            ]
        )
    timestamp_envs = [
        k
        for k, v in erc.muscle_action_simtimes.iloc[-1].items()
        if v["simtime_timestamp"] is not None
    ]
    if timestamp_envs:
        timestamp_env = timestamp_envs[0]
        erc["muscle_action_simtime_timestamp"] = (
            erc.muscle_action_simtimes.apply(
                lambda muscle_action_simtime: str(
                    muscle_action_simtime[timestamp_env]["simtime_timestamp"]
                )
            )
        )

    return erc


def latest_muscle_action_values_non_empty_multi_index(
    session: Optional[sqlalchemy.orm.Session] = None,
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_name: Optional[str] = None,
    experiment_run_uid: Optional[str] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> Union[pd.DataFrame, dd.DataFrame]:
    """The latest (max run instance id) action data of a ::`~.Muscle`:
    readings, setpoints, and rewards
    with the plain values of the information objects

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_name : Optional[str]
        An str for the experiment name to filter for
    experiment_run_uid : Optional[str]
        An str for the run uid to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    agent_uids : Optional[List[str]]
        An interable containing agent UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    Union[pd.DataFrame, dd.DataFrame]:
        This method returns a dask dataframe by default, unless the predicate
        adds a ``LIMIT`` or ``OFFSET`` clause. The dataframe with
        the index column of 'muscle_action_id's contains only non-empty rows
        with the following columns:
        * muscle_action_walltime
        * muscle_action_simtime_ticks
        * muscle_action_simtime_timestamp
        * muscle_sensor_readings
            With each sensor as a separate subcolumn
        * muscle_actuator_setpoints
            With each actuator as a separate subcolumn
        * muscle_action_rewards
            With each reward metric as a separate subcolumn
        * muscle_action_objective
        * agent_uid
        * experiment_run_phase_uid
    """
    if session is None:
        session = Session()

    erc = latest_muscle_action_values(
        session=session,
        experiment_name=experiment_name,
        experiment_run_uid=experiment_run_uid,
        experiment_run_phase_uids=experiment_run_phase_uids,
        agent_uids=agent_uids,
    )

    erc_non_empty = erc[
        erc.apply(
            lambda x: len(x["muscle_actuator_setpoints"]) > 0
            and len(x["muscle_sensor_readings"]) > 0,
            axis=1,
        )
    ]

    dict_erc_non_empty = {
        (key, key): erc_non_empty[key]
        for key in [
            "agent_uid",
            "experiment_run_phase_uid",
            "muscle_action_simtime_ticks",
            "muscle_action_simtime_timestamp",
            "muscle_action_walltime",
            "muscle_action_objective",
        ]
    }

    erc_non_empty_sensor_readings_dict = {
        ("muscle_sensor_readings", env): [
            sensor_reading[env]
            for sensor_reading in erc_non_empty.muscle_sensor_readings
        ]
        for env in erc_non_empty.muscle_sensor_readings.iloc[0].keys()
    }
    dict_erc_non_empty.update(erc_non_empty_sensor_readings_dict)

    erc_non_empty_actuator_setpoints_dict = {
        ("muscle_actuator_setpoints", env): [
            actuator_setpoints[env]
            for actuator_setpoints in erc_non_empty.muscle_actuator_setpoints
        ]
        for env in erc_non_empty.muscle_actuator_setpoints.iloc[0].keys()
    }
    dict_erc_non_empty.update(erc_non_empty_actuator_setpoints_dict)

    erc_non_empty_rewards_dict = {
        ("muscle_action_rewards", key): [
            rewards[key] for rewards in erc_non_empty.muscle_action_rewards
        ]
        for key in erc_non_empty.muscle_action_rewards.iloc[0].keys()
    }
    dict_erc_non_empty.update(erc_non_empty_rewards_dict)

    df_erc_non_empty = pd.DataFrame(
        dict_erc_non_empty, index=erc_non_empty.index
    )

    return df_erc_non_empty


def make_muscles_cumulative_objective_query(
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> sqlalchemy.sql.expression.Select:
    query = (
        sa.select(
            sa.func.max(MuscleAction.rollout_worker_uid).label(
                "rollout_worker_uid"
            ),
            MuscleAction.episode.label("muscle_actions_episode"),
            sa.func.sum(MuscleAction.objective).label(
                "muscle_cumulative_objective"
            ),
            Agent.uid.label("agent_uid"),
            Agent.name.label("agent_name"),
            ExperimentRunPhase.id.label("experiment_run_phase_id"),
            ExperimentRunPhase.uid.label("experiment_run_phase_uid"),
            ExperimentRunPhase.configuration.label(
                "experiment_run_phase_configuration"
            ),
            ExperimentRunInstance.uid.label("experiment_run_instance_uid"),
            ExperimentRun.id.label("experiment_run_id"),
            ExperimentRun.uid.label("experiment_run_uid"),
            Experiment.id.label("experiment_id"),
            Experiment.name.label("experiment_name"),
        )
        .select_from(MuscleAction)
        .join(Agent)
        .join(ExperimentRunPhase)
        .join(ExperimentRunInstance)
        .join(ExperimentRun)
        .join(Experiment)
        .where(MuscleAction.actuator_setpoints != sa.JSON.NULL)
        .group_by(
            Agent.uid,
            Agent.name,
            ExperimentRunPhase.id,
            ExperimentRunPhase.uid,
            ExperimentRunPhase.configuration,
            ExperimentRunInstance.uid,
            ExperimentRun.id,
            ExperimentRun.uid,
            Experiment.id,
            Experiment.name,
            MuscleAction.episode,
        )
    )

    if experiment_ids:
        query = query.where(Experiment.id.in_(experiment_ids))

    if experiment_run_uids:
        query = query.where(ExperimentRun.uid.in_(experiment_run_uids))

    if experiment_run_instance_uids:
        query = query.where(
            ExperimentRunInstance.uid.in_(experiment_run_instance_uids)
        )

    if experiment_run_phase_uids:
        query = query.where(
            ExperimentRunPhase.uid.in_(experiment_run_phase_uids)
        )

    if agent_uids:
        query = query.where(Agent.name.in_(agent_uids))
    query = predicate(query)
    return query


def muscles_cumulative_objective(
    session: Optional[sqlalchemy.orm.Session] = None,
    like_dataframe: Optional[Union[pd.DataFrame, dd.DataFrame]] = None,
    experiment_ids: Optional[List[str]] = None,
    experiment_run_uids: Optional[List[str]] = None,
    experiment_run_instance_uids: Optional[List[str]] = None,
    experiment_run_phase_uids: Optional[List[str]] = None,
    agent_uids: Optional[List[str]] = None,
    predicate: Predicate = lambda query: query,
) -> pd.DataFrame:
    """Cumulative object values of rollout workers (i.e., per-worker rewards)

    The resulting dataframe lists the cumulative reward of each worker of
    agents in phases of the experiment.
    Results can be filtered by providing the respective parameters, e.g.,
    to get the cumulative objective values of agents in one particular phase,
    use the ``experiment_run_phase_uids`` parameter.
    The ``like_dataframe`` will probably be the most convenient method for
    filtering.
    Supplying both a dataframe via ``like_dataframe`` and any other filter
    parameter filters according to both.

    Parameters
    ----------
    session : sqlalchemy.orm.Session, optional
        An session object created by ::`palaestrai.store.Session()`.
        If not given (``None``), a new session will be automatically estblished
    like_dataframe : Optional[Union[pd.DataFrame, dd.DataFrame]] = None
        Uses the given dataframe to construct a search predicate. Refer to the
        parameter documentation of ::`~experiments_and_runs_configurations`
    experiment_ids : Optional[List[str]]
        An interable containing experiment IDs to filter for
    experiment_run_uids :  Optional[List[str]]
        An interable containing experiment run UIDs to filter for
    experiment_run_instance_uids :  Optional[List[str]]
        An interable containing experiment run instance UIDs to filter for
    experiment_run_phase_uids :  Optional[List[str]]
        An interable containing experiment run phase UIDs to filter for
    agent_uids : Optional[List[str]] = None
        An interable containing agent UIDs to filter for
    predicate : Predicate = lambda query: query
        An additional predicate (cf. ::`sqlalchemy.sql.expression`) applied to
        the database query after all other predicates have been applied

    Returns
    -------
    pd.DataFrame:
        The dataframe contains the following columns:
        * agent_id
        * agent_uid
        * agent_name
        * rollout_worker_uid
        * muscle_cumulative_objective
        * experiment_run_phase_id
        * experiment_run_phase_uid
        * experiment_run_phase_configuration
        * experiment_run_instance_uid
        * experiment_run_id
        * experiment_run_uid
        * experiment_id
        * experiment_name
    """
    if session is None:
        session = Session()

    experiment_ids = (experiment_ids or []) + list(
        like_dataframe.get("experiment_id", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_uids = (experiment_run_uids or []) + list(
        like_dataframe.get("experiment_run_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_instance_uids = (experiment_run_instance_uids or []) + list(
        like_dataframe.get("experiment_run_instance_uid", [])
        if like_dataframe is not None
        else []
    )
    experiment_run_phase_uids = (experiment_run_phase_uids or []) + list(
        like_dataframe.get("experiment_run_phase_uid", [])
        if like_dataframe is not None
        else []
    )

    query = make_muscles_cumulative_objective_query(
        experiment_ids=experiment_ids,
        experiment_run_uids=experiment_run_uids,
        experiment_run_instance_uids=experiment_run_instance_uids,
        experiment_run_phase_uids=experiment_run_phase_uids,
        agent_uids=agent_uids,
        predicate=predicate,
    )
    return pd.read_sql_query(
        query, session.bind, index_col="rollout_worker_uid"
    )
