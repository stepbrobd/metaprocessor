import click

from metaprocessor.helpers.decorator import linux_only


@click.group()
def metawear() -> None:
    """
    MetaWear firmware level interactions.
    """
    pass


@metawear.command()
@linux_only
def download() -> None:
    """
    Download raw IMU data from MetaWear.
    """
    pass

@metawear.command()
@linux_only
def reset() -> None:
    """
    Reset MetaWear to factory settings.
    """
    pass
