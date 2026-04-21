"""Shared fixtures for tools/lib/ tests — v1.7 Sprint 2.

Provides fixtures used by test_config.py, test_llm.py, and test_notion.py.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def tmp_second_brain(tmp_path: Path) -> Path:
    """Return a tmp directory acting as a second-brain root."""
    root = tmp_path / "second-brain"
    root.mkdir()
    return root


@pytest.fixture
def sample_config_toml() -> str:
    """A minimal-but-complete `.life-os.toml` text."""
    return """\
[second_brain]
root = "~/second-brain"

[tools]
backup_dest = "~/second-brain-backups"

[reconcile]
auto_fix = true

[search]
recency_boost_days = 120

[export]
default_format = "pdf"

[notion]
token_env_var = "NOTION_TOKEN"
workspace_id = "ws-demo-001"
"""


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[pytest.MonkeyPatch]:
    """Remove any LIFE_OS_* / NOTION_* env vars for test isolation."""
    import os

    for key in list(os.environ):
        if key.startswith("LIFE_OS_") or key.startswith("NOTION_"):
            monkeypatch.delenv(key, raising=False)
    yield monkeypatch
