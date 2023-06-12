import json as libjson

import click
from rich import print

import metaprocessor.helpers.config


@click.group()
def config() -> None:
    """
    Manage MetaProcessor configurations.
    """
    pass


@config.command()
@click.option(
    "--interactive",
    is_flag=True,
    help="Interactively configure MetaProcessor.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force to overwrite existing configuration file.",
)
def init(interactive: bool, force: bool) -> None:
    """
    Initialize MetaProcessor configurations.
    """
    default_config = {
        "general": {  # General settings
            "utc-offset": 0.0,  # UTC offset in hours
            "gd-location": "",  # Global Data Storage location
            "gp-regex": "*",  # Global Project ID regex
            "sg-regex": "*",  # Study Group ID regex
            "sp-regex": "*",  # Study Participant ID regex
            "sd-regex": "*",  # Recording Device ID regex
        },
        "aws": {  # Cloud object store settings, must be S3 compatible
            "endpoint": "",  # Endpoint URL, leave empty for AWS S3
            "region": "",  # Region name, leave empty for AWS S3
            "bucket": "",  # Bucket name
            "access-key": "",  # Access key ID
            "secret-key": "",  # Secret access key
        },
    }

    if metaprocessor.helpers.config.exist() and not force:
        print(
            "[white][red]Configuration file already exists[/red], "
            "please run [u]\\[metaprocessor|mp] config edit[/u] instead, "
            "or use [u]--force[/u] to overwrite.[/white]"
        )
        raise SystemExit(1)
    elif metaprocessor.helpers.config.exist() and force:
        print(
            "[white][yellow]Configuration file already exists[/yellow], "
            "overwriting...[/white]"
        )

    if interactive:
        for section in default_config:
            for key in default_config[section]:
                default_config[section][key] = click.prompt(
                    f"{section}.{key}",
                    default=default_config[section][key],
                )

    metaprocessor.helpers.config.write(default_config)


@config.command()
def edit() -> None:
    """
    Edit MetaProcessor configurations.
    """
    if not metaprocessor.helpers.config.exist():
        print(
            "[white][red]No configuration file found[/red], "
            "please run [u]\\[metaprocessor|mp] config init[/u] first.[/white]"
        )
        return
    else:
        metaprocessor.helpers.config.edit()


@config.command()
def check() -> None:
    """
    Check MetaProcessor configurations.
    """
    if not metaprocessor.helpers.config.exist():
        print(
            "[white][red]No configuration file found[/red], "
            "please run [u]\\[metaprocessor|mp] config init[/u] first.[/white]"
        )
        return
    else:
        config = metaprocessor.helpers.config.read()
        rule = {  # (required, type)
            "general": {
                "utc-offset": (True, float),
                "gd-location": (True, str),
                "gp-regex": (True, str),
                "sg-regex": (True, str),
                "sp-regex": (True, str),
                "sd-regex": (True, str),
            },
            "aws": {
                "endpoint": (False, str),
                "region": (False, str),
                "bucket": (True, str),
                "access-key": (True, str),
                "secret-key": (True, str),
            },
        }

        print(
            f"[white]In [u]{metaprocessor.helpers.config.location()}[/u]:[/white]")
        error_count = 0
        for section in rule:
            for key in rule[section]:
                if rule[section][key][0] and key not in config[section]:
                    print(
                        f"\t[red]Unfilled Option: [blue]{section}.{key}[/blue] is required[/red]."
                    )
                    error_count += 1
                elif key in config[section]:
                    if not isinstance(config[section][key], rule[section][key][1]):
                        print(
                            f"\t[red]Invalid Type: [blue]{section}.{key}[/blue] should be {rule[section][key][1]}[/red]."
                        )
                        error_count += 1
        if error_count == 0:
            print("[white][green]No error found[/green].[/white]")
        else:
            print(
                f"[white][red]{error_count} error(s) found.[/red]\n"
                f"Please run [u]\\[metaprocessor|mp] config edit[/u] to fix above error(s).[/white]"
            )


@config.command()
@click.option(
    "--json",
    is_flag=True,
    help="Show configurations in JSON format.",
)
def show(json: bool) -> None:
    """
    Show MetaProcessor configurations.
    """
    if not metaprocessor.helpers.config.exist():
        print(
            "[white][red]No configuration file found[/red], "
            "please run [u]\\[metaprocessor|mp] config init[/u] first.[/white]"
        )
        return
    else:
        config = metaprocessor.helpers.config.read()
        if json:
            print(libjson.dumps(config, indent=2))
        else:
            for section in config:
                print(f"[white][u]{section}[/u]:[/white]")
                for key in config[section]:
                    print(f"\t[white]{key} = {config[section][key]}[/white]")
