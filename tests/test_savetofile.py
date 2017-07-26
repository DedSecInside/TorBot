import sys
import os
import unittest
from io import StringIO
sys.path.append(os.path.abspath('../modules'))
import getweblinks
from bcolors import Bcolors
import pagereader
import time

soup = pagereader.readPage('http://www.whatsmyip.net/')
timestr = time.strftime("%Y%m%d-%H%M%S")

class getLinksTestCase(unittest.TestCase):
	
	def setUp(self):
		self.held, sys.stdout = sys.stdout, StringIO()
		self.maxDiff=None
	
	def test_save_links(self):
		data = "\n"+Bcolors.OKGREEN+"Websites Found - "+Bcolors.ENDC+"1\n-------------------------------\nhttp://cmsgear.com/\n\nData will be saved with a File Name :"+ "TorBoT-Export-Onion-Links"+timestr+".json\n"
		ext = ['.com/']
		getweblinks.getLinks(soup,ext,0,1)
		self.assertEqual(sys.stdout.getvalue(),data)


if __name__ == '__main__':
	unittest.main()

