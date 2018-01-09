#!/usr/bin/env python

import unittest
import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from io import StringIO
from modules.bcolors import Bcolors
from modules import getweblinks, pagereader

soup = pagereader.readPage('http://www.whatsmyip.net/')


class getLinksTestCase(unittest.TestCase):

        def setUp(self):
            self.b_colors = Bcolors()
            self.held, sys.stdout = sys.stdout, StringIO()
            self.maxDiff = None

        def test_print_links(self):

            data = ['http://aff.ironsocket.com/SH7L',
                               'http://aff.ironsocket.com/SH7L',
                               'http://wsrs.net/',
                               'http://cmsgear.com/',
                               'http://cmsgear.com/']

            ext = ['.com/']
            result = getweblinks.getLinks(soup, ext)
            self.assertEqual(result, data)


if __name__ == '__main__':
    unittest.main()
