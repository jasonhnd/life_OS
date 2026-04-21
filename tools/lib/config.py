"""Life OS tools — per-user TOML config loader (v1.7 Sprint 2).

Loads ``~/second-brain/.life-os.toml`` into an immutable ``LifeOSConfig``
dataclass. All 12 tools in ``tools/`` should import from this module —
no scattered ``os.path.expanduser`` calls.

Precedence (highest first), per references/tools-spec.md §8:

    CLI flags  >  env vars (LIFE_OS_*)  >  .life-os.toml  >  defaults

CLI overrides are applied by the caller; this module handles env vars
and toml.

Env var names (all string-valued; coerced at parse time):

    LIFE_OS_SECOND_BRAIN_ROOT
    LIFE_OS_BACKUP_DEST
    LIFE_OS_RECONCILE_AUTO_FIX           ("true"/"false"/"1"/"0")
    LIFE_OS_SEARCH_RECENCY_BOOST_DAYS    (int)
    LIFE_OS_EXPORT_DEFAULT_FORMAT
    LIFE_OS_NOTION_TOKEN_ENV_VAR
    LIFE_OS_NOTION_WORKSPACE_ID

Tilde (``~``) in any path is expanded via ``Path.expanduser()``.

This module uses only stdlib (``tomllib`` available from Python 3.11+).
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ─── Public API ─────────────────────────────────────────────────────────────


class ConfigError(Exception):
    """Raised when the config file cannot be parsed or a value is invalid."""


@dataclass(frozen=True)
class LifeOSConfig:
    """Immutable view of the resolved Life OS configuration.

    All paths are absolute and tilde-expanded. Missing-file or missing-key
    scenarios fall through to well-known defaults.
    """

    second_brain_root: Path
    backup_dest: Path
    reconcile_auto_fix: bool
    search_recency_boost_days: int
    export_default_format: str
    notion_token_env_var: str | None = None
    notion_workspace_id: str | None = None


# ─── Defaults ───────────────────────────────────────────────────────────────

_DEFAULT_BACKUP_DIR_NAME = "second-brain-backups"
_DEFAULT_RECENCY_BOOST_DAYS = 90
_DEFAULT_EXPORT_FORMAT = "pdf"
_DEFAULT_AUTO_FIX = False


# ─── Helpers ────────────────────────────────────────────────────────────────


def get_config_path(root: Path) -> Path:
    """Return the on-disk path of the .life-os.toml for a given root."""
    return root / ".life-os.toml"


def _expand(path_str: str) -> Path:
    """Expand a user string (possibly containing ``~``) to an absolute Path."""
    return Path(path_str).expanduser()


def _parse_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    raise ConfigError(f"Expected boolean for {field}, got {value!r}")


def _parse_int(value: Any, *, field: str) -> int:
    if isinstance(value, bool):
        # Guard: bool is a subclass of int — reject explicitly.
        raise ConfigError(f"Expected int for {field}, got bool {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        try:
            return int(stripped)
        except ValueError as exc:
            raise ConfigError(
                f"Expected int for {field}, got {value!r}"
            ) from exc
    raise ConfigError(f"Expected int for {field}, got type {type(value).__name__}")


def _load_toml(path: Path) -> dict[str, Any]:
    """Return parsed toml dict, or {} if file is absent."""
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Failed to parse TOML at {path}: {exc}") from exc
    except OSError as exc:  # pragma: no cover - rare file-system edge
        raise ConfigError(f"Cannot read config at {path}: {exc}") from exc


def _section(data: dict[str, Any], name: str) -> dict[str, Any]:
    """Return the named section as a dict, or {} if absent / not a dict."""
    value = data.get(name, {})
    if not isinstance(value, dict):
        raise ConfigError(
            f"Expected [{name}] to be a TOML table, got {type(value).__name__}"
        )
    return value


# ─── Main loader ────────────────────────────────────────────────────────────


def load_config(root: Path | None = None) -> LifeOSConfig:
    """Load the effective Life OS config.

    :param root: Optional second-brain root path. If ``None``, defaults to
        ``~/second-brain``. When explicitly passed, this root becomes the
        fallback for ``second_brain_root`` if no toml / env value overrides it.
    :returns: A fully populated, immutable ``LifeOSConfig``.
    :raises ConfigError: on malformed toml or un-coercible field values.
    """
    default_root = root if root is not None else (Path.home() / "second-brain")
    toml_path = get_config_path(default_root)
    toml_data = _load_toml(toml_path)

    # --- second_brain.root -------------------------------------------------
    sb_section = _section(toml_data, "second_brain")
    toml_root = sb_section.get("root")
    if toml_root is not None:
        if not isinstance(toml_root, str):
            raise ConfigError(
                f"[second_brain] root must be a string, got {type(toml_root).__name__}"
            )
        second_brain_root = _expand(toml_root)
    else:
        second_brain_root = default_root

    env_root = os.environ.get("LIFE_OS_SECOND_BRAIN_ROOT")
    if env_root:
        second_brain_root = _expand(env_root)

    # --- tools.backup_dest -------------------------------------------------
    tools_section = _section(toml_data, "tools")
    toml_backup = tools_section.get("backup_dest")
    if toml_backup is not None:
        if not isinstance(toml_backup, str):
            raise ConfigError(
                f"[tools] backup_dest must be a string, got {type(toml_backup).__name__}"
            )
        backup_dest = _expand(toml_backup)
    else:
        # Default: sibling directory next to the second-brain root
        backup_dest = second_brain_root.parent / _DEFAULT_BACKUP_DIR_NAME

    env_backup = os.environ.get("LIFE_OS_BACKUP_DEST")
    if env_backup:
        backup_dest = _expand(env_backup)

    # --- reconcile.auto_fix ------------------------------------------------
    recon_section = _section(toml_data, "reconcile")
    reconcile_auto_fix = _DEFAULT_AUTO_FIX
    if "auto_fix" in recon_section:
        reconcile_auto_fix = _parse_bool(
            recon_section["auto_fix"], field="[reconcile] auto_fix"
        )
    env_auto = os.environ.get("LIFE_OS_RECONCILE_AUTO_FIX")
    if env_auto is not None:
        reconcile_auto_fix = _parse_bool(
            env_auto, field="LIFE_OS_RECONCILE_AUTO_FIX"
        )

    # --- search.recency_boost_days ----------------------------------------
    search_section = _section(toml_data, "search")
    recency_days = _DEFAULT_RECENCY_BOOST_DAYS
    if "recency_boost_days" in search_section:
        recency_days = _parse_int(
            search_section["recency_boost_days"],
            field="[search] recency_boost_days",
        )
    env_rec = os.environ.get("LIFE_OS_SEARCH_RECENCY_BOOST_DAYS")
    if env_rec is not None:
        recency_days = _parse_int(
            env_rec, field="LIFE_OS_SEARCH_RECENCY_BOOST_DAYS"
        )

    # --- export.default_format --------------------------------------------
    export_section = _section(toml_data, "export")
    export_format = _DEFAULT_EXPORT_FORMAT
    if "default_format" in export_section:
        raw = export_section["default_format"]
        if not isinstance(raw, str):
            raise ConfigError(
                f"[export] default_format must be a string, got {type(raw).__name__}"
            )
        export_format = raw
    env_fmt = os.environ.get("LIFE_OS_EXPORT_DEFAULT_FORMAT")
    if env_fmt:
        export_format = env_fmt

    # --- notion section (all optional) ------------------------------------
    notion_section = _section(toml_data, "notion")
    notion_token_env_var = notion_section.get("token_env_var")
    notion_workspace_id = notion_section.get("workspace_id")

    if notion_token_env_var is not None and not isinstance(notion_token_env_var, str):
        raise ConfigError(
            f"[notion] token_env_var must be a string, "
            f"got {type(notion_token_env_var).__name__}"
        )
    if notion_workspace_id is not None and not isinstance(notion_workspace_id, str):
        raise ConfigError(
            f"[notion] workspace_id must be a string, "
            f"got {type(notion_workspace_id).__name__}"
        )

    env_tok = os.environ.get("LIFE_OS_NOTION_TOKEN_ENV_VAR")
    if env_tok:
        notion_token_env_var = env_tok
    env_ws = os.environ.get("LIFE_OS_NOTION_WORKSPACE_ID")
    if env_ws:
        notion_workspace_id = env_ws

    return LifeOSConfig(
        second_brain_root=second_brain_root,
        backup_dest=backup_dest,
        reconcile_auto_fix=reconcile_auto_fix,
        search_recency_boost_days=recency_days,
        export_default_format=export_format,
        notion_token_env_var=notion_token_env_var,
        notion_workspace_id=notion_workspace_id,
    )


__all__ = [
    "ConfigError",
    "LifeOSConfig",
    "get_config_path",
    "load_config",
]
