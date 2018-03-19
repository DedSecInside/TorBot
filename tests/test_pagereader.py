import pytest
import requests
import requests_mock

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

@pytest.fixture
def test_read_first_page(site, extension=False):

    with requests_mock.Mocker() as m: 
        # Creating mock https requests
        m.get('https://test_dotcom.com', text='This is a dot com site.')
        m.get('https://test_dotonion.onion', text='This is a dot onion site.')
        m.get('https://test_dotorg.org', text='This is a dot org site.')
        m.get('https://test_dotnet.net', text='This is a dot net site.')
        m.register_uri('GET', 'https://test_cannotbefound.cannotbefound', exc=HTTPError)

        headers = {'User-Agent':
                   'TorBot - Onion crawler | www.github.com/DedSecInside/TorBot'}
        err = " "

        # Removed all unneccssary functionality for testing such as printing
        try:
                response = requests.get('https://'+site, headers=headers)
                page = BeautifulSoup(response.text, 'html.parser')
                return page
        except HTTPError as e:
            raise e


def test_single_extension():

    urls = {
            "test_dotcom.com":".com", 
            "test_dotonion.onion":".onion",
            "test_dotorg.org":".org",
            "test_dotnet.net":".net",
            "test_cannotbefound.cannotbefound":".cannotbefound"
            }
   
    # Using context manager to catch error that will be raised
    with pytest.raises(HTTPError):
        for secondlevel_domain, toplevel_domain in urls.items():
            page = test_read_first_page(secondlevel_domain, toplevel_domain)
            if toplevel_domain == ".com":
                assert str(page) == "This is a dot com site."
            elif toplevel_domain == ".onion":
                assert str(page) == "This is a dot onion site." 
            elif toplevel_domain == ".org":
                assert str(page) =="This is a dot org site."
            elif toplevel_domain == ".net":
                assert str(page) == "This is a dot net site."

if __name__ == 'main':
    test_single_extension()
