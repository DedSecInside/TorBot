import sys
sys.path.append('../')

from modules import getemails
from bs4 import BeautifulSoup
from yattag import Doc


def test_get_emails_fail():
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
    test_get_emails()
    test_get_emails_fail()


if __name__ == '__main__':
    test_run()
