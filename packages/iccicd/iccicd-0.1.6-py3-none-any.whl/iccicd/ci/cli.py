import os
import logging
from pathlib import Path

from .ci import gitlab_ci_push, sync_external_archive

logger = logging.getLogger(__name__)


def gitlab_ci_push_cli(args):

    logger.info("CI pushing state of current checkout")

    gitlab_ci_push(
        args.user_name, args.user_email, args.repo_url, args.token, args.message
    )

    logger.info("CI finished pushing state of current checkout")


def register_ci_push(subparsers):

    parser = subparsers.add_parser("ci_push")
    parser.add_argument("--user_name", type=str, help="Name of the CI user")
    parser.add_argument("--user_email", type=str, help="Email of the CI user")
    parser.add_argument(
        "--instance_url", type=str, help="Url for the target ci instance"
    )
    parser.add_argument(
        "--url", type=str, help="Url for the repo relative to the ci instance"
    )
    parser.add_argument("--token", type=str, help="Oath access token for the repo")
    parser.add_argument("--message", type=str, help="Commit message")
    parser.set_defaults(func=gitlab_ci_push_cli)


def sync_external_archive_cli(args):

    logger.info("Starting external package sync")

    sync_external_archive(
        repo_dir=args.repo_dir,
        project_id=args.project_id,
        sync_script=args.sync_script,
        asset_name=args.asset_name,
        archive_name=args.archive_name,
        source_token=args.source_token,
        user_name=args.user_name,
        user_email=args.user_email,
        url=args.url,
        target_token=args.target_token,
        target_repo_url=args.target_repo_url,
    )

    logger.info("Finished external package sync")


def register_sync_exterinal(subparsers):

    parser = subparsers.add_parser("sync_external_archive")
    parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to increment the tag",
    )

    parser.add_argument(
        "--project_id",
        type=int,
        help="The id of the project to sync against.",
    )
    parser.add_argument(
        "--source_token", type=str, default="", help="Access token for the source repo"
    )

    parser.add_argument("--user_name", type=str, default="", help="Name of the CI user")
    parser.add_argument(
        "--user_email", type=str, default="", help="Email of the CI user"
    )

    parser.add_argument(
        "--url",
        type=str,
        default="https://git.ichec.ie",
        help="Url for the Gitlab instance",
    )
    parser.add_argument(
        "--target_token", type=str, default="", help="Oath access token for the repo"
    )

    parser.add_argument(
        "--asset_name", type=str, help="Name of the release asset for the archive"
    )
    parser.add_argument(
        "--archive_name", type=str, help="Name of the downloaded archive"
    )
    parser.add_argument(
        "--sync_script", type=Path, help="Path to script to do the sync"
    )
    parser.add_argument(
        "--target_repo_url", type=str, default="", help="Url for the target repo"
    )
    parser.set_defaults(func=sync_external_archive_cli)


def register(subparser):

    register_ci_push(subparser)
    register_sync_exterinal(subparser)
