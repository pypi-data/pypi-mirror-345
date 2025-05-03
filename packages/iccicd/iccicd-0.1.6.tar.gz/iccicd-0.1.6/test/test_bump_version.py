from pathlib import Path
import shutil
import os

from iccore.test_utils import get_test_data_dir, get_test_output_dir

from iccicd.repo import python_repo, Repo


def setup_mock_repo(name, output_dir):

    repo_dir = get_test_data_dir() / name
    output_repo_dir = output_dir / name
    os.makedirs(output_dir)
    shutil.copytree(repo_dir, output_repo_dir)
    shutil.move(
        output_repo_dir / "testpyproject.toml", output_repo_dir / "pyproject.toml"
    )
    shutil.move(output_repo_dir / "docs/conf.xpy", output_repo_dir / "docs/conf.py")


def test_increment_python_repo_version():

    name = "version_bump"
    output_dir = get_test_output_dir()
    setup_mock_repo(name, output_dir)

    version = python_repo.get_version(output_dir / name)

    python_repo.increment_version(
        repo=Repo(path=output_dir / name, version=version), field="minor"
    )

    pp_version = python_repo.pyproject.get_version(output_dir / name)
    sphinx_version = python_repo.sphinx.get_version(output_dir / name)

    shutil.rmtree(output_dir)

    assert pp_version.major == 0
    assert pp_version.minor == 1
    assert pp_version.patch == 0

    assert sphinx_version.major == 0
    assert sphinx_version.minor == 1
    assert sphinx_version.patch == 0
