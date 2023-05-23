import click


@click.group()
def metawear() -> None:
    """
    MetaWear firmware level interactions.
    """
    pass


@metawear.command()
def download() -> None:
    """
    Download raw IMU data from MetaWear.
    """
    pass


@metawear.command()
def reset() -> None:
    """
    Reset MetaWear to factory settings.
    """
    pass
