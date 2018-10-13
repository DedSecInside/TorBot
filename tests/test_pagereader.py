import sys
sys.path.append('../')
import pytest
import requests_mock

from modules.pagereader import read
from yattag import Doc


@pytest.fixture
def test_read_first_page():
    websites = []
    test_data = [
        ('https://www.test.com', 'This is a dot com site.'),
        ('https://www.test.org', 'This is a dot org site.'),
        ('https://www.test.net', 'This is a dot net site.'),
        ('https://www.test.onion', 'This is a dot onion site.')
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
            mock_connection.register_uri('GET',
                                         test_data[i][0],
                                         text=test_data[i][1])
            result = read(test_data[i][0])
            assert result == test_data[i][1]


def test_run():
    test_read_first_page()


if __name__ == '__main__':
    test_run()
