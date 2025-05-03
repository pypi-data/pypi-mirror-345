from pathlib import Path
import logging

from iccore.project import version, Version

from iccicd.repo import Repo
from iccicd.repo.python_repo import sphinx, pyproject


logger = logging.getLogger(__name__)


def get_version(
    path: Path, pyproject_filename: str = pyproject._DEFAULT_FILENAME
) -> Version:
    return pyproject.get_version(path, pyproject_filename)


def set_version(
    repo: Repo,
    ver: Version | None = None,
    pyproject_filename: str = pyproject._DEFAULT_FILENAME,
    sphinx_filename: Path = sphinx._DEFAULT_CONF,
):
    selected_version = ver if ver else repo.version

    logger.info("Setting project version to %s", selected_version.as_string())

    pyproject.set_version(repo.path, selected_version, pyproject_filename)

    sphinx_path = Path(sphinx_filename)
    if sphinx_path.exists():
        sphinx.set_version(repo.path, selected_version, Path(sphinx_filename))
    else:
        logger.info("No sphinx config found at %s. Skipping.", sphinx_path)


def increment_version(
    repo: Repo,
    field: str,
    pyproject_filename: str = pyproject._DEFAULT_FILENAME,
    sphinx_filename: Path = sphinx._DEFAULT_CONF,
):
    logger.info(
        "Incrementing project %s version from %s", field, repo.version.as_string()
    )
    set_version(
        repo,
        version.increment(repo.version, field),
        pyproject_filename,
        sphinx_filename,
    )
