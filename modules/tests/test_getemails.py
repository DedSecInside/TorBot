"""
Test module for getemails
"""
from bs4 import BeautifulSoup
from yattag import Doc
from .. import getemails


def test_get_emails_fail():
    """
    Test case for if website doesn't contain any email links
    """
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            line('a', 'test_anchor')

    mock_html = doc.getvalue()

    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    emails = getemails.get_mails(mock_soup)
    assert emails == []


def test_get_emails():
    """
    Test case for if website has multiple email links
    """
    test_emails = ['hello@helloaddress.com',
                   'test@testemail.com',
                   'foo@bar.com',
                   'lol@me.biz']
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            for email in test_emails:
                line('a', 'test_anchor', href=':'.join(('mailto', email)))

    mock_html = doc.getvalue()

    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    emails = getemails.get_mails(mock_soup)
    assert emails == test_emails


def test_run():
    """
    Execute test cases
    """
    test_get_emails()
    test_get_emails_fail()


if __name__ == '__main__':
    test_run()
