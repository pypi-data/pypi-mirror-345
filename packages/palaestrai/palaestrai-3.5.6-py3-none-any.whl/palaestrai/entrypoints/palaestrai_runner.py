from __future__ import annotations
from typing import Union, TextIO, Tuple, List

import sys
import asyncio
import logging
from pathlib import Path
from itertools import chain
from datetime import datetime

import ruamel.yaml

from palaestrai.core import RuntimeConfig
from palaestrai.experiment import ExperimentRun, Executor, ExecutorState

ExperimentRunInputTypes = Union[ExperimentRun, TextIO, str, Path]

LOG = logging.getLogger("palaestrai.runner")


def execute(
    experiment_run_definition: Union[
        ExperimentRunInputTypes, List[ExperimentRunInputTypes]
    ],
    runtime_config: Union[str, TextIO, dict, None] = None,
) -> Tuple[List[str], ExecutorState]:
    """Provides a single-line command to start an experiment and set a
    runtime configuration

    Parameters
    ----------
    experiment_run_definition: 1. Already set ExperimentRun object
                               2. Any text stream
                               3. The path to a file

        The configuration from which the experiment is loaded.

    runtime_config:            1. Any text stream
                               2. dict
                               3. None

        The Runtime configuration applicable for the run.
        Note that even when no additional source is provided, runtime will load
        a minimal configuration from build-in defaults.

    Returns
    -------
    typing.Tuple[Sequence[str], ExecutorState]
        A tuple containing:
        1. The list of all experiment run IDs
        2. The final state of the executor
    """
    if runtime_config:
        RuntimeConfig().load(runtime_config)

    # There is an implicit loading of the default config. The object returned
    # by RuntimeConfig() has at least the default loaded, and tries to load
    # from the search path. So there is no reason to have an explicit load()
    # here.

    if not isinstance(experiment_run_definition, List):
        experiment_run_definition = [experiment_run_definition]
    experiment_run_definition = [
        Path(i) if isinstance(i, str) else i for i in experiment_run_definition
    ]

    experiment_run_definition = list(
        chain.from_iterable(
            i.rglob("*.y*ml") if isinstance(i, Path) and i.is_dir() else [i]
            for i in experiment_run_definition
        )
    )
    experiment_runs = [
        ExperimentRun.load(i) if not isinstance(i, ExperimentRun) else i
        for i in experiment_run_definition
    ]

    if (
        not RuntimeConfig().store_uri is None
        and RuntimeConfig().store_uri.startswith("elasticsearch")
    ):
        try:
            from elasticsearch import Elasticsearch

            yaml = ruamel.yaml.YAML(typ="safe")
            _e_client = Elasticsearch(
                hosts=RuntimeConfig().store_uri.replace("elasticsearch+", ""),
                verify_certs=False,
            )
            for e in experiment_run_definition:
                with open(str(e), "r") as y_file:
                    yml = yaml.load(y_file)
                    file = {
                        "experiment_runs_instance_id": experiment_runs[
                            0
                        ].instance_uid,
                        "start_time": datetime.utcnow(),
                        "type": "experiment_run",
                        "file": yml,
                    }
                _ = _e_client.index(index="palaestrai", document=file)
            _e_client.close()
        except ImportError as e:
            LOG.debug("Could not load ElasticSearch client: %s", e)
        except Exception as e:
            LOG.exception("Could not connect to ElasticSearch: %s", e)

    executor = Executor()
    executor.schedule(experiment_runs)

    if asyncio.events._get_running_loop() is not None:
        LOG.debug("Event loop already running, using nest_asyncio.")
        import nest_asyncio

        nest_asyncio.apply()
        executor_final_state = asyncio.run(executor.execute())
    else:
        try:
            import uvloop

            LOG.debug("Using uvloop.")
            if sys.version_info >= (3, 11):
                with asyncio.Runner(
                    loop_factory=uvloop.new_event_loop
                ) as runner:
                    executor_final_state = runner.run(executor.execute())
            else:
                uvloop.install()
                executor_final_state = asyncio.run(executor.execute())
        except ModuleNotFoundError:
            LOG.debug("uvloop not available, using nest_asyncio.")
            import nest_asyncio

            nest_asyncio.apply()
            executor_final_state = asyncio.run(executor.execute())

    return [e.uid for e in experiment_runs], executor_final_state
