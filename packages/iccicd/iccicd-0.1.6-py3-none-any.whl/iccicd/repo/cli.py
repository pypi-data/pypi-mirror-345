"""
CLI handling for the 'repo' module.
"""

import logging
from pathlib import Path
import argparse
import os

from iccore.project import version

from iccicd import repo
from iccicd.repo import python_repo


logger = logging.getLogger(__name__)


def set_version(args) -> None:
    """
    Set the project's version via its configuration files. At the moment
    only Python is supported.
    """

    logger.info("Setting version number")

    python_repo.set_version(
        repo.Repo(path=args.repo_dir, version=version.parse(args.version))
    )

    logger.info("Finished setting version number")


def increment_tag_cli(args) -> None:
    """
    Increment the repo's git tag
    """

    logger.info("Incrementing tag")

    if args.token:
        logger.info("Have access token")
    if args.url:
        logger.info("Have remote url")

    repo.increment_tag(
        args.repo_dir,
        args.field,
        args.schema,
        args.check,
        args.branch,
        args.url,
        repo.Secret(data=args.token),
        args.user_name,
        args.user_email,
    )

    logger.info("Finished incrementing tag")


def register(subparsers):
    """
    Register the module's CLI handlers
    """

    set_version_parser = subparsers.add_parser("set_version")
    set_version_parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to set the version",
    )

    set_version_parser.add_argument(
        "version",
        type=str,
        help="The version to set",
    )
    set_version_parser.set_defaults(func=set_version)

    increment_tag_parser = subparsers.add_parser("increment_tag")
    increment_tag_parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to increment the tag",
    )

    increment_tag_parser.add_argument(
        "--field",
        type=str,
        default="patch",
        help="The tag field to increment: 'major', 'minor' or 'patch'",
    )
    increment_tag_parser.add_argument(
        "--schema",
        type=str,
        default="semver",
        help="The tag schema, 'semver' or 'date'",
    )
    increment_tag_parser.add_argument(
        "--check",
        action=argparse.BooleanOptionalAction,
        help="Only do the increment if there are changes on the target branch",
    )
    increment_tag_parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Name of the branch to check against",
    )
    increment_tag_parser.add_argument(
        "--user_name", type=str, default="", help="Name of the CI user"
    )
    increment_tag_parser.add_argument(
        "--user_email", type=str, default="", help="Email of the CI user"
    )
    increment_tag_parser.add_argument(
        "--url", type=str, default="", help="Url for the repo remote"
    )
    increment_tag_parser.add_argument(
        "--token", type=str, default="", help="Oath access token for the repo"
    )
    increment_tag_parser.set_defaults(func=increment_tag_cli)
