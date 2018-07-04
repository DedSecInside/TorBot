import sys
sys.path.append('../')

import pytest
import modules.getemails as getemails

from bs4 import BeautifulSoup
from yattag import Doc


def test_get_emails():
    test_emails = ['hello@helloaddress.com']
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            for email in test_emails:
                line('a', 'test_anchor', href=':'.join(('mailto', email)))

    mock_html = doc.getvalue()

    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    emails = getemails.getMails(mock_soup)
    assert emails == test_emails


def test_run():
    test_get_emails()


if __name__ == '__main__':
    test_run()
