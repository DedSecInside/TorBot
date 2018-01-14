import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from modules import pagereader, getemails


def test_get_emails_successful():
    soup = pagereader.readPage('http://www.whatsmyip.net/')
    test_emails = ["advertise@provaz.eu"]
    emails = getemails.getMails(soup)
    assert emails == test_emails


