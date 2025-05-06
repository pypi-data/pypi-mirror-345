from __future__ import annotations
from typing import Optional

import time
import logging

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy_utils import database_exists, create_database

from .database_model import Model

LOG = logging.getLogger(__name__)

try:
    from influxdb_client import InfluxDBClient
    from elasticsearch import Elasticsearch, BadRequestError
    from influxdb_client.client.exceptions import InfluxDBError
except ModuleNotFoundError as e:
    LOG.debug("Could not load ElasticSearch/Influx client: %s", e)

# Default chunk_time_interval. Might become configurable at some point iff we
# decide to keep TimescaleDB.
TIMESCALEDB_DEFAULT_CHUNK_SIZE_INTERVAL = 512


def _create_timescaledb_extension(engine):
    """Create the timescaledb extension.

    :param engine: The database engine.
    """
    with engine.begin() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    timescale_tables = {
        "world_states",
        "muscle_actions",
    }
    with engine.begin() as conn:
        for tbl in timescale_tables:
            cmd = (
                f"SELECT * FROM create_hypertable("
                f"'{tbl}', "  # Table name
                f"'id', "  # Primary partitioning column
                f"chunk_time_interval => "
                f"{TIMESCALEDB_DEFAULT_CHUNK_SIZE_INTERVAL})"
            )
            res = conn.execute(text(cmd))
            LOG.debug(
                'Result of executing "%s" during setup: %s',
                cmd,
                res.fetchall(),
            )
            res.close()
    LOG.info(
        "Created TimescaleDB hypertables: %s, set 'chunk_time_interval' "
        "parameter to %d. HINT: The chunk_time_interval should be chosen such "
        "that all active chunks of all your hypertables fit in 25\% of your "
        "RAM. You can change the value with TimescaleDB's "
        "set_chunk_time_interval() function.",
        ", ".join(timescale_tables),
        TIMESCALEDB_DEFAULT_CHUNK_SIZE_INTERVAL,
    )


def setup_database(uri: Optional[str] = None):
    """Creates the database from the current model in one go.

    Parameters
    ----------
    uri : str
        The complete database connection URI.
    """
    if not uri:
        from palaestrai.core import RuntimeConfig

        uri = RuntimeConfig().store_uri
    engine = create_engine(uri)
    while not database_exists(uri):
        i = 1
        if i > 3:  # Hardcoded max tries. No real reason to configure this.
            LOG.critical(
                "Could not create the database. See errors above for more "
                "details. Giving up now."
            )
            raise RuntimeError("Could not create database")
        try:
            create_database(uri)
        except OperationalError as e:
            try:
                import psycopg2.errors

                if isinstance(e.orig, psycopg2.errors.ObjectInUse):
                    LOG.warning(
                        "Could not create database because the template was "
                        "in use. Retrying in %d seconds.",
                        i,
                    )
                    time.sleep(i)
                else:
                    break
            except ImportError:
                pass
        except ProgrammingError as e:
            LOG.error(
                "There was an error creating the database. I will continue "
                "and hope for the best. The error was: %s",
                e,
            )
        i += 1

    with engine.begin() as conn:
        try:
            Model.metadata.create_all(engine)
        except ProgrammingError as e:
            LOG.error("Could not create database: %s" % e)
            raise e
        try:
            from midas.tools.palaestrai.database_view import (  # type: ignore
                create_midas_views,
            )

            if engine.url.drivername == "psycopg2":
                # type: ignore
                create_midas_views(conn)
        except ModuleNotFoundError:
            pass  # Ok, don't create specific views if the tools are not pres.
    try:
        _create_timescaledb_extension(engine)
    except OperationalError as e:
        LOG.warning(
            "Could not create extension timescaledb and create hypertables: "
            "%s. "
            "Your database setup might lead to noticeable slowdowns with "
            "larger experiment runs. Please upgrade to PostgreSQL with "
            "TimescaleDB for the best performance." % e
        )


# create a new influx and elasticsearch database using setup_influxdb(time_series_uri) and
# setup_elasticsearch(storage_uri) and write numpy style code documentation
def setup_database_v2(store_uri, time_series_uri):
    """Creates the database from the current model in one go.

    :param store_uri: The complete database connection URI.
    :param time_series_uri: The complete database connection URI.

    """
    # try setup the time series database
    setup_influxdb(time_series_uri)
    # setup the storage database
    setup_elasticsearch(store_uri)


# TODO: Implement SSL verification
def setup_influxdb(time_series_uri):
    """Creates the database from the current model in one go.

    :param time_series_uri: The complete database connection URI.

    """

    # create the database
    db_type, time_series_uri = time_series_uri.split("+")
    org, token = time_series_uri.split("@")[0].split(":")
    connections = time_series_uri.split("@")[1]

    try:
        client = InfluxDBClient(url=connections, token=token, org=org)
    except Exception as e:
        LOG.error(
            "Could not connect to the influxdb. Please check if the "
            "'time_series_store_uri' is set correctly"
            "Error %s was risen.",
            e,
        )
        raise RuntimeError("Could not connect to database")

    bucket_api = client.buckets_api()
    try:
        bucket_api.create_bucket(bucket_name="palaestrai")
    except InfluxDBError as e:
        if "already exists" in str(e):
            LOG.info("Bucket already exists. Continuing...")
        else:
            LOG.error("Could not create bucket: %s" % e)
            raise e
    client.close()


# create a new elasticsearch client which ignores tls verification
# and create a new index with the name "palaestrai" if it does not exist
# if the index already exists, the client will be closed and the function will return
def setup_elasticsearch(store_uri):
    """Creates the database from the current model in one go.

    :param store_uri: The complete database connection URI.
    """
    store_uri = store_uri.replace("elasticsearch+", "")

    try:
        es = Elasticsearch(
            [store_uri],
            verify_certs=False,
            timeout=60,
            max_retries=10,
            retry_on_timeout=True,
        )
    except Exception as e:
        LOG.critical(
            "Could not connect to the elasticsearch. Please check if the "
            "'store_uri' is set correctly"
            "Error %s was risen.",
            e,
        )
        raise RuntimeError("Could not connect to database")
    try:
        es.indices.create(index="palaestrai", ignore=400)
    except Exception as e:
        if "resource_already_exists_exception" in str(e):
            LOG.info("Index already exists. Continuing...")
        else:
            raise e
