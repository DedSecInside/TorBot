import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from modules import pagereader, getemails


def test_get_emails_successful():
    soup = pagereader.read_first_page('https://www.helloaddress.com/')
    test_emails = ["hello@helloaddress.com"]
    emails = getemails.getMails(soup)
    assert emails == test_emails

if __name__ == '__main__':
    test_get_emails_successful()