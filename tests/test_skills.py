"""Integration tests for the skills observability CLI."""

from __future__ import annotations

import json
import sys
import urllib.request
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

from tools import skills as skills_cli
from tools.lib import skills_upstream as upstream

EXPECTED_COLUMNS = (
    "name",
    "version",
    "installed-at",
    "source",
    "upstream-latest",
    "status",
    "triggers-hint",
)


def _isolate_cli_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    home = tmp_path / "home"
    home.mkdir()
    cache_path = tmp_path / "cache" / "skills-upstream.json"

    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv(upstream.ENV_CACHE_PATH, str(cache_path))
    return home, cache_path


def _block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_urlopen(request: object, timeout: float) -> Any:
        raise AssertionError("skills CLI tests must not use the network")

    monkeypatch.setattr(urllib.request, "urlopen", fail_urlopen)


def _run_cli(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *args: str,
) -> tuple[int, str, str]:
    monkeypatch.setattr(sys, "argv", ["skills", *args])

    exit_code = skills_cli.main()
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def _write_skill(home: Path, skill_id: str, frontmatter: str) -> Path:
    skill_path = home / ".claude" / "skills" / skill_id / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(
        f"---\n{dedent(frontmatter).strip()}\n---\n# {skill_id}\n",
        encoding="utf-8",
    )
    return skill_path


def _write_raw_skill(home: Path, skill_id: str, content: str) -> Path:
    skill_path = home / ".claude" / "skills" / skill_id / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


def _write_cache(cache_path: Path, entries: dict[str, str]) -> None:
    now = datetime.now(UTC)
    upstream.write_upstream_cache(
        upstream.UpstreamCache(
            entries={
                source: upstream.CacheEntry(
                    latest_version=latest_version,
                    fetched_at=now,
                    url=f"https://example.test/{index}",
                )
                for index, (source, latest_version) in enumerate(entries.items())
            }
        ),
        cache_path,
    )


def _json_rows(output: str) -> list[dict[str, str]]:
    rows = json.loads(output)
    assert isinstance(rows, list)
    return rows


def _assert_markdown_columns(output: str) -> None:
    first_line = output.splitlines()[0]
    assert first_line == "| " + " | ".join(EXPECTED_COLUMNS) + " |"


def _assert_json_fields(rows: Sequence[dict[str, str]]) -> None:
    for row in rows:
        assert tuple(row) == EXPECTED_COLUMNS


def test_list_empty_directory_renders_markdown_columns_and_exits_zero(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, _cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    (home / ".claude" / "skills").mkdir(parents=True)

    exit_code, stdout, stderr = _run_cli(monkeypatch, capsys, "list")

    assert exit_code == 0
    assert stderr == ""
    _assert_markdown_columns(stdout)
    assert stdout.splitlines() == [
        "| name | version | installed-at | source | upstream-latest | status | triggers-hint |",
        "|---|---:|---|---|---:|---|---|",
    ]


def test_four_skill_fixture_json_uses_hyphen_keys_and_reports_update_and_stale(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    _write_skill(
        home,
        "alpha-current",
        """
        name: Alpha Current
        version: 1.0.0
        source: skills://alpha-current
        triggers:
          - alpha
          - current
          - local
          - extra
        """,
    )
    _write_skill(
        home,
        "beta-update",
        """
        name: Beta Update
        version: 1.0.0
        source: npm://beta-update
        triggers: beta, update
        """,
    )
    _write_skill(
        home,
        "delta-upstream-current",
        """
        name: Delta Upstream Current
        version: 2.0.0
        source: pypi://delta-current
        triggers: [delta, docs, current]
        """,
    )
    _write_skill(
        home,
        "gamma-stale",
        """
        name: Gamma Stale
        version: 0.1.0
        installed-at: 2000-01-01
        source: local
        triggers: gamma, stale, old, ignored
        """,
    )
    _write_cache(
        cache_path,
        {
            "npm://beta-update": "1.2.0",
            "pypi://delta-current": "2.0.0",
        },
    )

    exit_code, stdout, stderr = _run_cli(
        monkeypatch, capsys, "check", "--format", "json"
    )

    assert exit_code == 2
    assert stderr == ""
    rows = _json_rows(stdout)
    _assert_json_fields(rows)
    assert [row["name"] for row in rows] == [
        "Alpha Current",
        "Beta Update",
        "Delta Upstream Current",
        "Gamma Stale",
    ]
    assert rows[0]["triggers-hint"] == "alpha, current, local"
    assert rows[1]["upstream-latest"] == "1.2.0 (cached 0d ago)"
    assert rows[1]["status"] == skills_cli.STATUS_UPDATE_AVAILABLE
    assert rows[3]["status"] == skills_cli.STATUS_STALE


def test_check_update_available_exits_one_with_markdown_columns(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    _write_skill(
        home,
        "updatable",
        """
        name: Updatable
        version: 1.0.0
        source: npm://updatable
        triggers: update
        """,
    )
    _write_cache(cache_path, {"npm://updatable": "1.1.0"})

    exit_code, stdout, stderr = _run_cli(monkeypatch, capsys, "check")

    assert exit_code == 1
    assert stderr == ""
    _assert_markdown_columns(stdout)
    assert skills_cli.STATUS_UPDATE_AVAILABLE in stdout


def test_stale_command_filters_stale_rows_and_exits_two(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, _cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    _write_skill(
        home,
        "current",
        """
        name: Current
        version: 1.0.0
        source: skills://current
        triggers: current
        """,
    )
    _write_skill(
        home,
        "stale",
        """
        name: Stale
        version: 1.0.0
        installed-at: 2000-01-01
        source: local
        triggers: stale
        """,
    )

    exit_code, stdout, stderr = _run_cli(
        monkeypatch, capsys, "stale", "--format", "json"
    )

    assert exit_code == 2
    assert stderr == ""
    rows = _json_rows(stdout)
    _assert_json_fields(rows)
    assert [row["name"] for row in rows] == ["Stale"]
    assert rows[0]["status"] == skills_cli.STATUS_STALE


def test_corrupt_skill_metadata_keeps_rows_and_exits_three(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    _write_raw_skill(
        home,
        "broken",
        "---\nname: : :\nversion: 1.0.0\n---\n# Broken\n",
    )
    _write_skill(
        home,
        "stale",
        """
        name: Stale
        version: 1.0.0
        installed-at: 2000-01-01
        source: local
        triggers: stale
        """,
    )
    _write_skill(
        home,
        "update",
        """
        name: Update
        version: 1.0.0
        source: npm://update
        triggers: update
        """,
    )
    _write_cache(cache_path, {"npm://update": "1.1.0"})

    exit_code, stdout, stderr = _run_cli(
        monkeypatch, capsys, "check", "--format", "json"
    )

    assert exit_code == 3
    assert stderr == ""
    rows = _json_rows(stdout)
    _assert_json_fields(rows)
    by_name = {row["name"]: row for row in rows}
    assert by_name["broken"]["status"] == skills_cli.STATUS_CHECK_FAILED
    assert by_name["broken"]["upstream-latest"] == skills_cli.UNKNOWN_VALUE
    assert by_name["Stale"]["status"] == skills_cli.STATUS_STALE
    assert by_name["Update"]["status"] == skills_cli.STATUS_UPDATE_AVAILABLE


def test_corrupt_upstream_cache_exits_three_without_rows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    _write_skill(
        home,
        "valid",
        """
        name: Valid
        version: 1.0.0
        source: skills://valid
        triggers: valid
        """,
    )
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text("{not-json", encoding="utf-8")

    exit_code, stdout, stderr = _run_cli(monkeypatch, capsys, "list")

    assert exit_code == 3
    assert stdout == ""
    assert "Cannot parse upstream cache" in stderr


def test_offline_uses_cache_without_network_and_marks_check_failed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home, cache_path = _isolate_cli_home(monkeypatch, tmp_path)
    _block_network(monkeypatch)
    _write_skill(
        home,
        "offline",
        """
        name: Offline
        version: 1.0.0
        source: npm://offline
        triggers: offline, cache
        """,
    )
    _write_cache(cache_path, {"npm://offline": "1.0.0"})

    exit_code, stdout, stderr = _run_cli(
        monkeypatch, capsys, "check", "--offline", "--format", "json"
    )

    assert exit_code == 0
    assert stderr == ""
    rows = _json_rows(stdout)
    _assert_json_fields(rows)
    assert rows == [
        {
            "name": "Offline",
            "version": "1.0.0",
            "installed-at": rows[0]["installed-at"],
            "source": "npm://offline",
            "upstream-latest": "? (cached 0d ago)",
            "status": skills_cli.STATUS_CHECK_FAILED,
            "triggers-hint": "offline, cache",
        }
    ]
