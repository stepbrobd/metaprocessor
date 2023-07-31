import click

from metaprocessor.commands.completion import completion
from metaprocessor.commands.config import config
from metaprocessor.commands.metawear import metawear
from metaprocessor.commands.object import object
from metaprocessor.commands.run import run


@click.group()
@click.version_option(prog_name="metaprocessor")
def cli() -> None:
    """
    MetaProcessor, all-in-one data pipeline for MbientLab MetaWear series sensors!
    """
    pass


cli.add_command(completion)
cli.add_command(config)
cli.add_command(metawear)
cli.add_command(object)
cli.add_command(run)
