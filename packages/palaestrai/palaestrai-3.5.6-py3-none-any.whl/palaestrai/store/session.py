from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Tuple

import os

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy

import sqlalchemy.exc
import sqlalchemy.orm

from palaestrai.core.runtime_config import RuntimeConfig

if TYPE_CHECKING:
    import sqlalchemy.engine
    import sqlalchemy.orm.session


LOG = logging.getLogger(__name__)
_session_makers: Dict[
    int, Tuple[sqlalchemy.engine.Engine, sqlalchemy.orm.session.sessionmaker]
] = {}


def _get_session_maker() -> sqlalchemy.orm.session.sessionmaker:
    """Internal getter ensure one session maker per process"""
    pid = os.getpid()
    if (
        pid in _session_makers
        and str(_session_makers[pid][0].url) == RuntimeConfig().store_uri
    ):
        LOG.debug(
            "Returning existing DB session maker for PID %d: %s",
            pid,
            _session_makers[pid][1],
        )
        return _session_makers[pid][1]

    jsonpickle_numpy.register_handlers()
    jsonpickle.set_preferred_backend("simplejson")
    jsonpickle.set_encoder_options("simplejson", ignore_nan=True)

    db_engine = sqlalchemy.create_engine(
        RuntimeConfig().store_uri,
        json_serializer=jsonpickle.dumps,
        json_deserializer=jsonpickle.loads,
    )
    db_session_maker = sqlalchemy.orm.sessionmaker()
    db_session_maker.configure(bind=db_engine)

    _session_makers[pid] = (db_engine, db_session_maker)
    LOG.debug(
        "Created new DB session maker for PID %d; state dict is now: %s",
        pid,
        _session_makers,
    )
    return db_session_maker


def Session() -> sqlalchemy.orm.Session:
    """Creates a new, connected database session to run queries on.

    This is a convenience function that creates and returns a new, opened
    database session. It uses the access data provided by
    ::`RuntimeConfig.store_uri`. It exists in order to facilitate working
    with the store, such as this::

        from palaestrai.store import Session, database_model as dbm

        session = Session()
        q = session.query(dbm.Experiment)

    Returns:
    --------

    sqlalchemy.orm.Session
        The initialized, opened database session.
    """
    db_session_maker = _get_session_maker()
    return db_session_maker()
