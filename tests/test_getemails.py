import sys
import os
import unittest
from io import StringIO
sys.path.append(os.path.abspath('../modules'))
import getemails
from bcolors import bcolors
import pagereader

soup = pagereader.readPage('http://www.whatsmyip.net/')

class getMailsTestCase(unittest.TestCase):
	
	def setUp(self):
		self.held, sys.stdout = sys.stdout, StringIO()
	
	def test_print_emails(self):
		data = "\n"+bcolors.OKGREEN+"Mails Found - "+bcolors.ENDC+"1\n-------------------------------\nadvertise@provaz.eu\n"
		getemails.getMails(soup)
		self.assertEqual(sys.stdout.getvalue(),data)
		

if __name__ == '__main__':
	unittest.main()
