import argparse
import coloredlogs
import logging
import pathlib
import sys
import toml

import metaprocessor.config
import metaprocessor.command.config


__exec__ = pathlib.Path(sys.argv[0]).name
__meta__ = toml.load(pathlib.Path(__file__).parent.parent/"pyproject.toml")

logger = logging.getLogger(__exec__)
coloredlogs.install(level="SPAM")


def __parser__() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__exec__,
        description=__meta__["project"]["description"],
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"MetaProcessor {__meta__['project']['version']} from {sys.argv[0]}"
    )
    subparser = parser.add_subparsers(dest="command")
    subparser.required = True

    config_parser = subparser.add_parser(
        "config",
        help=f"manage {__exec__} configuration",
    )
    config_parser.add_argument(
        "init",
        help="initialize configuration",
    )
    config_parser.add_argument(
        "edit",
        help="edit configuration",
    )
    config_parser.add_argument(
        "show",
        help="show configuration",
    )
    config_parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="interactive configuration",
    )
    config_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="force overwrite existing configuration",
    )

    metawear_parser = subparser.add_parser(
        "metawear",
        help="metawear device operations",
    )
    metawear_parser.add_argument(
        "list",
        help="list metawear devices nearby",
    )
    metawear_parser.add_argument(
        "download",
        help="download data from metawear device",
    )
    metawear_parser.add_argument(
        "reset",
        help="reset metawear device",
    )
    metawear_parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="interactive data entry",
    )
    metawear_parser.add_argument(
        "-m", "--mac",
        type=str,
        help="metawear device MAC address",
    )
    metawear_parser.add_argument(
        "-p", "--patient",
        type=str,
        help="patient ID, will be checked against provide regex in configuration",
    )
    metawear_parser.add_argument(
        "-s", "--session",
        type=str,
        help="session ID, will be checked against provide regex in configuration",
    )
    metawear_parser.add_argument(
        "-d", "--device",
        type=str,
        help="device ID, will be checked against provide regex in configuration",
    )
    metawear_parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=10,
        help="discovery timeout (s)",
    )

    return parser


def main() -> int:
    if not metaprocessor.config.exist_config():
        logger.error(
            f"Configuration file not found. Please run '{__exec__} init' first."
        )

    parser = __parser__()
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    print(args)

    if args.command == "config":
        return metaprocessor.command.config.run()

    return 0
