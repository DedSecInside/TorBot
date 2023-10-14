from yattag import Doc

from ..linktree import parse_hostname, parse_links


def test_parse_hostname() -> None:
    https_test_url = 'https://www.example.com'
    assert parse_hostname(https_test_url) == 'www.example.com'

    http_test_url = 'https://www.test.com'
    assert parse_hostname(http_test_url) == 'www.test.com'


def test_parse_links() -> None:
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('a', href='https://example.com'):
            pass
        with tag('a', href='http://test.com'):
            pass
        with tag('a', href='https://example-test.com'):
            pass
        with tag('a', href='invalid link'):
            pass

    links = parse_links(doc.getvalue())
    assert len(links) == 3
    assert links == ['https://example.com', 'http://test.com', 'https://example-test.com']
