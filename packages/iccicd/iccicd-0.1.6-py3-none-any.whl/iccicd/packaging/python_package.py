from pathlib import Path
import logging

from pydantic import BaseModel

from iccore.system import process


logger = logging.getLogger(__name__)


class PyPiContext(BaseModel, frozen=True):

    token: str
    use_test_repo: bool = False


class PythonPackage(BaseModel, frozen=True):
    repo_path: Path


def build(package: PythonPackage):
    logger.info("Building Python package")
    output_dir = package.repo_path / "dist"
    cmd = f"python3 -m build --outdir {output_dir} {package.repo_path}"
    process.run(cmd)
    logger.info("Finished building Python package")


def upload(package: PythonPackage, pypi_context: PyPiContext):
    logger.info("Uploading Python package")

    if not pypi_context.token:
        raise RuntimeError("Provided PyPi token cannot be empty")

    repo = ""
    if pypi_context.use_test_repo:
        repo = " -r testpypi "

    token = f"-p {pypi_context.token}"
    upload_dir = package.repo_path / "dist"
    cmd = f"twine upload {upload_dir}/*  --non-interactive {token} {repo}"
    process.run(cmd)
    logger.info("Finished uploading Python package")


def deploy(repo_path: Path, token: str, use_test_repo: bool = False):
    package = PythonPackage(repo_path=repo_path)
    build(package)
    upload(package, PyPiContext(token=token, use_test_repo=use_test_repo))
