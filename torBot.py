import argparse
import socket
import socks
from modules import (bcolors, getemails, pagereader, getweblinks, updater,
                     info, go_linker, savefile)

# GLOBAL CONSTS
LOCALHOST = "127.0.0.1"
DEFPORT = 9050

# TorBot VERSION
__VERSION = "1.2"


def connect(address, port):
    """ Establishes connection to port

    Assumes port is bound to localhost, if host that port is bound to changes
    then change the port

    Args:
        address: address for port to bound to
        port: Establishes connect to this port
    """

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
        Overloads socket function for std socket library
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

    b_color = bcolors.Bcolors()
    D3DSEC = b_color.FAIL + " D3DSEC " + b_color.WHITE
    INS1DE = b_color.FAIL + " INS1DE " + b_color.WHITE

    text_header = r"""
                           __  ____  ____  __        ______
                          / /_/ __ \/ __ \/ /_  ____/_  __/
                         / __/ / / / /_/ / __ \/ __ \/ /
                        / /_/ /_/ / _, _/ /_/ / /_/ / /
                        \__/\____/_/ |_/_____/\____/_/  V{VERSION}
                {FAIL} + {On_Black}
                #######################################################
                #  TorBot - A python Tor Crawler                      #
                #  GitHub : https://github.com/DedsecInside/TorBot    #
                #  Help : use -h for help text                        #
                #######################################################
                      {FAIL} + "LICENSE: GNU Public License" + {END}""".format(
                D3DSEC=D3DSEC, INS1DE=INS1DE, FAIL=b_color.FAIL,
                BOLD=b_color.BOLD, VERSION=__VERSION, END=b_color.ENDC,
                On_Black=b_color.On_Black, WHITE=b_color.WHITE
                )
    print(text_header)

    
def main():
    args = get_args()
    connect(args.ip, args.port)
    link = args.url

    # If flag is -v, --update, -q/--quiet then user only runs that operation
    # because these are single flags only
    if args.version:
        print("TorBot Version:" + __VERSION)
        exit()
    if args.update:
        updater.updateTor()
        exit()
    if not args.quiet:
        header()
    # If url flag is set then check for accompanying flag set. Only one
    # additional flag can be set with -u/--url flag
    if args.url:
        print("Tor IP Address :", pagereader.get_ip())
        html_content, response = pagereader.read_first_page(link)
        print("Connection successful.")
        # -m/--mail
        if args.mail:
            emails = getemails.getMails(html_content)
            print(emails)
            if args.save:
                savefile.saveJson('Emails', emails)
        # -i/--info
        elif args.info:
            info.executeAll(link, html_content, response)
            if args.save:
                print('Nothing to save.\n')
        else:
            # Golang library isn't being used.
            #links = go_linker.GetLinks(link, LOCALHOST, PORT, 15)
            links = getweblinks.get_links(soup=html_content, ext=args.extension, live=args.live)
            if args.save:
                savefile.saveJson("Links", links)
    else:
        print("usage: torBot.py [-h] [-v] [--update] [-q] [-u URL] [-s] [-m]",
              "[-e EXTENSION] [-l] [-i]")

    print("\n\n")

    
if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
