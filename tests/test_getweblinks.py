#!/usr/bin/env python

import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from modules import getLinks, pagereader


def test_get_links_successful():
    link = 'http://www.whatsmyip.net'
    soup = pagereader.read_first_page(link)[0]
    data = ['http://aff.ironsocket.com/SH7L',
            'http://aff.ironsocket.com/SH7L',
            'http://wsrs.net/',
            'http://cmsgear.com/']

    LOCALHOST = '127.0.0.1'
    PORT = 9050
    result = getLinks.GetLinks(link, LOCALHOST, PORT, 15)
    
    assert result == data


if __name__ == '__main__':
	test_get_links_successful()
