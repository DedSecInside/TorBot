from importlib import metadata

from main import set_arguments
from torbot.cli import get_version
from torbot.modules.app_launcher import find_torbot_app, launch_torbot_app
from torbot.modules.linktree import parse_links


def test_version_flag_does_not_require_url() -> None:
    parser = set_arguments()
    args = parser.parse_args(["--version"])

    assert args.version is True
    assert args.url is None


def test_app_command_does_not_require_url() -> None:
    parser = set_arguments()
    args = parser.parse_args(["app"])

    assert args.command == "app"
    assert args.url is None


def test_app_flag_does_not_require_url() -> None:
    parser = set_arguments()
    args = parser.parse_args(["--app"])

    assert args.app is True
    assert args.url is None


def test_get_version_reads_pyproject_when_package_metadata_is_unavailable(
    monkeypatch,
) -> None:
    def missing_package(_: str) -> str:
        raise metadata.PackageNotFoundError

    monkeypatch.setattr(metadata, "version", missing_package)

    assert get_version() == "4.3.0"


def test_find_torbot_app_from_explicit_directory(tmp_path) -> None:
    app_dir = tmp_path / "TorBotApp"
    app_dir.mkdir()
    (app_dir / "package.json").write_text("{}", encoding="utf-8")

    assert find_torbot_app(tmp_path / "TorBot", app_dir=str(app_dir)) == app_dir


def test_launch_torbot_app_reports_missing_checkout(tmp_path, capsys) -> None:
    exit_code = launch_torbot_app(
        tmp_path / "TorBot",
        app_dir=str(tmp_path / "missing-app"),
    )

    assert exit_code == 1
    assert "TorBotApp is not installed" in capsys.readouterr().out


def test_parse_links_resolves_relative_urls_against_base_url() -> None:
    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="https://example.com/docs">Docs</a>
            <a href="javascript:void(0)">JS</a>
        </body>
    </html>
    """

    links = parse_links(html, base_url="https://example.com/index")

    assert links == ["https://example.com/about", "https://example.com/docs"]
