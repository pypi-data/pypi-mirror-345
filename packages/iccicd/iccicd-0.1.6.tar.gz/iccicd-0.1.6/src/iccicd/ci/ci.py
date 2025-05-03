import logging
from pathlib import Path
import os
import shutil

from iccore.system import process
from iccore import filesystem as fs
from iccore.version_control import (
    GitlabClient,
    GitlabInstance,
    GitRepo,
    GitUser,
    GitlabToken,
)
from iccore.version_control.gitlab_client import get_latest_release

logger = logging.getLogger(__name__)


def gitlab_ci_push(
    user_name: str,
    user_email: str,
    repo_url: str,
    token: str,
    message: str,
    repo_dir: Path = Path(os.getcwd()),
):

    user = GitUser(name=user_name, email=user_email)
    repo = GitRepo(user=user, path=repo_dir)

    gitlab = GitlabClient(
        instance=GitlabInstance(url=repo_url),
        token=GitlabToken(value=token),
        user=user,
        local_repo=repo,
    )

    remote_name = "origin"
    if token:
        remote_name = "oath_origin"
    gitlab.push_change(message, remote_name=remote_name)


def sync_external_archive(
    repo_dir: Path,
    project_id: int,
    asset_name: str,
    archive_name: str,
    sync_script: Path,
    source_token: str = "",
    user_name: str = "",
    user_email: str = "",
    url: str = "",
    target_token: str = "",
    target_repo_url: str = "",
):

    # Download package
    logger.info("Fetching remote asset from %s for project %s", url, project_id)
    work_dir = repo_dir / "_temp"
    os.makedirs(work_dir)
    get_latest_release(
        project_id, url, source_token, "PRIVATE-TOKEN", asset_name, work_dir
    )

    logger.info("Extracting archive from %s", work_dir / asset_name)
    fs.unpack_archive(work_dir / asset_name, work_dir)
    (work_dir / asset_name).unlink()

    # Run sync script
    logger.info("Running sync with %s", repo_dir / sync_script)
    process.run(f"{repo_dir/sync_script} {work_dir}")

    # Clean work working directory
    shutil.rmtree(work_dir)

    # Commit and push change
    logger.info("Pushing change")
    gitlab_ci_push(
        user_name,
        user_email,
        target_repo_url,
        target_token,
        "External_repo_sync",
        repo_dir,
    )

    logger.info("Finished external package sync")
