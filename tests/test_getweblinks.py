import sys
import os
import unittest
from io import StringIO
sys.path.append(os.path.abspath('../modules'))
import getweblinks
from bcolors import Bcolors
import pagereader

soup = pagereader.readPage('http://www.whatsmyip.net/')

class getLinksTestCase(unittest.TestCase):
	
	def setUp(self):
		self.held, sys.stdout = sys.stdout, StringIO()
		self.maxDiff=None
	
	def test_print_links(self):
		#data = "\nWebsites Found - 7\n-------------------------------\nhttp://ads.wsrs.net/www/delivery/ck.php?n=MyIP856a6b4\nhttp://ads.wsrs.net/www/delivery/ck.php?n=MyIPbf5d683\nhttp://aff.ironsocket.com/SH7L\nhttp://aff.ironsocket.com/SH7L\nhttp://ads.wsrs.net/www/delivery/ck.php?n=MyIPdb5f512\nhttp://wsrs.net/\nhttp://cmsgear.com/\n"
		data = "\n"+Bcolors.OKGREEN+"Websites Found - "+Bcolors.ENDC+"1\n-------------------------------\nhttp://cmsgear.com/\n"
		ext = ['.com/']
		getweblinks.getLinks(soup,ext)
		self.assertEqual(sys.stdout.getvalue(),data)


if __name__ == '__main__':
	unittest.main()
