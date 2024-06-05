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
    # Generate mock HTML page
    mock_html_page = generate_mock_torproject_page(
        header="TorProject Page",
        body="You are connected to tor. IP 127.0.0.1"
    )

    # Define mock response
    mock_response = Mock()
    mock_response.text = mock_html_page
    mock_get.return_value = mock_response

   #added the perform test block for effiecient catch
    # Perform test 
    with httpx.Client() as client:
        resp = get_ip(client)
        assert resp["header"] == "TorProject Page"
        assert resp["body"] == "You are connected to tor. IP 127.0.0.1"
