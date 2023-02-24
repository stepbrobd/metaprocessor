import toml
import pathlib


def exist_config() -> bool:
    return pathlib.Path.home().joinpath(".config", "metaprocessor", "config.toml").exists()


def read_config() -> dict:
    return toml.load(pathlib.Path.home().joinpath(".config", "metaprocessor", "config.toml"))


def write_config(config: dict) -> None:
    file = pathlib.Path.home().joinpath(".config", "metaprocessor", "config.toml")
    file.parent.parent.mkdir(parents=True, exist_ok=True)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch(exist_ok=True)
    with open(pathlib.Path.home().joinpath(".config", "metaprocessor", "config.toml"), "w") as f:
        toml.dump(config, f)
