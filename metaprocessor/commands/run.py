import click


@click.group()
def run() -> None:
    """
    Run MetaProcessor workflow.
    """
    pass


@run.command()
def preprocess() -> None:
    """
    Preprocess raw IMU data.
    """
    pass
