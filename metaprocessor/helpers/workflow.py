import json
import pathlib
import re
import time
import zipfile

import pandas as pd


def generate_tasks(config: dict) -> list:
    location = config["general"]["gd-location"]
    regex = re.compile("-".join([config["general"]["sg-regex"], config["general"]["sp-regex"], config["general"]["sd-regex"]]))
    tasks = []
    for file in pathlib.Path(location).glob("**/*.zip"):
        if regex.search(file.name):
            tasks.append(file)
    return tasks


def get_task_metadata(task: pathlib.Path) -> dict:
    with zipfile.ZipFile(task, "r") as dp:
        return json.loads(dp.read(
            task.name.split(".zip")[0] + "-Metadata.json"
        ).decode("utf-8"))


def get_timestamp(input: str, offset: float) -> int:
    return int(int(time.mktime(time.strptime(
                input, "%Y-%m-%dT%H.%M.%S"
    ))) * 1000 - (offset * 3600 * 1000))


def align_timestamp(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    df = df.sort_values(by=["epoc (ms)"], ascending=True)

    diff = int(start - df["epoc (ms)"][0])
    df["epoc (ms)"] = df["epoc (ms)"].apply(lambda x: x + diff)

    if end >= df.iloc[-1]["epoc (ms)"]:
        cutoff_index = -1
    else:
        cutoff_index = df[df["epoc (ms)"] >= end].index[0]
    df = df.iloc[:cutoff_index]

    return df


def merge(acce: pathlib.Path, gyro: pathlib.Path, start: int, end: int) -> pd.DataFrame:
    df = pd.DataFrame(columns=[
        "epoc (ms)",
        "x-axis (g)", "y-axis (g)", "z-axis (g)",
        "x-axis (deg/s)", "y-axis (deg/s)", "z-axis (deg/s)"
    ])

    acce = pd.read_csv(acce, engine="pyarrow")
    acce.columns = [
        "epoc (ms)", "x-axis (g)", "y-axis (g)", "z-axis (g)"
    ]
    acce = align_timestamp(acce, start, end)

    gyro = pd.read_csv(gyro, engine="pyarrow")
    gyro.columns = [
        "epoc (ms)", "x-axis (deg/s)", "y-axis (deg/s)", "z-axis (deg/s)"
    ]
    gyro = align_timestamp(gyro, start, end)

    if acce.shape[0] > gyro.shape[0]:
        df = pd.merge_asof(
            acce, gyro, on="epoc (ms)"
        )
    else:
        df = pd.merge_asof(
            gyro, acce, on="epoc (ms)"
        )
        df = df[df.columns[[0, 4, 5, 6, 1, 2, 3]]]

    return df


def preprocess(task: pathlib.Path, config: dict) -> None:
    folder = pathlib.Path(task.as_posix().split(".zip")[0])
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(task, "r") as dp:
            dp.extractall(folder)

    if (folder/(folder.name+"-Preprocessed.csv")).exists() and (folder/(folder.name+"-Preprocessed.feather")).exists():
        return

    metadata = get_task_metadata(task)
    offset = config["general"]["utc-offset"]
    start = get_timestamp(metadata["start_time"], offset)
    end = get_timestamp(metadata["end_time"], offset)

    acce = folder/(folder.name+"-Accelerometer.csv")
    gyro = folder/(folder.name+"-Gyroscope.csv")

    df = merge(acce, gyro, start, end)
    df.to_csv(folder/(folder.name+"-Preprocessed.csv"), index=False)
    df.to_feather(folder/(folder.name+"-Preprocessed.feather"))
