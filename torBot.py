import argparse
import socket
import socks

from modules import bcolors, getemails, pagereader, getweblinks, updater, info
from stem import Signal
from stem.control import Controller


HSH_PWORD = "16:010CAA866566D3366070D2FA37DAD785D394B5263E90BB4C25135A2023"
with Controller.from_port(port=9051) as controller:
    controller.authenticate(HSH_PWORD)
    controller.signal(Signal.NEWNYM)

# TorBot VERSION
__VERSION = "1.1.0_dev"

# TOR SETUP GLOBAL Vars
SOCKS_PORT = 9050  # Default tor proxy port for socks, check torrc
socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT)
socket.socket = socks.socksocket


# Perform DNS resolution through the socket
def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]


socket.getaddrinfo = getaddrinfo


def header():
    b_color = bcolors.Bcolors()
    D3DSEC = b_color.FAIL + " D3DSEC " + b_color.WHITE + "MMMMMMMM"
    INS1DE = b_color.FAIL + " INS1DE " + b_color.WHITE + "MMMMMMMM"

    """ Display the header of TorBot """
    print("######################################################")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXNWWWWWMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWX0KXXKKXWMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNNKOkOOkOXWMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMNX0kdodoxKWMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMW0doccloONMWWMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMKl;;:cxKWMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMWKOXNx;,,cONMMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMMXdxKk:',lONMMMM" + D3DSEC)
    print("MMMMMMMMMMMMMMMMMMMMMMMMOo0NOdxc,kMMMM" + INS1DE)
    print("MMMMMMMMMMMMMMMMMMMMMMMMOcONOxkx;dWMMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMMNkcdXXOkxkd:oXMMMMMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMNOoclONNX00OkOxc:lkXWMMMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMN0olld0NWNNX0O00kxkxl:;ckXMWWMMMMMMMMM")
    print("MMMMMMMMMMMWMMNxccd0NNNNNXNXOkOK0dodxdo:,;o0WMMMMMMMMM")
    print("MMMMMMMMMMMMNk:ckXNNWNXXXXNXOOOOK0oloooooc,'oKMMMMMMMM")
    print("MMMMMMMMMMMXc;xXNNNXKXXXNNWKOO0Ok0x:clllllc:.,OWMMMMMM")
    print("MMMMMMMMMMX:;0WNNX00XNNNNNNKOO0KkkOc,ccccccc:.'OWMMMMM")
    print("MMMMMMMMMNl,ONNN0OXNNNNNXXNKOkOK0xkl':c::::::;.;KMMMMM")
    print("MMMMMMMMM0,lNWXO0NNNNXKKXXNXO0Ok0Oxl',:;;;;;;;..dMMMMM")
    print("MMMMMMMMMk,xWNOONNNX00XNNNWKOO0OkOxc'';;,,,,,,'.cMMMMM")
    print("MMMMMMMMMx,xWKkKWNXOKNWNNNX0xxOKxxx:..,,,,,''''.cMMMMM")
    print("MMMMMMMMM0,oWXkOWXOKNNNNN00Xkdx0kdd;..,'''''''..oMMMMM")
    print("MMMMMMMMMNl;0W0kKKkKWNNN0ONNOxdOOll,..'''......,0MMMMM")
    print("MMMMMMMMMMK::KN0kKOkNNWXk0WX0kdxkc:............xWMMMMM")
    print("MMMMMMMMMMMKl:kX0k0kONWNOONX0koxd:,..........'kWMMMMMM")
    print("MMMMMMMMMMMMNxccxOkkxkKWKx0NOoooc'..........lKWMMMMMMM")
    print("MMMMMMMMMMMMMWNklccclldk0OxOdcc;. .......;oKWWMMMMMMMM")
    print("MMMMMMMMMMMMMMMMWXOdl:::;cc;'... ..',:lx0NMMMMMMMMMMMM")
    print("MMMMMMMMMMMMMMMMMMMMMNKOkxddolloodk0XWMMMMMMMMMMMMMMMM")
    print(b_color.FAIL + b_color.BOLD)
    print(" 	       __  ____  ____  __        ______ ")
    print("  	      / /_/ __ \/ __ \/ /_  ____/_  __/ ")
    print(" 	     / __/ / / / /_/ / __ \/ __ \/ / ")
    print("	    / /_/ /_/ / _, _/ /_/ / /_/ / /  ")
    print("	    \__/\____/_/ |_/_.___/\____/_/  V" + __VERSION)
    print(b_color.FAIL + b_color.On_Black)
    print("#######################################################")
    print("#  TorBot - A python Tor Crawler                      #")
    print("#  GitHub : https://github.com/DedsecInside/TorBot    #")
    print("#  Help : use -h for help text                        #")
    print("#######################################################")
    print(b_color.FAIL + "LICENSE: GNU Public License" + b_color.ENDC)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version",
                        action="store_true",
                        help="Show current version of TorBot.")
    parser.add_argument("--update",
                        action="store_true",
                        help="Update TorBot to the latest stable version")
    parser.add_argument("-q", "--quiet",
                        action="store_true")
    parser.add_argument("-u", "--url",
                        help="Specifiy a website link to crawl")
    parser.add_argument("-s", "--save",
                        action="store_true",
                        help="Save results in a file")
    parser.add_argument("-m", "--mail",
                        action="store_true",
                        help="Get e-mail addresses from the crawled sites")
    parser.add_argument("-e", "--extension",
                        action='append',
                        dest='extension',
                        default=[],
                        help=' '.join(("Specifiy additional website extensions",
                                       "to the list(.com or .org etc)")))
    parser.add_argument("-l", "--live",
                        action="store_true",
                        help="Check if websites are live or not (slow)")
    parser.add_argument("-i", "--info",
                        action="store_true",
                        help=' '.join(("Info displays basic info of the",
                                       "scanned site, (very slow)")))

    args = parser.parse_args()

    if args.version:
        print("TorBot Version:" + __VERSION)
        exit()

    if args.update:
        updater.updateTor()
        exit()

    if args.quiet == 0:
        header()

    print("Tor Ip Address :")
    link = args.url
    defaultLink = "http://torlinkbgs6aabns.onion/"

    live = args.live
    ext = args.extension
    save = args.save

    pagereader.readPage("https://check.torproject.org/", 1)

    if link:
        b = pagereader.readPage(link)
    else:
        b = pagereader.readPage(defaultLink, 0)
        link = defaultLink

    if args.mail and b is not None:
        getemails.getMails(b, save)

    if args.info:
        info.executeAll(link)

    if b is not None:
        links = getweblinks.getLinks(b, ext, live, save)
        print(links)

    print("\n\n")

    return 0


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
