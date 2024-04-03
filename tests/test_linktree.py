from bs4 import BeautifulSoup
from yattag import Doc

from torbot.modules.linktree import parse_hostname, parse_links, parse_emails, parse_phone_numbers


def test_parse_hostname() -> None:
    https_test_url = "https://www.example.com"
    assert parse_hostname(https_test_url) == "www.example.com"

    http_test_url = "https://www.test.com"
    assert parse_hostname(http_test_url) == "www.test.com"


def test_parse_links() -> None:
    doc, tag, text = Doc().tagtext()
    with tag("html"):
        with tag("a", href="https://example.com"):
            pass
        with tag("a", href="http://test.com"):
            pass
        with tag("a", href="https://example-test.com"):
            pass
        with tag("a", href="invalid link"):
            pass

    links = parse_links(doc.getvalue())
    assert len(links) == 3
    assert links == [
        "https://example.com",
        "http://test.com",
        "https://example-test.com",
    ]


def test_parse_emails() -> None:
    doc, tag, text = Doc().tagtext()
    with tag("html"):
        with tag("a", href="mailto:example@yahoo.com"):
            pass
        with tag("a", href="mailto:example@outlook.com"):
            pass
        with tag("a", href="mailto:example@gmail.com"):
            pass
        with tag("a", href="mailto:invalid_email"):
            pass
        with tag("a", href="random-href"):
            pass

    soup = BeautifulSoup(doc.getvalue(), "html.parser")
    emails = parse_emails(soup)
    assert len(emails) == 3
    assert sorted(emails) == sorted(
        ["example@yahoo.com", "example@outlook.com", "example@gmail.com"]
    )


def test_parse_phone_numbers() -> None:
    doc, tag, text = Doc().tagtext()
    with tag("html"):
        with tag("a", href="tel:+18082453499"):
            pass
        with tag("a", href="tel:+15722027503"):
            pass
        with tag("a", href="tel:+18334966190"):
            pass
        with tag("a", href="tel:invalid_phone"):
            pass
        with tag("a", href="random-href"):
            pass

    soup = BeautifulSoup(doc.getvalue(), "html.parser")
    phone_numbers = parse_phone_numbers(soup)
    assert len(phone_numbers) == 3
    assert sorted(phone_numbers) == sorted(
        ["+18082453499", "+15722027503", "+18334966190"]
    )
