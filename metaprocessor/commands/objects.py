import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
from rich import print


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


@objects.command()
def mv() -> None:
    """
    Move (or rename) objects managed by MetaProcessor.
    """


@objects.command()
def rm() -> None:
    """
    Delete objects from MetaProcessor.
    """


@objects.command()
def upload() -> None:
    """
    Upload objects to cloud object store.
    """


@objects.command()
def download() -> None:
    """
    Download objects from cloud object store.
    """
