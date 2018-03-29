import pytest
import requests
import requests_mock

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, MissingSchema, ConnectionError


@pytest.fixture
def test_read_first_page(site):

    with requests_mock.Mocker() as m:
        m.get('https://www.test.com', text='This is a dot com site.')
        m.get('https://www.test.org', text='This is a dot org site.')
        m.get('https://www.test.net', text='This is a dot net site.')
        m.get('https://www.test.onion', text='This is a dot onion site.')

        m.register_uri('GET', 'https://www.test.cannotbefound', exc=HTTPError)
        m.register_uri('GET', 'http://www.test.cannotbefound', exc=HTTPError)

        headers = {'User-Agent':
                   'TorBot - Onion crawler | www.github.com/DedSecInside/TorBot'}
        attempts_left = 3
        err = " "

        # Removed unnecessary code such as printing
        while attempts_left:
            try:
                if attempts_left == 3:
                    response = requests.get(site, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    return str(page)
                if attempts_left == 2:
                    response = requests.get('https://'+site, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    return str(page)
                if attempts_left == 1:
                    response = requests.get('http://'+site, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    return str(page)
                if not attempts_left:
                    raise err

            except (HTTPError, MissingSchema, ConnectionError) as e:
                err = e
                attempts_left -= 1

        raise err


def test_run():
    urls = ['www.test.com', 'www.test.org', 'www.test.net', 'www.test.onion',
            'www.test.cannotbefound']

    with pytest.raises(HTTPError):
        for url in urls:
            page = test_read_first_page(url)
            if url[-4:] == '.com':
                assert page == 'This is a dot com site.'
            elif url[-4:] == '.org':
                assert page == 'This is a dot org site.'
            elif url[-4:] == '.net':
                assert page == 'This is a dot net site.'
            elif url[-6:] == '.onion':
                assert page == 'This is a dot onion site.'


if __name__ == '__main__':
    test_run()
