import click

from metaprocessor.commands.config import config
from metaprocessor.commands.metawear import metawear
from metaprocessor.commands.objects import objects


@click.group()
@click.version_option(prog_name="metaprocessor")
def cli() -> None:
    """
    MetaProcessor, all-in-one data pipeline for MbientLab MetaWear series sensors!
    """
    pass


cli.add_command(config)
cli.add_command(metawear)
cli.add_command(objects)
