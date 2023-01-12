"""
Core
"""
import argparse
import sys

from .modules import link_io
from .modules.linktree import LinkTree
from .modules.color import color
from .modules.updater import check_version
from .modules.savefile import saveJson
from .modules.info import execute_all
from .modules.collect_data import collect_data
from .modules.nlp import main

from . import version


# TorBot CLI class
class TorBot:

    def __init__(self, args):
        self.args = args

    def get_header(self):
        license_msg = color("LICENSE: GNU Public License v3", "red")
        banner = r"""
                              __  ____  ____  __        ______
                             / /_/ __ \/ __ \/ /_  ____/_  __/
                            / __/ / / / /_/ / __ \/ __ \/ /
                           / /_/ /_/ / _, _/ /_/ / /_/ / /
                           \__/\____/_/ |_/_____/\____/_/  V{VERSION}
                """.format(VERSION=version.__version__)
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

    def handle_json_args(self, args):
        """
        Outputs JSON file for data
        """

        # -m/--mail
        if args.mail:
            email_json = link_io.print_emails(args.url)
            if args.save:
                saveJson('Emails', email_json)
        # -p/--phone
        if args.phone:
            phone_json = link_io.print_phones(args.url)
            if args.save:
                saveJson('Phones', phone_json)
        # -s/--save
        else:
            node_json = link_io.print_json(args.url, args.depth)
            saveJson("Links", node_json)

    def handle_tree_args(self, args):
        """
        Outputs tree visual for data
        """
        tree = LinkTree(args.url, args.depth)
        # -v/--visualize
        if args.visualize:
            tree.show()

        # -d/--download
        if args.download:
            file_name = str(input("File Name (.txt): "))
            tree.save(file_name)

    def perform_action(self):
        args = self.args
        if args.gather:
            collect_data(args.url)
            return

        # If flag is -v, --update, -q/--quiet then user only runs that operation
        # because these are single flags only
        if args.version:
            print("TorBot Version:" + self.__version__)
            sys.exit()
        if args.update:
            check_version()
            sys.exit()
        if not args.quiet:
            self.get_header()
        # If url flag is set then check for accompanying flag set. Only one
        # additional flag can be set with -u/--url flag
        if not args.url:
            print("usage: See run.py -h for possible arguments.")
        link_io.print_tor_ip_address()
        if args.classify:
            result = main.classify(args.url)
            print("Website Classification: " + result[0], "| Accuracy: " + str(result[1]))
        if args.visualize or args.download:
            self.handle_tree_args(args)
            # raise NotImplementedError("Tree visualization and download is not available yet.")
        elif args.save or args.mail or args.phone:
            self.handle_json_args(args)
        # -i/--info
        elif args.info:
            execute_all(args.url)
        else:
            if args.url:
                link_io.print_tree(args.url, args.depth, args.classifyAll)
        print("\n\n")


def get_args():
    """
    Parses user flags passed to TorBot
    """
    parser = argparse.ArgumentParser(prog="TorBot", usage="Gather and analayze data from Tor sites.")
    parser.add_argument("--version", action="store_true", help="Show current version of TorBot.")
    parser.add_argument("--update", action="store_true", help="Update TorBot to the latest stable version")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-u", "--url", help="Specifiy a website link to crawl")
    parser.add_argument("-s", "--save", action="store_true", help="Save results in a file")
    parser.add_argument("-m", "--mail", action="store_true", help="Get e-mail addresses from the crawled sites")
    parser.add_argument("-p", "--phone", action="store_true", help="Get phone numbers from the crawled sites")
    parser.add_argument("--depth", help="Specifiy max depth of crawler (default 1)", default=1)
    parser.add_argument("--gather", action="store_true", help="Gather data for analysis")
    parser.add_argument("-v", "--visualize", action="store_true", help="Visualizes tree of data gathered.")
    parser.add_argument("-d", "--download", action="store_true", help="Downloads tree of data gathered.")
    parser.add_argument(
        "-e",
        "--extension",
        action='append',
        dest='extension',
        default=[],
        help=' '.join(("Specifiy additional website", "extensions to the list(.com , .org, .etc)"))
    )
    parser.add_argument("-c", "--classify", action="store_true", help="Classify the webpage using NLP module")
    parser.add_argument(
        "-cAll", "--classifyAll", action="store_true", help="Classify all the obtained webpages using NLP module"
    )
    parser.add_argument(
        "-i", "--info", action="store_true", help=' '.join(("Info displays basic info of the scanned site"))
    )
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_args()
        torbot = TorBot(args)
        torbot.perform_action()
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
