from ..linktree import parse_hostname


def test_parse_hostname() -> None:
    https_test_url = 'https://www.example.com'
    assert parse_hostname(https_test_url) == 'www.example.com'

    http_test_url = 'https://www.test.com'
    assert parse_hostname(http_test_url) == 'www.test.com'
