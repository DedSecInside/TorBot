import sys
import os
import unittest

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from modules import pagereader, getemails
from modules.bcolors import Bcolors


soup = pagereader.readPage('http://www.whatsmyip.net/')


class getMailsTestCase(unittest.TestCase):

        def setUp(self):
            self.b_colors = Bcolors()

        def test_getemails(self):
            test_emails = ["advertise@provaz.eu"]
            emails = getemails.getMails(soup)
            self.assertEqual(emails, test_emails)


if __name__ == '__main__':
    unittest.main()
