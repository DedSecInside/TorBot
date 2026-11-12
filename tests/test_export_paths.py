from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from torbot.modules.info import fetch_html
from torbot.modules.linktree import LinkTree


@pytest.mark.parametrize("title", [
    "../outside/escaped", "/tmp/escaped", r"C:\outside\escaped",
    r"..\outside\escaped", "&#47;tmp&#47;escaped", "..", "",
    "CON", "NUL.txt", "a" * 1000, "Example page", "日本語のページ",
])
def test_exports_stay_in_output_directory(tmp_path, title):
    output = tmp_path / "output"
    output.mkdir()
    html = f"<html><title>{title}</title><body>Test page</body></html>"
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, text=html)
    )) as client:
        with patch("torbot.modules.linktree.project_root_directory", str(output)), patch(
            "torbot.modules.linktree.classify", return_value=["test", 1.0]
        ):
            tree = LinkTree("http://example.test", 0, client)
            tree.load()
            tree.save()
            tree.saveJSON()
            fetch_html(client, "http://example.test", tree, save_html=True)
            files = list(output.iterdir())
            assert len(files) == 3
            assert {p.suffix for p in files} == {".txt", ".json", ".html"}
            assert all(p.resolve().parent == output.resolve() for p in files)
            assert all(len(p.name) < 160 for p in files)
            assert len(list(tmp_path.rglob("*"))) == 4
            if title == "Example page":
                assert Path(tree._get_tree_file_name()).name == "Example page - Depth 0"
