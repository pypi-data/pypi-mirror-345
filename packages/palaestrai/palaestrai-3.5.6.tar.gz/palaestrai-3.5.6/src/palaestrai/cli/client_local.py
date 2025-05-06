import sys
from itertools import chain
from pathlib import Path
from typing import Sequence, List, Union, TextIO

import click
from click_aliases import ClickAliasedGroup
import csv
import ruamel.yaml
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session
from sqlalchemy import delete, select
import sqlalchemy as sa
from tabulate import tabulate
from collections import defaultdict

import palaestrai
from palaestrai.core import RuntimeConfig
from palaestrai.experiment import ExecutorState, ExperimentRun
from palaestrai.store import database_model as dbm


@click.group(cls=ClickAliasedGroup)
def client():
    pass


def parse_id_choice(user_input: str):
    id_list = []
    for element in user_input.split(","):
        sections = [int(x) for x in element.split("-")]

        if len(sections) == 1:
            id_list.append(sections[0])
        else:
            for parts in range(min(sections), max(sections) + 1):
                id_list.append(parts)

    return id_list


@client.command(aliases=["start", "s"])
@click.option("-C", is_flag=True, default=False)
@click.argument(
    "experiment_paths",
    nargs=-1,
    type=click.Path(
        exists=True,
        readable=True,
        dir_okay=True,
        file_okay=True,
        allow_dash=True,
    ),
)
@click.pass_context
def experiment_start(ctx, c, experiment_paths: Sequence[Path]):
    """Starts a one or more experiments from a file or directory.

    EXPERIMENT_PATHS is any mixture of paths to files or directories;
    directories are expanded and recursively searched for experiment run files.
    \f

    Parameters
    ----------
    -C :
        Flag to invoke database cleaning before experiment run.
        Defaults to false.

    experiment_paths : Sequence[Path]
        Any mixture of file paths or directories.
    """
    if c:
        ctx.invoke(clean, experiment_paths=experiment_paths)

    experiment_paths = [Path(p) for p in experiment_paths]
    experiment_paths = list(
        chain.from_iterable(
            p.rglob("*.y*ml") if p.is_dir() else [p] for p in experiment_paths
        )
    )
    checked_experiment_files = [
        (path, ExperimentRun.check_syntax(path)) for path in experiment_paths
    ]
    invalid_experiment_files = [
        x[0] for x in checked_experiment_files if not x[1]
    ]
    if invalid_experiment_files:
        click.echo(
            "Skipping the following files, because they contain errors:",
            file=sys.stderr,
        )
        for path in invalid_experiment_files:
            click.echo(f"  * {path}", file=sys.stderr)
        click.echo(
            "Hint: run palaestrai experiment-check-syntax [FILES] to inspect "
            "the output of the syntax check.",
            file=sys.stderr,
        )

    _, executor_final_state = palaestrai.execute(
        [x[0] for x in checked_experiment_files if x[1]]
    )
    if executor_final_state != ExecutorState.EXITED:
        sys.exit(
            {
                ExecutorState.SIGINT: -2,
                ExecutorState.SIGABRT: -6,
                ExecutorState.SIGTERM: -15,
            }[executor_final_state]
        )
    else:
        click.echo("\nThank you for using palaestrAI!")
        try:
            from .fortune import get_cookie

            click.echo(get_cookie())
        except Exception:
            pass  # Don't let our fortune cookie break execution!


def _get_store_uri():
    config = RuntimeConfig()
    if not config.store_uri:
        click.echo(
            "Please create a runtime config (one of %s), "
            "and set the 'store_uri' options.\n"
            "My configuration, loaded from %s, does not contain it."
            % (config.CONFIG_FILE_PATHS, config._config_file_path),
            file=sys.stderr,
        )
        exit(1)

    return config.store_uri


def _get_store_type():
    store_uri = _get_store_uri()
    if store_uri.startswith("sqlite") or store_uri.startswith("postgresql"):
        return "relational"
    elif (
        store_uri.startswith("influxdb")
        or store_uri.startswith("influx")
        or store_uri.startswith("elastic")
        or store_uri.startswith("elasticsearch")
    ):
        return "timeseries"
    else:
        raise ValueError(
            "The store type of the store URI %s is not supported." % store_uri
        )


def _get_timeseries_store_uri():
    config = RuntimeConfig()
    if not config.time_series_store_uri:
        click.echo(
            "Please create a runtime config (one of %s), "
            "and set the 'time_series_store_uri' options.\n"
            "My configuration, loaded from %s, does not contain it."
            % (config.CONFIG_FILE_PATHS, config._config_file_path),
            file=sys.stderr,
        )
        exit(1)

    return config.time_series_store_uri


def _get_brain_dump_store_location():
    config = RuntimeConfig()
    if not config.brain_dump_store_location:
        click.echo(
            "There is no brain_dump_store_location in your"
            "Runtime config. The default is storing the"
            "brain dumps to the disk."
        )
    return config.brain_dump_store_location


def _get_environment_store_location():
    raise NotImplementedError()


@client.command()
def database_create():
    """Creates the store database.

    Requires a valid runtime configuration file.
    """
    store_type = _get_store_type()
    if store_type == "relational":
        store_uri = _get_store_uri()
        if not store_uri:
            exit(1)
        from palaestrai.store.database_util import setup_database

        try:
            setup_database(store_uri)
        except ArgumentError as e:
            click.echo(
                "SQLalchemy could not open a database connection. "
                "Please make sure that your 'store_uri' in %s is formed like "
                "'driver://user:password@host/database'. Error was: %s"
                % (RuntimeConfig()._config_file_path, e),
                file=sys.stderr,
            )
            exit(1)
    elif store_type == "timeseries":
        meta_store = _get_store_uri()
        timeseries_store = _get_timeseries_store_uri()
        if not meta_store or not timeseries_store:
            click.echo("Please set the store_uri and time_series_store_uri")
            exit(1)
        from palaestrai.store.database_util import setup_database_v2

        try:
            setup_database_v2(meta_store, timeseries_store)
        except ArgumentError as e:
            click.echo(
                "We could not open a database connection. "
                "Please make sure that your 'store_uri' and"
                "'time_series_store_uri' in %s is formed like "
                "'driver://user:password@host/database'. Error was: %s"
                % (RuntimeConfig()._config_file_path, e),
                file=sys.stderr,
            )
            exit(1)


@client.command()
def database_migrate():
    store_uri = _get_store_uri()
    if not store_uri:
        exit(1)


@client.command()
def runtime_config_show_default():
    """Shows the default runtime config and search paths."""
    yml = ruamel.yaml.YAML(typ="safe")
    print("%YAML 1.2\n")
    print("# palaestrAI Runtime Configuration")
    print(
        f"# Search path for this file is: {RuntimeConfig().CONFIG_FILE_PATHS}"
    )
    print("#\n\n---")
    yml.dump(RuntimeConfig().DEFAULT_CONFIG, stream=sys.stdout)


@client.command()
def runtime_config_show_effective():
    """Shows the currently effective runtime configuration"""
    yml = ruamel.yaml.YAML(typ="safe")
    print("%YAML 1.2")
    print(f"# Configuration loaded from: {RuntimeConfig()._config_file_path}")
    print("---")
    yml.dump(RuntimeConfig().to_dict(), stream=sys.stdout)


@client.command(aliases=["check", "c"])
@click.argument(
    "experiment_paths",
    nargs=-1,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        allow_dash=True,
    ),
)
def experiment_check_syntax(experiment_paths: Sequence[Path]):
    """Syntax checks experiment run definition files.

    The command runs the syntax/schema check on all provided files and prints
    a summary of all errors that were encountered.

    EXPERIMENT_PATHS is a mixture of file paths and paths to directories;
    directories are recursively searched for experiment run files.
    \f

    Parameters
    ----------
    experiment_paths : Sequence[Path]
        Any mixture of file paths or directories.
    """
    experiment_runs: List[Union[str, TextIO, Path]] = [
        Path(p) if p != "-" else sys.stdin for p in experiment_paths
    ]
    experiment_runs = list(
        chain.from_iterable(
            p.rglob("*.y*ml") if isinstance(p, Path) and p.is_dir() else [p]
            for p in experiment_runs
        )
    )
    check_errors = [
        (f, ExperimentRun.check_syntax(f)) for f in experiment_runs
    ]
    check_errors = [x for x in check_errors if not x[1]]  # Only errors
    if check_errors:
        click.echo("The following files contain errors:", file=sys.stderr)
    for e in check_errors:
        click.echo(f"  * {e[0]}: {e[1].error_message}", file=sys.stderr)
    exit(1 if check_errors else 0)


@client.command(aliases=["list", "l"])
@click.option("--format", "_format", default="simple")
@click.option("--limit", type=int)
@click.option("--offset", type=int)
@click.option("--database")
@click.option("--csv", "_csv")
def experiment_list(_format, limit, offset, database, _csv):
    """Lists all run experiments.

    Checks the provided or default database and either lists all run experiments in a
    tabulated fashion or writes them to a csv-file.
    """

    store_type = _get_store_type()
    if store_type == "relational":
        if not database:
            experiment_database = _get_store_uri()
            if not experiment_database:
                click.echo(
                    "No experiment-database found, please provide a database. E.g. --database=sqlite:///experiments.db",
                    file=sys.stderr,
                )
                exit(1)
        else:
            experiment_database = database

        click.echo(f"Checking database {experiment_database}")

        engine = sa.create_engine(experiment_database)
        connection = engine.connect()

        metadata = sa.MetaData()
        experiment_runs = sa.Table(
            "experiments", metadata, autoload=True, autoload_with=engine
        )

        query = sa.select([experiment_runs])
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        experiment_runs = connection.execute(query).fetchall()

        experiments_dict = defaultdict(list)
        for d in experiment_runs:
            for key, value in d.items():
                if _csv:
                    with open(_csv, "w", newline="") as csvfile:
                        experiment_writer = csv.writer(
                            csvfile,
                            delimiter=" ",
                            quotechar="|",
                            quoting=csv.QUOTE_MINIMAL,
                        )
                        experiment_writer.writerow(d)
                else:
                    experiments_dict[key].append(value)

        if not (_csv):
            click.echo(
                tabulate(experiments_dict, headers="keys", tablefmt=_format)
            )
        else:
            click.echo(f"Wrote experiments to {_csv}")
    exit(0)


@client.command()
@click.option("--database", type=str)
@click.option("--experiment-id", type=str)
@click.argument(
    "experiment_paths",
    nargs=-1,
    type=click.Path(
        exists=True,
        readable=True,
        dir_okay=True,
        file_okay=True,
        allow_dash=True,
    ),
)
def clean(database, experiment_id, experiment_paths: Sequence[Path]):
    """Cleans database of experiment runs and all associated
    entries.


    Parameters
    ----------
    database : Str
        URL of a specific database if you want to clean
        something other than the one specified in the runtime-config.
        Please provide the whole database URL.

        --database=sqlite:///experiments.db

    experiment-id : Str
        Experiment IDs fetched e.g. from palaestrai experiment-list
        Multiple values possible in the following formats:

        --experiment-id=1,3,6
        --experiment-id=2-7,9

    experiment_paths : Sequence[Path]
        Any mixture of file paths or directories.
    """
    if database:
        store_uri = database
    else:
        try:
            store_uri = _get_store_uri()
        except:
            exit(1)

    engine = sa.create_engine(store_uri)
    connection = engine.connect()
    if experiment_id:
        id_list = parse_id_choice(experiment_id)
        for experiment in id_list:
            db_result = connection.execute(
                "select name from experiments where id=" + str(experiment)
            )
            for row in db_result:
                with Session(engine, future=True) as session:
                    session.begin()
                    try:
                        delete_experiment = (
                            session.query(dbm.Experiment)
                            .filter_by(id=experiment)
                            .first()
                        )
                        session.delete(delete_experiment)
                    except:
                        session.rollback()
                        raise
                    else:
                        session.commit()

    experiment_paths = [Path(p) for p in experiment_paths]
    experiment_paths = list(
        chain.from_iterable(
            p.rglob("*.y*ml") if p.is_dir() else [p] for p in experiment_paths
        )
    )
    yml = ruamel.yaml.YAML(typ="safe")
    for experiment in experiment_paths:
        experiment_data = yml.load(experiment)
        if "experiment_uid" in experiment_data.keys():
            delete_me_uid = experiment_data["experiment_uid"]
        else:
            required_uid = experiment_data["uid"]
            delete_me_uid = (
                "Dummy experiment record for experiment run " + required_uid
            )

        db_result = connection.execute(
            "select * from experiments where name='" + delete_me_uid + "'"
        )
        for row in db_result:
            with Session(engine, future=True) as session:
                session.begin()
                try:
                    delete_experiment = (
                        session.query(dbm.Experiment)
                        .filter_by(name=delete_me_uid)
                        .first()
                    )
                    session.delete(delete_experiment)
                except:
                    session.rollback()
                    raise
                else:
                    session.commit()


def get_aliases():
    return (client._aliases, client._commands)
