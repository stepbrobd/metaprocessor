import os
import pathlib

import toml


def location() -> str:
    """
    Check `XDG_CONFIG_HOME` environment variable,
    if it is not set, use `~/.config` instead.
    """
    return pathlib.Path(
        os.environ.get(
            "XDG_CONFIG_HOME",
            pathlib.Path.home().joinpath(".config"),
        )
    )/"metaprocessor"/"config.toml"


def exist() -> bool:
    return pathlib.Path(location()).exists()


def edit() -> None:
    os.system(f"{os.environ.get('EDITOR', 'vim')} {pathlib.Path(location())}")


def read() -> dict:
    return toml.load(pathlib.Path(location()))


def write(config: dict) -> None:
    file = location()
    file.parent.parent.mkdir(parents=True, exist_ok=True)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)
    with open(file, "w") as f:
        toml.dump(config, f)
