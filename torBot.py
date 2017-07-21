#from modules.getemails import getMails
#from modules.getweblinks import getLinks
#from modules.pagereader import readPage
#from modules.bcolors import bcolors
#from modules.updater import updateTor

from modules import *

import socket
import socks
import argparse

from stem import Signal
from stem.control import Controller

with Controller.from_port(port = 9051) as controller:
    controller.authenticate("16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C")
    controller.signal(Signal.NEWNYM)
#TorBot VERSION    
_VERSION_ = "1.0.1"
#TOR SETUP GLOBAL Vars
SOCKS_PORT = 9050  # TOR proxy port that is default from torrc, change to whatever torrc is configured to
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1",SOCKS_PORT)
socket.socket = socks.socksocket
# Perform DNS resolution through the socket
def getaddrinfo(*args):
  return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
  
socket.getaddrinfo = getaddrinfo

def header():
	""" Display the header of TorBot """
	print("#######################################################")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNXNWWWWWMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWX0KXXKKXWMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNNKOkOOkOXWMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMMNX0kdodoxKWMMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMW0doccloONMWWMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMMMMKl;;:cxKWMMMMMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMWKOXNx;,,cONMMMMMMMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMXdxKk:',lONMMMM"+Bcolors.FAIL + " D3DSEC "+Bcolors.WHITE+"MMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMOo0NOdxc,kMMMM"+Bcolors.FAIL + " INS1DE "+Bcolors.WHITE+"MMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMOcONOxkx;dWMMMMMMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMNkcdXXOkxkd:oXMMMMMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMNOoclONNX00OkOxc:lkXWMMMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMN0olld0NWNNX0O00kxkxl:;ckXMWWMMMMMMMMM")
	print( "MMMMMMMMMMMWMMNxccd0NNNNNXNXOkOK0dodxdo:,;o0WMMMMMMMMM")
	print( "MMMMMMMMMMMMNk:ckXNNWNXXXXNXOOOOK0oloooooc,'oKMMMMMMMM")
	print( "MMMMMMMMMMMXc;xXNNNXKXXXNNWKOO0Ok0x:clllllc:.,OWMMMMMM")
	print( "MMMMMMMMMMX:;0WNNX00XNNNNNNKOO0KkkOc,ccccccc:.'OWMMMMM")
	print( "MMMMMMMMMNl,ONNN0OXNNNNNXXNKOkOK0xkl':c::::::;.;KMMMMM")
	print( "MMMMMMMMM0,lNWXO0NNNNXKKXXNXO0Ok0Oxl',:;;;;;;;..dMMMMM")
	print( "MMMMMMMMMk,xWNOONNNX00XNNNWKOO0OkOxc'';;,,,,,,'.cMMMMM")
	print( "MMMMMMMMMx,xWKkKWNXOKNWNNNX0xxOKxxx:..,,,,,''''.cMMMMM")
	print( "MMMMMMMMM0,oWXkOWXOKNNNNN00Xkdx0kdd;..,'''''''..oMMMMM")
	print( "MMMMMMMMMNl;0W0kKKkKWNNN0ONNOxdOOll,..'''......,0MMMMM")
	print( "MMMMMMMMMMK::KN0kKOkNNWXk0WX0kdxkc:............xWMMMMM")
	print( "MMMMMMMMMMMKl:kX0k0kONWNOONX0koxd:,..........'kWMMMMMM")
	print( "MMMMMMMMMMMMNxccxOkkxkKWKx0NOoooc'..........lKWMMMMMMM")
	print( "MMMMMMMMMMMMMWNklccclldk0OxOdcc;. .......;oKWWMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMWXOdl:::;cc;'... ..',:lx0NMMMMMMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMNKOkxddolloodk0XWMMMMMMMMMMMMMMMM")
	print(Bcolors.FAIL+Bcolors.BOLD)
	print( " 	       __  ____  ____  __        ______ ")
	print( "  	      / /_/ __ \/ __ \/ /_  ____/_  __/ ")
	print( " 	     / __/ / / / /_/ / __ \/ __ \/ / ")
	print( "	    / /_/ /_/ / _, _/ /_/ / /_/ / /  ")
	print( "	    \__/\____/_/ |_/_.___/\____/_/  V"+_VERSION_)
	print(Bcolors.FAIL+Bcolors.On_Black)
	print("#######################################################")
	print("#  TorBot - A python Tor Crawler                      #")
	print("#  GitHub : https://github.com/DedsecInside/TorBot    #")
	print("#######################################################")
	print(Bcolors.FAIL + "LICENSE: GNU Public License" + Bcolors.ENDC)
	print()
   

def main():
 parser = argparse.ArgumentParser()
 parser.add_argument("-v","--version",action="store_true",help="Show current version of TorBot.")
 parser.add_argument("--update",action="store_true",help="Update TorBot to the latest stable version")
 parser.add_argument("-q","--quiet",action="store_true")
 parser.add_argument("-u","--url",help="Specifiy a website link to crawl")
 parser.add_argument("-m","--mail",action="store_true", help="Get e-mail addresses from the crawled sites")
 parser.add_argument("-e","--extension",action='append',dest='extension',default=[],help="Specifiy additional website extensions to the list(.com or .org etc)")
 parser.add_argument("-l","--live",action="store_true",help="Check if websites are live or not (slow)")
 args = parser.parse_args()	
 if args.version :
 	print("TorBot Version:"+_VERSION_)
 	exit()
 if args.update:
 	updateTor()
 	exit()

 if args.quiet == 0:
 	header()
 print ("Tor Ip Address :")
 link = args.url
 ext = 0
 live = 0
 live = args.live
 ext = args.extension
 a = readPage("https://check.torproject.org/",1)
 if link:
 	b = readPage(link)
 else:
    b = readPage("http://torlinkbgs6aabns.onion/")
 if args.mail:
 	getMails(b)
 getLinks(b,ext,live)
 print ("\n\n")
 return 0

if __name__ == '__main__':

 try:	
  main()
 except KeyboardInterrupt:
  print("Interrupt received! Exiting cleanly...")
