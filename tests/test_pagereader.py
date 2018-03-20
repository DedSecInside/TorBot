import pytest
import requests
import requests_mock

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, ConnectionError


@pytest.fixture
def test_read_first_page(site, extension=False):

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
                if not extension:
                    response = requests.get(site, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    return str(page)
                if extension and attempts_left == 3:
                    response = requests.get('https://'+site, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    return str(page)
                if extension and attempts_left == 2:
                    response = requests.get('http://'+site, headers=headers)
                    page = BeautifulSoup(response.text, 'html.parser')
                    return str(page)
                if extension and attempts_left == 1:
                    raise err

            except (HTTPError, ConnectionError) as e:
                err = e
                attempts_left -= 1

        raise err


def test_single_extension():
    uris = {
        '.com': 'www.test.com',
        '.org': 'www.test.org',
        '.net': 'www.test.net',
        '.onion': 'www.test.onion',
        '.cannotbefound': 'www.test.cannotbefound'
            }

    with pytest.raises(HTTPError):
        for toplevel_domain, url in uris.items():
            page = test_read_first_page(url, toplevel_domain)
            if toplevel_domain == '.com':
                assert page == 'This is a dot com site.'
            elif toplevel_domain == '.org':
                assert page == 'This is a dot org site.'
            elif toplevel_domain == '.net':
                assert page == 'This is a dot net site.'
            elif toplevel_domain == '.onion':
                assert page == 'This is a dot onion site.'


if __name__ == '__main__':
    test_single_extension()
