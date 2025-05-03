"""
CLI handlers for the `packaging` module
"""

import os
from pathlib import Path
import logging

from iccicd.packaging.python_package import deploy


logger = logging.getLogger(__name__)


def deploy_cli(args):

    logger.info("Doing deployment")

    deploy(args.repo_dir, args.token, args.use_test_repo)

    logger.info("Finished deployment")


def register(subparsers):

    parser = subparsers.add_parser("deploy")
    parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to be deployed",
    )

    parser.add_argument(
        "--token",
        type=str,
        default="",
        help="Authentication token for the target repo",
    )

    parser.add_argument(
        "--use_test_repo",
        type=bool,
        default=False,
        help="If there is an available test repo use it.",
    )
    parser.set_defaults(func=deploy_cli)
