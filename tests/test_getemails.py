import sys
import os
import unittest

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from modules import pagereader, getemails
from io import StringIO
from modules.bcolors import Bcolors


soup = pagereader.readPage('http://www.whatsmyip.net/')


class getMailsTestCase(unittest.TestCase):

        def setUp(self):
            self.held, sys.stdout = sys.stdout, StringIO()
            self.b_colors = Bcolors()

        def test_print_emails(self):
            data = ''.join(("\n", self.b_colors.OKGREEN, "Mails Found - ",
                            self.b_colors.ENDC, "1\n------------------------",
                            "-------\nadvertise@provaz.eu\n"))
            getemails.getMails(soup)
            self.assertEqual(sys.stdout.getvalue(), data)


if __name__ == '__main__':
    unittest.main()
