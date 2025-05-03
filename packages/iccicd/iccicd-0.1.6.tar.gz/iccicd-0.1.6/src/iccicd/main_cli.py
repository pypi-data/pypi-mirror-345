#!/usr/bin/env python3

"""
This is the entrypoint for the `iccicd` application.

CLI arguments and handlers for individual modules are
registered here and defined in the respective `cli` submodules.

`launch_common()` is common code run before all handlers.
"""

import argparse
import logging

from iccore import runtime, logging_utils

import iccicd.packaging.cli
import iccicd.ci.cli
import iccicd.repo.cli

logger = logging.getLogger(__name__)


def launch_common(args) -> None:
    """
    Run this code before all CLI handlers. It sets up a global
    runtime context to store runtime configuration, such as the
    'dry run' flag and sets up logging.
    """
    runtime.ctx.set_is_dry_run(args.dry_run)
    logging_utils.setup_default_logger()


def main_cli():
    """
    This method is associated with the `iccicd` application in the
    project's pyproject.toml, i.e. it will be run when `iccicd` is
    called in a terminal.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    iccicd.packaging.cli.register(subparsers)
    iccicd.repo.cli.register(subparsers)
    iccicd.ci.cli.register(subparsers)

    args = parser.parse_args()
    launch_common(args)
    args.func(args)


if __name__ == "__main__":
    main_cli()
