"""Tests for tools/lib/config.py — v1.7 Sprint 2.

Per references/tools-spec.md §8:
 - Per-user config at ~/second-brain/.life-os.toml (stdlib tomllib)
 - Precedence: CLI > env vars (LIFE_OS_*) > toml > defaults
 - Fail fast (ConfigError) if required fields missing or TOML is malformed
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.lib.config import (
    ConfigError,
    LifeOSConfig,
    get_config_path,
    load_config,
)

# ─── get_config_path ────────────────────────────────────────────────────────


def test_get_config_path_returns_root_slash_dot_life_os_toml(tmp_path: Path) -> None:
    assert get_config_path(tmp_path) == tmp_path / ".life-os.toml"


# ─── load_config: defaults when file absent ─────────────────────────────────


def test_load_config_missing_file_returns_defaults(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    """No .life-os.toml → should still return a LifeOSConfig with defaults."""
    cfg = load_config(tmp_second_brain)
    assert isinstance(cfg, LifeOSConfig)
    assert cfg.second_brain_root == tmp_second_brain
    # Default backup: sibling "second-brain-backups"
    assert cfg.backup_dest.name == "second-brain-backups"
    assert cfg.reconcile_auto_fix is False
    assert cfg.search_recency_boost_days == 90
    assert cfg.export_default_format == "pdf"
    assert cfg.notion_token_env_var is None
    assert cfg.notion_workspace_id is None


# ─── load_config: reads full toml ───────────────────────────────────────────


def test_load_config_full_toml_maps_all_fields(
    tmp_second_brain: Path,
    sample_config_toml: str,
    clean_env: pytest.MonkeyPatch,
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(sample_config_toml, encoding="utf-8")

    cfg = load_config(tmp_second_brain)

    # second_brain.root is tilde-expanded from toml
    assert cfg.second_brain_root == Path.home() / "second-brain"
    assert cfg.backup_dest == Path.home() / "second-brain-backups"
    assert cfg.reconcile_auto_fix is True
    assert cfg.search_recency_boost_days == 120
    assert cfg.export_default_format == "pdf"
    assert cfg.notion_token_env_var == "NOTION_TOKEN"
    assert cfg.notion_workspace_id == "ws-demo-001"


# ─── load_config: malformed toml raises ConfigError ─────────────────────────


def test_load_config_malformed_toml_raises_config_error(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(
        "[second_brain\nroot = broken", encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="parse|TOML|toml"):
        load_config(tmp_second_brain)


# ─── load_config: partial toml falls back to defaults ───────────────────────


def test_load_config_partial_toml_uses_defaults_for_missing_sections(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    """If only [second_brain] present, other fields should be defaults."""
    (tmp_second_brain / ".life-os.toml").write_text(
        '[second_brain]\nroot = "~/my-brain"\n', encoding="utf-8"
    )
    cfg = load_config(tmp_second_brain)
    assert cfg.second_brain_root == Path.home() / "my-brain"
    assert cfg.reconcile_auto_fix is False  # default
    assert cfg.search_recency_boost_days == 90  # default
    assert cfg.export_default_format == "pdf"  # default


# ─── load_config: env vars override toml ────────────────────────────────────


def test_env_var_overrides_toml_backup_dest(
    tmp_second_brain: Path,
    sample_config_toml: str,
    clean_env: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(sample_config_toml, encoding="utf-8")
    env_dest = tmp_path / "env-backup"
    clean_env.setenv("LIFE_OS_BACKUP_DEST", str(env_dest))

    cfg = load_config(tmp_second_brain)
    assert cfg.backup_dest == env_dest


def test_env_var_overrides_toml_recency_boost(
    tmp_second_brain: Path,
    sample_config_toml: str,
    clean_env: pytest.MonkeyPatch,
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(sample_config_toml, encoding="utf-8")
    clean_env.setenv("LIFE_OS_SEARCH_RECENCY_BOOST_DAYS", "45")

    cfg = load_config(tmp_second_brain)
    assert cfg.search_recency_boost_days == 45


def test_env_var_invalid_int_raises_config_error(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    clean_env.setenv("LIFE_OS_SEARCH_RECENCY_BOOST_DAYS", "not-a-number")
    with pytest.raises(ConfigError, match="recency|int|LIFE_OS"):
        load_config(tmp_second_brain)


def test_env_var_overrides_toml_auto_fix(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(
        "[reconcile]\nauto_fix = false\n", encoding="utf-8"
    )
    clean_env.setenv("LIFE_OS_RECONCILE_AUTO_FIX", "true")

    cfg = load_config(tmp_second_brain)
    assert cfg.reconcile_auto_fix is True


# ─── tilde expansion ────────────────────────────────────────────────────────


def test_tilde_expansion_in_toml_paths(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(
        '[second_brain]\nroot = "~/a"\n[tools]\nbackup_dest = "~/b"\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_second_brain)
    assert cfg.second_brain_root == Path.home() / "a"
    assert cfg.backup_dest == Path.home() / "b"


# ─── notion section ─────────────────────────────────────────────────────────


def test_notion_section_optional(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    """If [notion] absent, notion_* fields are None."""
    (tmp_second_brain / ".life-os.toml").write_text(
        '[second_brain]\nroot = "~/x"\n', encoding="utf-8"
    )
    cfg = load_config(tmp_second_brain)
    assert cfg.notion_token_env_var is None
    assert cfg.notion_workspace_id is None


def test_notion_token_env_var_read(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    (tmp_second_brain / ".life-os.toml").write_text(
        '[notion]\ntoken_env_var = "MY_NOTION_VAR"\nworkspace_id = "abc"\n',
        encoding="utf-8",
    )
    cfg = load_config(tmp_second_brain)
    assert cfg.notion_token_env_var == "MY_NOTION_VAR"
    assert cfg.notion_workspace_id == "abc"


# ─── default root (no arg) ──────────────────────────────────────────────────


def test_load_config_default_root_uses_home_second_brain(
    clean_env: pytest.MonkeyPatch,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """load_config(None) / load_config() should use ~/second-brain."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    fake_brain = tmp_path / "second-brain"
    fake_brain.mkdir()

    cfg = load_config()
    assert cfg.second_brain_root == fake_brain


# ─── immutability ───────────────────────────────────────────────────────────


def test_life_os_config_is_frozen(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    cfg = load_config(tmp_second_brain)
    with pytest.raises((AttributeError, Exception)):
        cfg.reconcile_auto_fix = True  # type: ignore[misc]


# ─── non-dict toml raises ──────────────────────────────────────────────────


def test_toml_non_dict_value_for_section_raises(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    """E.g. [search] recency_boost_days = "abc" → int parse fails."""
    (tmp_second_brain / ".life-os.toml").write_text(
        '[search]\nrecency_boost_days = "abc"\n', encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="recency|int|type"):
        load_config(tmp_second_brain)


def test_toml_root_missing_but_section_present(
    tmp_second_brain: Path, clean_env: pytest.MonkeyPatch
) -> None:
    """[second_brain] section without 'root' key → use tmp_second_brain as default."""
    (tmp_second_brain / ".life-os.toml").write_text(
        "[second_brain]\n", encoding="utf-8"
    )
    cfg = load_config(tmp_second_brain)
    # Falls back to the passed root when toml's root is missing
    assert cfg.second_brain_root == tmp_second_brain
