"""
Utilities for working with code repositories in general
"""

from pathlib import Path
import logging

from pydantic import BaseModel

from iccore.project import Version
from iccore.version_control import git, GitRemote, GitUser


class Secret(BaseModel, frozen=True):
    data: str


class Repo(BaseModel, frozen=True):

    path: Path
    version: Version


def increment_tag(
    repo_path: Path,
    field: str,
    schema: str = "semver",
    check: bool = False,
    branch: str = "main",
    url: str = "",
    token: Secret | None = None,
    user_name: str = "",
    user_email: str = "",
) -> None:
    """
    Increment the git tag on a repository
    """

    remote: str | None = None
    if url and token:
        logging.info("Setting oath remote")
        remote = "oath_remote"
        url_prefix = f"https://oauth2:{token.data}"
        git.add_remote(repo_path, GitRemote(name=remote, url=f"{url_prefix}@{url}"))

    if user_name and user_email:
        git.set_user(repo_path, GitUser(name=user_name, email=user_email))

    git.increment_tag(repo_path, schema, field, branch, check, remote)
