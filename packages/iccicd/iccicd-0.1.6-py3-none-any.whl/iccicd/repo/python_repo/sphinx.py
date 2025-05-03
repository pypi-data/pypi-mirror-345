from pathlib import Path

from iccore.project import version, Version


_DEFAULT_CONF = Path("docs/conf.py")


def set_version(path: Path, ver: Version, conf_path: Path = _DEFAULT_CONF):
    conf_path = path / conf_path
    with open(conf_path, "r") as f:
        lines = f.readlines()

    with open(conf_path, "w") as f:
        for line in lines:
            if "release" in line:
                line = f"release = '{ver.as_string()}'"
            f.write(line)


def _parse_version(line: str) -> Version:
    _, val = line.split("=")
    return version.parse(val.strip().replace("'", ""))


def get_version(path: Path, conf_path: Path = _DEFAULT_CONF) -> Version:
    with open(path / conf_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        if "release" in line:
            return _parse_version(line)
    raise RuntimeError("release key not found in config")
