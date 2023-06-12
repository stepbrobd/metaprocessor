import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
from rich import print
import pandas as pd
import os
import json as libjson
import datetime
import time
import pathlib
import botocore
from concurrent.futures.thread import ThreadPoolExecutor
import metaprocessor.helpers.config
import metaprocessor.helpers.boto3


@click.group()
def objects() -> None:
    """
    Manage MetaProcessor objects.
    """
    pass


@objects.command()
@optgroup.group(
    "Target location settings",
    help="List either local or remote objects, if no flags are provided, all objects will be listed.",
    cls=MutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--local",
    is_flag=True,
    help="List local objects.",
)
@optgroup.option(
    "--remote",
    is_flag=True,
    help="List remote objects.",
)
@click.option(
    "--json",
    is_flag=True,
    help="Show objects in JSON format.",
)
def ls(local: bool, remote: bool, json: bool) -> None:
    """
    List objects managed by MetaProcessor.
    """
    pd.set_option("display.width", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    config = metaprocessor.helpers.config.read()
    result = pd.DataFrame()

    if not local and not remote:
        local = True
        remote = True

    if local:
        location = config.get("general", {}).get("gd-location")
        if location is None:
            print(
                "[white][red]No location set[/red], "
                "please run [u]\[metaprocessor|mp] config edit[/u] to set location.[/white]"
            )
            return
        else:
            for root, _, files in os.walk(location):
                for file in files:
                    path = pathlib.Path(root)/file
                    result = pd.concat([
                        result,
                        pd.DataFrame({
                            "ETag": ["N/A"],
                            "Key": [str(path.relative_to(location))],
                            "Version ID": ["N/A"],
                            "Size": [path.stat().st_size],
                            "Last Modified": [datetime.datetime.fromtimestamp(path.stat().st_mtime, tz=datetime.timezone(datetime.timedelta(seconds=-time.timezone)))],
                            "Deleted": [False],
                            "Location": ["Local"],
                        })
                    ])

    if remote:
        response = metaprocessor.helpers.boto3.list_objects()

        deleted = pd.DataFrame()
        for object in response.get("DeleteMarkers", []):
            deleted = pd.concat([
                deleted,
                pd.DataFrame({
                    "Key": [object["Key"]],
                    "Version ID": [object["VersionId"]],
                    "Last Modified": [object["LastModified"]],
                })
            ])
        deleted = deleted.sort_values(by=["Last Modified"], ascending=False)
        deleted.index = range(len(deleted.index))

        current = pd.DataFrame()
        for object in response.get("Versions", []):
            if object["Size"] > 0 and object["Key"][-1] != "/":
                current = pd.concat([
                    current,
                    pd.DataFrame({
                        # remove double quotes from ETag
                        "ETag": [object["ETag"][1:-1]],
                        "Key": [object["Key"]],
                        "Version ID": [object["VersionId"]],
                        "Size": [object["Size"]],
                        "Last Modified": [object["LastModified"]],
                    })
                ])
        current = current.sort_values(by=["Last Modified"], ascending=False)
        current.index = range(len(current.index))

        for i in range(len(current.index)):
            for j in range(len(deleted.index)):
                if current.loc[i, "Key"] == deleted.loc[j, "Key"]:
                    current.loc[i, "Version ID"] = deleted.loc[
                        j, "Version ID"
                    ]
                    current.loc[i, "Last Modified"] = deleted.loc[
                        j, "Last Modified"
                    ]
                    current.loc[i, "Deleted"] = True
                    break
                else:
                    current.loc[i, "Deleted"] = False
            current.loc[i, "Location"] = "Remote"

        result = pd.concat([result, current])

    if len(result) == 0:
        print(
            "[white][red]No objects found[/red], "
            "please make sure configurations are correctly setup or run [u]\[metaprocessor|mp] objects upload[/u] to upload objects.[/white]"
        )
        return
    else:
        result = result.sort_values(by=["Last Modified"], ascending=False)
        result.index = range(len(result.index))

    if json:
        result["Last Modified"] = result["Last Modified"].astype(str)
        print(libjson.dumps(libjson.loads(
            result.to_json(orient="records")), indent=4
        ))
    else:
        print(result)


@objects.command()
def mv() -> None:
    """
    Move (or rename) objects managed by MetaProcessor.
    """
    print(
        "[white][red]Not implemented yet[/red], "
        "please see [u]https://github.com/metaprocessor/metaprocessor/blob/master/metaprocessor/commands/objects.py[/u] to check implantation status.[/white]"
    )


@objects.command()
def rm() -> None:
    """
    Delete objects from MetaProcessor.
    """
    print(
        "[white][red]Not implemented yet[/red], "
        "please see [u]https://github.com/metaprocessor/metaprocessor/blob/master/metaprocessor/commands/objects.py[/u] to check implantation status.[/white]"
    )


@objects.command()
def upload() -> None:
    """
    Upload objects to cloud object store.
    """


@objects.command()
@click.option(
    "--key",
    required=False,
    help="Key of the object to download.",
)
def download(key: str) -> None:
    """
    Download objects from cloud object store.
    """
    config = metaprocessor.helpers.config.read()
    response = metaprocessor.helpers.boto3.list_objects()
    etags = {
        object["Key"]: object["ETag"]
        for object in response.get("Versions", [])
    }
    sizes = {
        object["Key"]: object["Size"]
        for object in response.get("Versions", [])
    }

    base = config.get("general", {}).get("gd-location")
    if not base:
        print(
            "[white][red]No location set[/red], "
            "please run [u]\[metaprocessor|mp] config edit[/u] to set location.[/white]"
        )
        return

    def cached_download(key: str) -> None:
        location = pathlib.Path(base) / key

        for parent in reversed(location.parents):
            if not parent.exists():
                parent.mkdir()

        if location.is_file() and metaprocessor.helpers.boto3.verify_object(str(location), etags[key]):
            print(
                f"[white][green]Object with key \"{key}\" already exists[/green], "
                f"the integrity of the file has been verified, skipping download.[/white]"
            )
        else:
            metaprocessor.helpers.boto3.download_object(
                key, str(location), sizes[key]
            )

    if not key:
        valid_keys = []
        deleted_keys = []

        for object in response.get("Versions", []):
            if object["Size"] > 0 and object["Key"][-1] != "/":
                valid_keys.append(object["Key"])

        for object in response.get("DeleteMarkers", []):
            deleted_keys.append(object["Key"])

        keys = [key for key in valid_keys if key not in deleted_keys]

        with ThreadPoolExecutor() as executor:
            executor.map(cached_download, keys)
    else:
        cached_download(key)
