from pathlib import Path
from typing import Any, cast
import logging
import tomlkit
from tomlkit import TOMLDocument

from iccore.project import version, Version

logger = logging.getLogger(__name__)


_DEFAULT_FILENAME = "pyproject.toml"


def read(path: Path, filename: str = _DEFAULT_FILENAME) -> dict[str, Any]:
    with open(path / filename, "r") as f:
        content = f.read()
    return tomlkit.parse(content)


def write(path: Path, content: dict[str, Any], filename: str = _DEFAULT_FILENAME):
    with open(path / filename, "w") as f:
        f.write(tomlkit.dumps(cast("TOMLDocument", content)))


def get_version(path: Path, filename: str = _DEFAULT_FILENAME) -> Version:
    content = read(path, filename)
    return version.parse(content["project"]["version"])


def set_version(path: Path, ver: Version, filename: str = _DEFAULT_FILENAME):
    content = read(path, filename)
    content["project"]["version"] = ver.as_string()
    write(path, content, filename)
