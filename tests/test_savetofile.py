import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from modules import getweblinks, pagereader


def test_save_links_successful():
    soup = pagereader.readPage('http://www.whatsmyip.net/')
    data = ['http://aff.ironsocket.com/SH7L',
            'http://aff.ironsocket.com/SH7L',
            'http://wsrs.net/',
            'http://cmsgear.com/']
    result = getweblinks.getLinks(soup)
    assert result == data
