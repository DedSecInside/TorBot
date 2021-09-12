"""
MAIN MODULE
"""
import argparse
import sys

from requests.exceptions import HTTPError

from modules import link_io
from modules.analyzer import LinkTree
from modules.color import color
from modules.link import LinkNode
from modules.updater import updateTor
from modules.savefile import saveJson
from modules.info import execute_all
from modules.collect_data import collect_data

# TorBot VERSION
__VERSION = "2.0.0"

def header():
    """
    Prints out header ASCII art
    """
    license_msg = color("LICENSE: GNU Public License v3", "red")
    banner = r"""
                           __  ____  ____  __        ______
                          / /_/ __ \/ __ \/ /_  ____/_  __/
                         / __/ / / / /_/ / __ \/ __ \/ /
                        / /_/ /_/ / _, _/ /_/ / /_/ / /
                        \__/\____/_/ |_/_____/\____/_/  V{VERSION}
              """.format(VERSION=__VERSION)
    banner = color(banner, "red")

    title = r"""
                                    {banner}
                    #######################################################
                    #  TorBot - An OSINT Tool for Dark Web                #
                    #  GitHub : https://github.com/DedsecInside/TorBot    #
                    #  Help : use -h for help text                        #
                    #######################################################
                                  {license_msg}
              """

    title = title.format(license_msg=license_msg, banner=banner)
    print(title)


def get_args():
    """
    Parses user flags passed to TorBot
    """
    parser = argparse.ArgumentParser(prog="TorBot",
                                     usage="Gather and analayze data from Tor sites.")
    parser.add_argument("--version", action="store_true",
                        help="Show current version of TorBot.")
    parser.add_argument("--update", action="store_true",
                        help="Update TorBot to the latest stable version")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-e", "--extension", action='append', dest='extension',
                        default=[],
                        help=' '.join(("Specifiy additional website",
                                       "extensions to the list(.com , .org, .etc)")))
    parser.add_argument("-i", "--info", action="store_true",
                        help=' '.join(("Info displays basic info of the",
                                       "scanned site")))
    parser.add_argument("--gather", action="store_true",
                        help="Gather data for analysis")

    parser.add_argument("-u", "--url", help="Specifiy a website link to crawl")
    parser.add_argument("--depth", default=1,
                        help="Specifiy max depth of crawler (default 1)")

    add_tree_args(parser)
    add_json_args(parser)
    return parser.parse_args()


def main():
    """
    TorBot's Core
    """
    args = get_args()
    if args.gather:
        collect_data(args.url)
        return

    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args.version:
        print("TorBot Version:" + __VERSION)
        sys.exit()
    if args.update:
        updateTor()
        sys.exit()
    if not args.quiet:
        header()

    # If url flag is set then check for accompanying flag set. Only one
    # additional flag can be set with -u/--url flag
    if not args.url:
        print("usage: See torBot.py -h for possible arguments.")

    link_io.print_tor_ip_address()
    if args.visualize or args.download:
        handle_tree_args(args)
    elif args.save or args.mail:
        handle_json_args(args)
    # -i/--info
    elif args.info:
        execute_all(args.url)
    else:
        link_io.print_tree(args.url, args.depth)
    print("\n\n")


def handle_json_args(args):
    """
    Outputs JSON file for data
    """

    # -m/--mail
    if args.mail:
        email_json = link_io.print_emails(args.url)
        if args.save:
            saveJson('Emails', email_json)
    # -s/--save
    else:
        node_json = link_io.print_json(args.url, args.depth)
        saveJson("Links", node_json)


def add_json_args(parser):
    """
    Outputs JSON file for data
    """
    parser.add_argument("-s", "--save", action="store_true",
                        help="Save results in a file")

    parser.add_argument("-m", "--mail", action="store_true",
                        help="Get e-mail addresses from the crawled sites")


def handle_tree_args(args):
    """
    Outputs tree visual for data
    """
    tree = LinkTree(args.url, args.depth)
    # -v/--visualize
    if args.visualize:
        tree.show()

    # -d/--download
    if args.download:
        file_name = str(input("File Name (.pdf/.png/.svg): "))
        tree.save(file_name)


def add_tree_args(parser):
    """
    Outputs tree visual for data
    """
    parser.add_argument("-v", "--visualize", action="store_true",
                        help="Visualizes tree of data gathered.")
    parser.add_argument("-d", "--download", action="store_true",
                        help="Downloads tree of data gathered.")


def test(args):

    """
    TorBot's Core
    """
    #args = get_args()
    #if args['gather']==True:
     #   collect_data()
     #   return
    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args['version']==True:
        print("TorBot Version:" + __VERSION)
        exit()
    #if args['update']==True:
      #  updateTor()
      # exit()
   # if not args['quiet']==True:
     #   header()
    # If url flag is set then check for accompanying flag set. Only one
    # additional flag can be set with -u/--url flag
    if "url" in args:
        print("url",args['url'])
        url = args['url']
        try:
            node = LinkNode(url)
            print("Node",node)
            print("Link Node",LinkNode(url))
        except (ValueError, HTTPError, ConnectionError) as err:
            raise err
        print("display_ip()",link_io.print_tor_ip_address())
        # -m/--mail
        if args['mail']==True:
            print(node.emails)
            if args['save']==True:
                saveJson('Emails', node.emails)
        # -i/--info
        if args['info']==True:
            execute_all(node.uri)
            if args['save']:
                print('Nothing to save.\n')
        #if args['visualize']==True:
        #    if "depth" in args:
        #        tree = LinkTree(node, stop_depth=args['depth'])
        #    else:
        #        tree = LinkTree(node)
        #    tree.show()
        if args['download']==True:
            tree = LinkTree(node)
            file_name = str(input("File Name (.pdf/.png/.svg): "))
            tree.save(file_name)
        else:
            link_io.print_tree(url)
            if args['save']==True:
                saveJson("Links", node.links)
    else:
        print("usage: See torBot.py -h for possible arguments.")

    print("\n\n")
    #jsonvalues = [node.json_data, node.links]
    return node.links


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
