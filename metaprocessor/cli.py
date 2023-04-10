import click


from metaprocessor.commands.config import config


@click.group()
@click.version_option(prog_name="metaprocessor")
def cli() -> None:
    """
    MetaProcessor, all-in-one data pipeline for MbientLab MetaWear series sensors!
    """
    pass


cli.add_command(config)
