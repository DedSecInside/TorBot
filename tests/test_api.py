import httpx
from yattag import Doc
from unittest.mock import patch, Mock

from torbot.modules.api import get_ip


def generate_mock_torproject_page(header: str, body: str) -> str:
    doc, tag, text = Doc().tagtext()
    with tag("html"):
        with tag("div", klass="content"):
            with tag("h1"):
                text(header)
            with tag("p"):
                text(body)

    return doc.getvalue()


@patch.object(httpx.Client, "get")
def test_get_ip(mock_get) -> None:
    # generate HTML
    mock_header = "TorProject Page"
    mock_body = "You are connected to tor. IP 127.0.0.1"
    mock_html_page = generate_mock_torproject_page(mock_header, mock_body)

    # define mock
    mock_response = Mock()
    mock_get.return_value = mock_response
    mock_response.text = mock_html_page

    # attempt test
    with httpx.Client() as client:
        resp = get_ip(client)
        assert resp["header"] == mock_header
        assert resp["body"] == mock_body
