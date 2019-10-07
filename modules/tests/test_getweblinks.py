"""
Test module for getting web links
"""
import pytest
import requests_mock

from yattag import Doc
from ..link import LinkNode


def setup_html(test_links, fail=False):
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
                if not fail:
                    line('a', 'test_anchor', href=data)

    return doc.getvalue()


@pytest.fixture
def links_fail():
    """
    Test links that have incorrect scheme
    """
    test_data = ['ssh://aff.ironsocket.onion',
                 'ftp://aff.ironsocket.onion',
                 'lol://wsrs.onion',
                 'dial://cmsgear.onion']

    mock_html = setup_html(test_data, fail=True)
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', data, text=mock_html)
        with pytest.raises(ValueError):
            node = LinkNode(data)
            return node.links, []

def test_get_links_fail(links_fail):
    if links_fail:
        links, test_data = links_fail
        assert links == test_data

@pytest.fixture
def links_tor():
    """
    Test links that return sucessfully
    """
    test_data = ['https://aff.ironsocket.onion',
                 'https://aff.ironsocket.onion',
                 'https://wsrs.onion',
                 'https://cmsgear.onion']

    mock_html = setup_html(test_data)
    mock_link = 'http://test.tor'
    with requests_mock.Mocker() as mock_connection:
        mock_connection.register_uri('GET', mock_link, text=mock_html)

        node = LinkNode(mock_link)
        return node.links, test_data

def test_get_links_tor(links_tor):
    links, test_data = links_tor
    assert links == test_data


@pytest.fixture
def links_tld():
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
    mock_url = 'http://test.tor'
    with requests_mock.Mocker() as mock_connection:
        for data in test_data:
            mock_connection.register_uri('GET', mock_url, text=mock_html)

        node = LinkNode(mock_url)
        links = node.links
        return links, test_data


def test_get_links_tld(links_tld):
    links, test_data = links_tld
    assert links == test_data
