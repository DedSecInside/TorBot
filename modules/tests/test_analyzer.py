import pytest
import requests_mock

from yattag import Doc
from ..analyzer import LinkTree
from ..link import LinkNode

def create_page(name):
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        line('title', name)
        with tag('body'):
            line('h1', 'Something') 
    return doc.getvalue()

def create_root_page_with_links(root, links):
    doc, tag, _, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        line('title', root)
        with tag('body'):
            for link in links:
                line('a', 'test', href=link)

    return doc.getvalue()

@pytest.fixture
def test_links_in_tree():
    links = ['http://dog.onion', 'http://cat.onion', 'http://foo.cnion']
    with requests_mock.Mocker() as mock_connection:
        root_page = create_root_page_with_links('http://root.onion', links)
        for link in links:
            page = create_page(link)
            mock_connection.register_uri('GET', link, text=page)
        mock_connection.register_uri('GET', 'http://root.onion', text=root_page)

        node = LinkNode('http://root.onion') 
        tree = LinkTree(node)
         
        for link in links:
            assert link in tree

def test_run():
    test_links_in_tree()

if __name__ == '__main__':
    test_run()
