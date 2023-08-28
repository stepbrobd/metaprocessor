import datetime
import json
import pathlib
import re
import time
import zipfile
from typing import List

import pandas as pd
from rich import print

from metaprocessor.libs.steps import steps as calculate_steps
from metaprocessor.libs.uptime import uptime as calculate_uptime


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
    df["epoc (ms)"] = df["epoc (ms)"].astype(int)
    df = df.sort_values(by="epoc (ms)", ascending=True)

    diff = start - df["epoc (ms)"].iloc[0]
    df["epoc (ms)"] = df["epoc (ms)"] + diff

    if end > df.iloc[-1]["epoc (ms)"]:
        cutoff = -1
    else:
        cutoff = df[df["epoc (ms)"] > end].index[0]
    df = df.iloc[:cutoff]

    return df.sort_values(by="epoc (ms)", ascending=True)


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

    if acce.shape[0] >= gyro.shape[0]:
        df = pd.merge_asof(
            acce, gyro, on="epoc (ms)"
        )
    else:
        df = pd.merge_asof(
            gyro, acce, on="epoc (ms)"
        )
        df = df[df.columns[[0, 4, 5, 6, 1, 2, 3]]]

    return df


def get_preprocessed(task: pathlib.Path) -> pd.DataFrame:
    folder = pathlib.Path(task.as_posix().split(".zip")[0])
    if not folder.exists():
        raise FileNotFoundError("No preprocessed data found")

    if folder.glob("-Preprocessed.feather"):
        print(f"Using {folder/(folder.name+'-Preprocessed.feather')}")
        return pd.read_feather(folder/(folder.name+"-Preprocessed.feather"))
    elif folder.glob("-Preprocessed.csv"):
        print(f"Using {folder/(folder.name+'-Preprocessed.csv')}")
        return pd.read_csv(folder/(folder.name+"-Preprocessed.csv"))
    else:
        raise FileNotFoundError("No preprocessed data found")


def remove_milliseconds(epoch: int) -> int:
    if len(str(epoch)) == 13:
        return int(str(epoch)[:-3])
    elif len(str(epoch)) == 10:
        return epoch
    else:
        raise ValueError("Epoch must be in milliseconds or seconds")


def get_split_indices(df: pd.DataFrame) -> list:
    """
    Return a list of tuples containing the start and end indices of each split.
    """
    df["datetime"] = pd.to_datetime(df["epoc (ms)"], unit="ms")
    grouped = df.groupby(df["datetime"].dt.date).apply(lambda x: (x.index.min(), x.index.max()))
    df.drop(columns=["datetime"], inplace=True)
    return grouped.tolist()


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

    print(f"[green]Preprocessing {folder.name}[/green]")
    df = merge(acce, gyro, start, end)
    df.to_csv(folder/(folder.name+"-Preprocessed.csv"), index=False)
    df.to_feather(folder/(folder.name+"-Preprocessed.feather"))
    print(f"[green]Preprocessed {folder.name}[/green]")


def uptime(task: pathlib.Path, config: dict) -> None:
    folder = pathlib.Path(task.as_posix().split(".zip")[0])
    output = folder/(folder.name+"-Results.csv")

    df = get_preprocessed(task)
    indices = get_split_indices(df)

    # columns will be uptime, steps, etc.
    results = pd.DataFrame(columns=["uptime (%)"])

    for index, (start, end) in enumerate(indices):
        calc = df.iloc[start:end]
        calc.reset_index(drop=True, inplace=True)
        result = calculate_uptime(calc, gain=1, sample_rate=25, critical_angle=39)
        print(f"\t[green]{folder.name} Day ({index+1}/{len(indices)})[/green]: UpTime: {result}")
        results.loc[index, "uptime (%)"] = result

    if output.exists():
        result_df = pd.read_csv(output)
        result_df["uptime (%)"] = results["uptime (%)"]
    else:
        result_df = results

    result_df.to_csv(output, index=False)

    print(f"[green]Calculated uptime for {folder.name}[/green]")


def steps(task: pathlib.Path, config: dict) -> None:
    folder = pathlib.Path(task.as_posix().split(".zip")[0])
    output = folder/(folder.name+"-Results.csv")

    df = get_preprocessed(task)
    indices = get_split_indices(df)

     # columns will be uptime, steps, etc.
    results = pd.DataFrame(columns=["steps (count)"])

    for index, (start, end) in enumerate(indices):
        calc = df.iloc[start:end]
        calc.reset_index(drop=True, inplace=True)
        result = calculate_steps(calc)
        print(f"\t[green]{folder.name} Day ({index+1}/{len(indices)})[/green]: Steps: {result}")
        results.loc[index, "steps (count)"] = result

    if output.exists():
        result_df = pd.read_csv(output)
        result_df["steps (count)"] = results["steps (count)"]
    else:
        result_df = results

    result_df.to_csv(output, index=False)

    print(f"[green]Calculated steps for {folder.name}[/green]")


def report(tasks: List[pathlib.Path]) -> None:
    results = []
    for task in tasks:
        folder = pathlib.Path(task.as_posix().split(".zip")[0])
        output = folder/(folder.name+"-Results.csv")
        if output.exists():
            results.append(output)
    if len(results) == 0:
        print("[red]No results found.[/red]")
        return

    print(f"[green]Generating report for {len(results)} session(s).[/green]")

    # get all column names from all results
    columns = []
    for result in results:
        df = pd.read_csv(result)
        columns.extend(df.columns.tolist())
    columns = list(set(columns))

    # id, day_1, day_2, day_3, ..., day_99
    result_template = pd.DataFrame(columns=["id"] + [f"day_{i}" for i in range(1, 25)])

    # key is the column name, value is dataframe
    reports = {}
    for column in columns:
        reports[column] = result_template.copy()

    for result in results:
        id = result.parent.name
        rdf = pd.read_csv(result)
        for rc in rdf.columns:
            data = {"id": id}
            for ri, rv in enumerate(rdf[rc]):
                data[f"day_{ri+1}"] = rv
            reports[rc] = pd.concat([reports[rc], pd.DataFrame([data])], ignore_index=True)

    for key, value in reports.items():
        # replace all non-alphanumeric characters with underscore
        feature = re.sub(r"\W+", "_", key)
        # filename
        filename = f"mp-report-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{feature}.csv"
        # mp-report-yyyy-mm-dd-hh-mm-ss-feature.csv
        value.to_csv(f"{pathlib.Path.cwd()}/{filename}", index=False)
        print(f"[green]Generated {filename}[/green]")
