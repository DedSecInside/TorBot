import sys
sys.path.append('../')

import modules.getweblinks as getweblinks
import pytest
import requests_mock

from bs4 import BeautifulSoup
from yattag import Doc


def setup_html(test_links):
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            for data in test_links:
                line('a', 'test_anchor', href=data)

    return doc.getvalue()


@pytest.fixture
def test_get_links_fail():
    test_data = ['ssh://aff.ironsocket.tor',
                 'ftp://aff.ironsocket.tor',
                 'lol://wsrs.tor',
                 'dial://cmsgear.tor']

    mock_html = setup_html(test_data)
    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', data, text='Received')

        result = getweblinks.get_links(mock_soup, ext=['.tor'])
        assert result == []


@pytest.fixture
def test_get_links_tor():
    test_data = ['https://aff.ironsocket.tor',
                 'https://aff.ironsocket.tor',
                 'https://wsrs.tor',
                 'https://cmsgear.tor']

    mock_html = setup_html(test_data)
    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', data, text='Received')

        result = getweblinks.get_links(mock_soup, ext=['.tor'])
        assert result == test_data


@pytest.fixture
def test_get_links_ext():
    test_data = ['https://aff.ironsocket.com/SH7L',
                 'https://aff.ironsocket.gov/SH7L',
                 'https://wsrs.net/',
                 'https://cmsgear.com/']

    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            for data in test_data:
                line('a', 'test_anchor', href=data)

    mock_html = doc.getvalue()

    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', data, text='Received')

        result = getweblinks.get_links(mock_soup, ext=['.com', '.gov', '.net'])
        assert result == test_data


def test_run():
    test_get_links_fail()
    test_get_links_tor()
    test_get_links_ext()


if __name__ == '__main__':
    test_run()
