#!/usr/bin/env python3

import os
import argparse
import sys
import logging
import toml
import httpx

from torbot.modules.api import get_ip
from torbot.modules.color import color
from torbot.modules.updater import check_version
from torbot.modules.info import execute_all
from torbot.modules.linktree import LinkTree


def print_tor_ip_address(client: httpx.Client) -> None:
    """
    https://check.torproject.org/ tells you if you are using tor and it
    displays your IP address which we scape and display
    """
    resp = get_ip(client)
    print(resp["header"])
    print(color(resp["body"], "yellow"))


def print_header(version: str) -> None:
    """
    Prints the TorBot banner including version and license.
    """
    license_msg = color("LICENSE: GNU Public License v3", "red")
    banner = r"""
                            __  ____  ____  __        ______
                            / /_/ __ \/ __ \/ /_  ____/_  __/
                        / __/ / / / /_/ / __ \/ __ \/ /
                        / /_/ /_/ / _, _/ /_/ / /_/ / /
                        \__/\____/_/ |_/_____/\____/_/  v{VERSION}
            """.format(
        VERSION=version
    )
    banner = color(banner, "red")

    title = r"""
                                    {banner}
                    #######################################################
                    #  TorBot - Dark Web OSINT Tool                       #
                    #  GitHub : https://github.com/DedsecInside/TorBot    #
                    #  Help : use -h for help text                        #
                    #######################################################
                                {license_msg}
            """

    title = title.format(license_msg=license_msg, banner=banner)
    print(title)


def run(arg_parser: argparse.ArgumentParser, version: str) -> None:
    args = arg_parser.parse_args()

    # setup logging
    date_fmt = "%d-%b-%y %H:%M:%S"
    logging_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    logging_lvl = logging.DEBUG if args.v else logging.INFO
    logging.basicConfig(level=logging_lvl, format=logging_fmt, datefmt=date_fmt)

    # URL is a required argument
    if not args.url:
        arg_parser.print_help()
        sys.exit()

    # Print verison then exit
    if args.version:
        print(f"TorBot Version: {version}")
        sys.exit()

    # check version and update if necessary
    if args.update:
        check_version()
        sys.exit()

    socks5_host = args.host
    socks5_port = str(args.port)
    socks5_proxy = f"socks5://{socks5_host}:{socks5_port}"
    with httpx.Client(
        timeout=60, proxies=socks5_proxy if not args.disable_socks5 else None
    ) as client:
        # print header and IP address if not set to quiet
        if not args.quiet:
            print_header(version)
            print_tor_ip_address(client)

        if args.info:
            execute_all(client, args.url)

        tree = LinkTree(url=args.url, depth=args.depth, client=client)
        tree.load()

        # save data if desired
        if args.save == "tree":
            tree.save()
        elif args.save == "json":
            tree.saveJSON()

        # always print something, table is the default
        if args.visualize == "table" or not args.visualize:
            tree.showTable()
        elif args.visualize == "tree":
            print(tree)
        elif args.visualize == "json":
            tree.showJSON()

    print("\n\n")


def set_arguments() -> argparse.ArgumentParser:
    """
    Parses user flags passed to TorBot
    """
    parser = argparse.ArgumentParser(
        prog="TorBot", usage="Gather and analayze data from Tor sites."
    )
    parser.add_argument(
        "-u", "--url", type=str, required=True, help="Specifiy a website link to crawl"
    )
    parser.add_argument(
        "--depth", type=int, help="Specifiy max depth of crawler (default 1)", default=1
    )
    parser.add_argument(
        "--host", type=str, help="IP address for SOCKS5 proxy", default="127.0.0.1"
    )
    parser.add_argument("--port", type=int, help="Port for SOCKS5 proxy", default=9050)
    parser.add_argument(
        "--save", type=str, choices=["tree", "json"], help="Save results in a file"
    )
    parser.add_argument(
        "--visualize",
        type=str,
        choices=["table", "tree", "json"],
        help="Visualizes data collection.",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument(
        "--version", action="store_true", help="Show current version of TorBot."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update TorBot to the latest stable version",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Info displays basic info of the scanned site. Only supports a single URL at a time.",
    )
    parser.add_argument("-v", action="store_true", help="verbose logging")
    parser.add_argument(
        "--disable-socks5",
        action="store_true",
        help="Executes HTTP requests without using SOCKS5 proxy",
    )

    return parser


if __name__ == "__main__":
    try:
        arg_parser = set_arguments()
        config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pyproject.toml")
        try:
            with open(config_file_path, "r") as f:
                data = toml.load(f)
                version = data["project"]["version"]
        except Exception as e:
            raise Exception("unable to find version from pyproject.toml.\n", e)

        run(arg_parser, version)
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
