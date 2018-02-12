#!/usr/bin/env python

import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from modules import getweblinks, pagereader


def test_get_links_successful():
    soup = pagereader.readPage('http://www.whatsmyip.net/')
    data = ['http://aff.ironsocket.com/SH7L',
            'http://aff.ironsocket.com/SH7L',
            'http://wsrs.net/',
            'http://cmsgear.com/']

    result = getweblinks.getLinks(soup, ext=['.com', '.net'])
    assert result == data


if __name__ == '__main__':
	test_get_links_successful()