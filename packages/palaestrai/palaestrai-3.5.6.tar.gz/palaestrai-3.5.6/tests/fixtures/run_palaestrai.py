"""This module contains the debug script that can be used to start the dummy
experiment without the CLI."""

import os

from click.testing import CliRunner, Result

from palaestrai.cli.manager import cli


def run_palaestrai(*cli_args) -> int:
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli, list(cli_args))
    return result.exit_code
