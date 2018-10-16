"""
Test module for getting web links
"""
import pytest
import requests_mock

from bs4 import BeautifulSoup
from yattag import Doc
from ..getweblinks import get_links


def setup_html(test_links):
    """
    Sets up test html containing links

    Args:
        test_links (list): list of links to be used for tests
    Return:
        test HTML value
    """
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            for data in test_links:
                line('a', 'test_anchor', href=data)

    return doc.getvalue()


@pytest.fixture
def test_get_links_fail():
    """
    Test links that have incorrect scheme
    """
    test_data = ['ssh://aff.ironsocket.tor',
                 'ftp://aff.ironsocket.tor',
                 'lol://wsrs.tor',
                 'dial://cmsgear.tor']

    mock_html = setup_html(test_data)
    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', data, text='Received')

        result = get_links('test', test_html=mock_soup)
        assert result == []


@pytest.fixture
def test_get_links_tor():
    """
    Test links that return sucessfully
    """
    test_data = ['https://aff.ironsocket.tor',
                 'https://aff.ironsocket.tor',
                 'https://wsrs.tor',
                 'https://cmsgear.tor']

    mock_html = setup_html(test_data)
    mock_soup = BeautifulSoup(mock_html, 'html.parser')
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', data, text='Received')

        result = get_links('test', test_html=mock_soup, ext=['.tor'])
        assert result == test_data


@pytest.fixture
def test_get_links_tld():
    """
    Test links with additional top-level-domains
    """
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

        result = get_links(data, test_html=mock_soup, ext=['.com', '.gov', '.net'])
        assert result == test_data


def test_run():
    """
    Executes tests
    """
    test_get_links_fail()
    test_get_links_tor()
    test_get_links_tld()


if __name__ == '__main__':
    test_run()
