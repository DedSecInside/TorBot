import urllib.request 
from bs4 import BeautifulSoup

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'
    On_Black = '\033[40m'
    On_Red = '\033[41m'
	

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
	print( "MMMMMMMMMMMMMMMMMMMMMMMXdxKk:',lONMMMM"+bcolors.FAIL + " D3DSEC "+bcolors.WHITE+"MMMMMMMM")
	print( "MMMMMMMMMMMMMMMMMMMMMMMMOo0NOdxc,kMMMM"+bcolors.FAIL + " INS1DE "+bcolors.WHITE+"MMMMMMMM")
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
	print(bcolors.FAIL)
	print( " 	       __  ____  ____  __        ______ ")
	print( "  	      / /_/ __ \/ __ \/ /_  ____/_  __/ ")
	print( " 	     / __/ / / / /_/ / __ \/ __ \/ / ")
	print( "	    / /_/ /_/ / _, _/ /_/ / /_/ / /  ")
	print( "	    \__/\____/_/ |_/_.___/\____/_/  V 0.1")
	print(bcolors.On_Black)
	print("#######################################################")
	print("#  TorBot - A python Tor Crawler                      #")
	print("#  GitHub : https://github.com/DedsecInside/TorBot    #")
	print("######################################################")
	print(bcolors.FAIL + "LICENSE: GNU Public License" + bcolors.ENDC)
	print()

def stemTest():
 from stem.control import Controller
 with Controller.from_port(port = 9051) as controller:
  controller.authenticate()
  bytes_read = controller.get_info("traffic/read")
  bytes_written = controller.get_info("traffic/written")
  print("My Tor relay has read %s bytes and written %s." % (bytes_read, bytes_written))


def readPage(page):
    response = urllib.request.urlopen(page)
    soup = BeautifulSoup(response.read(),'html.parser')
    print (soup.find_all('input'))
    return soup

###Get all emails from the website
def get_all_emails(soup):
    websites = []
    emails = []
    for link in soup.find_all('a'):
        email_link = link.get('href')
        if email_link != None:
            if 'http' in email_link:
                websites.append(email_link)
            elif 'mailto' in email_link:
                emails.append(email_link)
        else:
            pass
    return websites,emails
        

def main():
 header()
 stemTest()
 print ("Tor Ip Address :")
 a = readPage("http://www.whatsmyip.net/")
 print (get_all_emails(a))
 print ("\n\n")
 #readPage("http://od6j46sy5zg7aqze.onion")
 return 0

if __name__ == '__main__':
  main()
