"""
Test module for reading pages
"""
import pytest
import requests_mock

from yattag import Doc
from ..link_io import LinkIO


@pytest.fixture
def read_func():
    """
    Tests if read is returning the expected html
    """
    websites = []
    test_data = [
        ('https://www.test.com', 'This is a dot com site.'), ('https://www.test.org', 'This is a dot org site.'),
        ('https://www.test.net', 'This is a dot net site.'), ('https://www.test.onion', 'This is a dot onion site.')
    ]

    doc, tag, text = Doc().tagtext()

    for data in test_data:
        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('body'):
                text(data[1])

        websites.append(doc.getvalue())

    with requests_mock.Mocker() as mock_connection:
        for i in range(len(websites)):
            mock_connection.register_uri('GET', test_data[i][0], text=test_data[i][1])
            result = LinkIO.read(test_data[i][0])
            return result, test_data[i][1]


def test_read(read_func):
    result, test_data = read_func
    assert result == test_data
