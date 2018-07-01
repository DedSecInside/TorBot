import sys
sys.path.append('../')

import modules.getweblinks as getweblinks
import pytest
import requests_mock

from bs4 import BeautifulSoup
from yattag import Doc


@pytest.fixture
def test_get_links():
    test_data = ['https://aff.ironsocket.com/SH7L',
                 'https://aff.ironsocket.com/SH7L',
                 'https://wsrs.net/',
                 'https://cmsgear.com/']

    doc, tag, text, line = Doc().ttl()
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

        result = getweblinks.get_links(mock_soup, ext=['.com', '.net'])
        assert result == test_data


def test_run():
    test_get_links()


if __name__ == '__main__':
    test_run()
