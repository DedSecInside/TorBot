"""
MAIN MODULE
"""
import argparse
import socket
import socks

from requests.exceptions import HTTPError

from modules.analyzer import LinkTree
from modules.color import color
from modules.link_io import LinkIO
from modules.link import LinkNode
from modules.updater import updateTor
from modules.savefile import saveJson
from modules.info import execute_all
from modules.collect_data import collect_data

# GLOBAL CONSTS
LOCALHOST = "127.0.0.1"
DEFPORT = 9050

# TorBot VERSION
__VERSION = "1.3.4"


def connect(address, port, no_socks):
    """ Establishes connection to port

    Assumes port is bound to localhost, if host that port is bound to changes
    then change the port.

    Args:
        address (str): Address for port to bind to.
        port (str): Establishes connect to this port.
    """
    if no_socks:
        return
    if address and port:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, address, port)
    elif address:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, address, DEFPORT)
    elif port:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, LOCALHOST, port)
    else:
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, LOCALHOST, DEFPORT)

    socket.socket = socks.socksocket  # Monkey Patch our socket to tor socket

    def getaddrinfo(*args):
        """
        Overloads socket function for std socket library.
        Check socket.getaddrinfo() documentation to understand parameters.
        Simple description below:
        argument - explanation (actual value)
        socket.AF_INET - the type of address the socket can speak to (IPV4)
        sock.SOCK_STREAM - creates a stream connecton rather than packets
        6 - protocol being used is TCP
        Last two arguments should be a tuple containing the address and port
        """
        return [(socket.AF_INET, socket.SOCK_STREAM, 6,
                 '', (args[0], args[1]))]
    socket.getaddrinfo = getaddrinfo


def header():
    """
    Prints out header ASCII art
    """
    license_msg = color("LICENSE: GNU Public License", "red")
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
    parser.add_argument("-u", "--url", help="Specifiy a website link to crawl")
    parser.add_argument("--ip", help="Change default ip of tor")
    parser.add_argument("-p", "--port", help="Change default port of tor")
    parser.add_argument("-s", "--save", action="store_true",
                        help="Save results in a file")
    parser.add_argument("-m", "--mail", action="store_true",
                        help="Get e-mail addresses from the crawled sites")
    parser.add_argument("-e", "--extension", action='append', dest='extension',
                        default=[],
                        help=' '.join(("Specifiy additional website",
                                       "extensions to the list(.com , .org, .etc)")))
    parser.add_argument("-i", "--info", action="store_true",
                        help=' '.join(("Info displays basic info of the",
                                       "scanned site")))
    parser.add_argument("--depth", help="Specifiy max depth of crawler (default 1)")
    parser.add_argument("-v", "--visualize", action="store_true",
                        help="Visualizes tree of data gathered.")
    parser.add_argument("-d", "--download", action="store_true",
                        help="Downloads tree of data gathered.")
    parser.add_argument("--gather",
                        action="store_true",
                        help="Gather data for analysis")
    parser.add_argument("--no-socks",
                        action="store_true",
                        help="Don't use local SOCKS. Useful when TorBot is"
                             " launched behind a Whonix Gateway")
    return parser.parse_args()


def main():
    """
    TorBot's Core
    """
    args = get_args()
    connect(args.ip, args.port, args.no_socks)
    
    if args.gather:
        collect_data()
        return
    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args.version:
        print("TorBot Version:" + __VERSION)
        exit()
    if args.update:
        updateTor()
        exit()
    if not args.quiet:
        header()
    # If url flag is set then check for accompanying flag set. Only one
    # additional flag can be set with -u/--url flag
    if args.url:
        try:
            node = LinkNode(args.url)
        except (ValueError, HTTPError, ConnectionError) as err:
            raise err
        LinkIO.display_ip()
        # -m/--mail
        if args.mail:
            print(node.emails)
            if args.save:
                saveJson('Emails', node.emails)
        # -i/--info
        if args.info:
            execute_all(node.uri)
            if args.save:
                print('Nothing to save.\n')
        if args.visualize:
            if args.depth:
                tree = LinkTree(node, stop_depth=args.depth)
            else:
                tree = LinkTree(node)
            tree.show()
        if args.download:
            tree = LinkTree(node)
            file_name = str(input("File Name (.pdf/.png/.svg): "))
            tree.save(file_name)
        else:
            LinkIO.display_children(node)
            if args.save:
                print(node.titles)
                #saveJson("Links", node.links)
    else:
        print("usage: See torBot.py -h for possible arguments.")

    print("\n\n")

def test(args):
 
    """
    TorBot's Core
    """
    #args = get_args()
    #connect("127.0.0.1",9050,False)
    connect(args['ip'], args['port'], args['no_socks'])
    print(type(args['ip']), type(args['port']), type(args['no_socks']))
    if args['gather']==True:
        collect_data()
        return
    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args['version']==True:
        print("TorBot Version:" + __VERSION)
        exit()
    if args['update']==True:
        updateTor()
        exit()
    if not args['quiet']==True:
        header()
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
        LinkIO.display_ip()
        print("display_ip()",LinkIO.display_ip())
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
        if args['visualize']==True:
            if "depth" in args:
                tree = LinkTree(node, stop_depth=args['depth'])
            else:
                tree = LinkTree(node)
            tree.show()
        if args['download']==True:
            tree = LinkTree(node)
            file_name = str(input("File Name (.pdf/.png/.svg): "))
            tree.save(file_name)
        else:
            LinkIO.display_children(node)
            if args['save']==True:
                saveJson("Links", node.links)
    else:
        print("usage: See torBot.py -h for possible arguments.")
    
    print("\n\n")
    return node.links

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
