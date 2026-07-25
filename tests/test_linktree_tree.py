"""Comprehensive tests for LinkTree and LinkNode classes.

These tests verify:
- Creating nodes from HTTP responses (with/without title)
- Building trees with depth limits
- Duplicate node handling
- Saving to JSON and text formats
- Classification and contact extraction integration
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from torbot.modules.linktree import LinkTree, LinkNode, parse_hostname


class FakeResponse:
    """Mock HTTP response for testing."""

    def __init__(self, url: str, text: str, status_code: int = 200):
        self.url = url
        self.text = text
        self.status_code = status_code


class FakeClient:
    """Mock httpx.Client that returns pre-configured responses."""

    def __init__(self, responses: dict[str, FakeResponse]):
        self.responses = responses
        self.call_count = {}

    def get(self, url: str) -> FakeResponse:
        self.call_count[url] = self.call_count.get(url, 0) + 1
        if url in self.responses:
            return self.responses[url]
        # Return a minimal response for unknown URLs
        return FakeResponse(url, "<html><title>404</title></html>", 404)


def test_parse_hostname_extracts_domain():
    """Verify parse_hostname extracts hostname from various URL formats."""
    assert parse_hostname("https://example.com/path") == "example.com"
    assert parse_hostname("http://sub.domain.com:8080/") == "sub.domain.com"
    assert parse_hostname("https://test.onion") == "test.onion"


def test_parse_hostname_raises_on_invalid():
    """Ensure parse_hostname raises when URL has no hostname."""
    with pytest.raises(Exception, match="unable to parse hostname"):
        parse_hostname("not-a-url")

    with pytest.raises(Exception, match="unable to parse hostname"):
        parse_hostname("file:///local/path")


def test_linknode_initialization():
    """Verify LinkNode stores all required fields correctly."""
    node = LinkNode(
        title="Test Page",
        url="https://example.com",
        status=200,
        classification="blog",
        accuracy=0.85,
        numbers=["+14155551234"],
        emails=["test@example.com"],
    )

    assert node.tag == "Test Page"
    assert node.identifier == "https://example.com"
    assert node.status == 200
    assert node.classification == "blog"
    assert node.accuracy == 0.85
    assert node.numbers == ["+14155551234"]
    assert node.emails == ["test@example.com"]


def test_linktree_creates_root_node_with_title():
    """Test that LinkTree creates a root node using the page title."""
    html = """
    <html>
        <head><title>Example Site</title></head>
        <body>
            <a href="https://example.com/page1">Page 1</a>
        </body>
    </html>
    """

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", html, 200),
    })

    tree = LinkTree("https://example.com", depth=0, client=client)
    tree.load()

    root = tree.get_node("https://example.com")
    assert root is not None
    assert root.tag == "Example Site"
    assert root.data.status == 200


def test_linktree_creates_root_node_without_title():
    """Test that LinkTree falls back to hostname when no <title> tag."""
    html = "<html><body><p>No title here</p></body></html>"

    client = FakeClient({
        "https://test.onion": FakeResponse("https://test.onion", html, 200),
    })

    tree = LinkTree("https://test.onion", depth=0, client=client)
    tree.load()

    root = tree.get_node("https://test.onion")
    assert root is not None
    assert root.tag == "test.onion"


def test_linktree_extracts_contacts_from_page():
    """Verify LinkTree extracts emails and phone numbers from page."""
    html = """
    <html>
        <head><title>Contact Page</title></head>
        <body>
            <a href="mailto:info@example.com">Email us</a>
            <a href="tel:+14155551234">Call us</a>
            <a href="mailto:support@example.com">Support</a>
        </body>
    </html>
    """

    client = FakeClient({
        "https://example.com/contact": FakeResponse(
            "https://example.com/contact", html, 200
        ),
    })

    tree = LinkTree("https://example.com/contact", depth=0, client=client)
    tree.load()

    root = tree.get_node("https://example.com/contact")
    assert root is not None
    assert len(root.data.emails) == 2
    assert "info@example.com" in root.data.emails
    assert "support@example.com" in root.data.emails
    assert "+14155551234" in root.data.numbers


def test_linktree_builds_tree_to_depth_1():
    """Test that LinkTree builds children up to specified depth."""
    root_html = """
    <html>
        <head><title>Root</title></head>
        <body>
            <a href="https://example.com/child1">Child 1</a>
            <a href="https://example.com/child2">Child 2</a>
        </body>
    </html>
    """

    child1_html = "<html><head><title>Child 1</title></head></html>"
    child2_html = "<html><head><title>Child 2</title></head></html>"

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", root_html, 200),
        "https://example.com/child1": FakeResponse(
            "https://example.com/child1", child1_html, 200
        ),
        "https://example.com/child2": FakeResponse(
            "https://example.com/child2", child2_html, 200
        ),
    })

    tree = LinkTree("https://example.com", depth=1, client=client)
    tree.load()

    # Verify root exists
    root = tree.get_node("https://example.com")
    assert root is not None

    # Verify children exist
    child1 = tree.get_node("https://example.com/child1")
    child2 = tree.get_node("https://example.com/child2")
    assert child1 is not None
    assert child2 is not None
    assert child1.tag == "Child 1"
    assert child2.tag == "Child 2"

    # Verify tree structure
    assert tree.parent("https://example.com/child1").identifier == "https://example.com"
    assert tree.parent("https://example.com/child2").identifier == "https://example.com"


def test_linktree_respects_depth_limit():
    """Ensure LinkTree stops recursion at the specified depth."""
    root_html = '<html><title>Root</title><a href="https://example.com/level1">L1</a></html>'
    level1_html = '<html><title>Level 1</title><a href="https://example.com/level2">L2</a></html>'
    level2_html = '<html><title>Level 2</title><a href="https://example.com/level3">L3</a></html>'

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", root_html, 200),
        "https://example.com/level1": FakeResponse(
            "https://example.com/level1", level1_html, 200
        ),
        "https://example.com/level2": FakeResponse(
            "https://example.com/level2", level2_html, 200
        ),
        "https://example.com/level3": FakeResponse(
            "https://example.com/level3", '<html><title>Level 3</title></html>', 200
        ),
    })

    # Build tree with depth=2 (root + 2 levels)
    tree = LinkTree("https://example.com", depth=2, client=client)
    tree.load()

    # Root and level1 and level2 should exist
    assert tree.get_node("https://example.com") is not None
    assert tree.get_node("https://example.com/level1") is not None
    assert tree.get_node("https://example.com/level2") is not None

    # Level3 should NOT exist (depth limit)
    assert tree.get_node("https://example.com/level3") is None


def test_linktree_handles_duplicate_links():
    """Verify duplicate URLs don't cause errors or duplicate nodes."""
    html_with_dup = """
    <html>
        <title>Page with duplicates</title>
        <a href="https://example.com/page">Link 1</a>
        <a href="https://example.com/page">Link 2 (same URL)</a>
        <a href="https://example.com/other">Other</a>
    </html>
    """

    page_html = "<html><title>Target Page</title></html>"
    other_html = "<html><title>Other Page</title></html>"

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", html_with_dup, 200),
        "https://example.com/page": FakeResponse(
            "https://example.com/page", page_html, 200
        ),
        "https://example.com/other": FakeResponse(
            "https://example.com/other", other_html, 200
        ),
    })

    tree = LinkTree("https://example.com", depth=1, client=client)
    tree.load()

    # Should have 3 nodes total: root + 2 unique children
    all_nodes = tree.all_nodes()
    assert len(all_nodes) == 3

    # Duplicate should have been attempted once (first add), then skipped
    assert tree.get_node("https://example.com/page") is not None
    assert tree.get_node("https://example.com/other") is not None


def test_linktree_save_json_creates_file():
    """Test saveJSON writes a valid JSON file with tree structure."""
    html = '<html><title>Test JSON Save</title></html>'

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", html, 200),
    })

    tree = LinkTree("https://example.com", depth=0, client=client)
    tree.load()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch project_root_directory to use temp dir
        with patch("torbot.modules.linktree.project_root_directory", tmpdir):
            tree.saveJSON()

            # Check that JSON file was created
            json_files = list(Path(tmpdir).glob("*.json"))
            assert len(json_files) == 1

            # Verify JSON file is not empty and is valid JSON
            with open(json_files[0]) as f:
                content = f.read()
                assert len(content) > 0
                # The file should contain valid JSON (even if simple string from treelib)
                data = json.loads(content)
                # Verify file was created successfully (content is non-empty valid JSON)
                assert data is not None


def test_linktree_save_text_creates_file():
    """Test save creates a text file representation of the tree."""
    html = '<html><title>Test Text Save</title></html>'

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", html, 200),
    })

    tree = LinkTree("https://example.com", depth=0, client=client)
    tree.load()

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("torbot.modules.linktree.project_root_directory", tmpdir):
            tree.save()

            # Check that text file was created
            txt_files = list(Path(tmpdir).glob("*.txt"))
            assert len(txt_files) == 1

            # Verify file is not empty
            assert txt_files[0].stat().st_size > 0


def test_linktree_handles_non_200_status():
    """Verify LinkTree records non-200 status codes correctly."""
    html = '<html><title>Not Found</title></html>'

    client = FakeClient({
        "https://example.com/missing": FakeResponse(
            "https://example.com/missing", html, 404
        ),
    })

    tree = LinkTree("https://example.com/missing", depth=0, client=client)
    tree.load()

    root = tree.get_node("https://example.com/missing")
    assert root is not None
    assert root.data.status == 404


def test_linktree_filters_invalid_links():
    """Ensure non-crawlable links are filtered, and relative links are
    resolved against the page URL rather than dropped."""
    html = """
    <html>
        <title>Root</title>
        <a href="https://valid.com">Valid</a>
        <a href="/relative/path">Relative</a>
        <a href="javascript:void(0)">JS</a>
        <a href="mailto:test@example.com">Email</a>
        <a href="#fragment">Fragment</a>
    </html>
    """

    valid_html = '<html><title>Valid</title></html>'

    client = FakeClient({
        "https://example.com": FakeResponse("https://example.com", html, 200),
        "https://valid.com": FakeResponse("https://valid.com", valid_html, 200),
    })

    tree = LinkTree("https://example.com", depth=1, client=client)
    tree.load()

    # Should have 3 nodes: root + the absolute child + the relative child
    # (resolved against the root URL). javascript:/mailto:/# links are
    # filtered out entirely.
    all_nodes = tree.all_nodes()
    assert len(all_nodes) == 3
    assert tree.get_node("https://valid.com") is not None
    assert tree.get_node("https://example.com/relative/path") is not None
