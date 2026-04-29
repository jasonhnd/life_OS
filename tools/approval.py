# Forked from NousResearch/hermes-agent (MIT License) commit 59b56d445c34e1d4bf797f5345b802c7b5986c72
# Adapted for Life OS v1.7.2
"""Dangerous command approval for Life OS.

This module keeps the Hermes dangerous-command pattern corpus as the source
of truth while adapting runtime names and smart-approval behavior for Life OS.
"""

from __future__ import annotations

import contextlib
import contextvars
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PUBLIC_NAMESPACE = "lifeos_approval"
HERMES_SOURCE_COMMIT = "59b56d445c34e1d4bf797f5345b802c7b5986c72"
EXPECTED_HERMES_DANGEROUS_PATTERN_COUNT = 42

# Tirith availability flag — set to True the first time we discover
# tools.tirith_security is missing, so we only emit the disclosure mismatch
# warning ONCE per process instead of per command. R-1.8.0-013 deep-audit fix.
_TIRITH_UNAVAILABLE_WARNED: bool = False

# Per-thread/per-task session identity. The public namespace is intentionally
# Life OS specific; legacy Hermes environment variables are not consulted.
_approval_session_key: contextvars.ContextVar[str] = contextvars.ContextVar(
    "lifeos_approval_session_key",
    default="",
)


def set_current_session_key(session_key: str) -> contextvars.Token[str]:
    """Bind the active approval session key to the current context."""
    return _approval_session_key.set(session_key or "")


def reset_current_session_key(token: contextvars.Token[str]) -> None:
    """Restore the prior approval session key context."""
    _approval_session_key.reset(token)


def get_current_session_key(default: str = "default") -> str:
    """Return the active Life OS approval session key."""
    session_key = _approval_session_key.get()
    if session_key:
        return session_key
    return os.getenv("LIFEOS_SESSION_KEY", default)


# Sensitive write targets preserved from the Hermes source so the imported
# DANGEROUS_PATTERNS stay source-faithful.
_SSH_SENSITIVE_PATH = r'(?:~|\$home|\$\{home\})/\.ssh(?:/|$)'
_HERMES_ENV_PATH = (
    r'(?:~\/\.hermes/|'
    r'(?:\$home|\$\{home\})/\.hermes/|'
    r'(?:\$hermes_home|\$\{hermes_home\})/)'
    r'\.env\b'
)
_PROJECT_ENV_PATH = r'(?:(?:/|\.{1,2}/)?(?:[^\s/"\'`]+/)*\.env(?:\.[^/\s"\'`]+)*)'
_PROJECT_CONFIG_PATH = r'(?:(?:/|\.{1,2}/)?(?:[^\s/"\'`]+/)*config\.yaml)'
_SENSITIVE_WRITE_TARGET = (
    r'(?:/etc/|/dev/sd|'
    rf'{_SSH_SENSITIVE_PATH}|'
    rf'{_HERMES_ENV_PATH})'
)
_PROJECT_SENSITIVE_WRITE_TARGET = rf'(?:{_PROJECT_ENV_PATH}|{_PROJECT_CONFIG_PATH})'
_COMMAND_TAIL = r'(?:\s*(?:&&|\|\||;).*)?$'

# Regex fragment matching the start of a shell command.
_CMDPOS = (
    r'(?:^|[;&|\n`]|\$\()'
    r'\s*'
    r'(?:sudo\s+(?:-[^\s]+\s+)*)?'
    r'(?:env\s+(?:\w+=\S*\s+)*)?'
    r'(?:(?:exec|nohup|setsid|time)\s+)*'
    r'\s*'
)

HARDLINE_PATTERNS = [
    (r'\brm\s+(-[^\s]*\s+)*(/|/\*|/ \*)(\s|$)', "recursive delete of root filesystem"),
    (r'\brm\s+(-[^\s]*\s+)*(/home|/home/\*|/root|/root/\*|/etc|/etc/\*|/usr|/usr/\*|/var|/var/\*|/bin|/bin/\*|/sbin|/sbin/\*|/boot|/boot/\*|/lib|/lib/\*)(\s|$)', "recursive delete of system directory"),
    (r'\brm\s+(-[^\s]*\s+)*(~|\$HOME)(/?|/\*)?(\s|$)', "recursive delete of home directory"),
    (r'\bmkfs(\.[a-z0-9]+)?\b', "format filesystem (mkfs)"),
    (r'\bdd\b[^\n]*\bof=/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*', "dd to raw block device"),
    (r'>\s*/dev/(sd|nvme|hd|mmcblk|vd|xvd)[a-z0-9]*\b', "redirect to raw block device"),
    (r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:', "fork bomb"),
    (r'\bkill\s+(-[^\s]+\s+)*-1\b', "kill all processes"),
    (_CMDPOS + r'(shutdown|reboot|halt|poweroff)\b', "system shutdown/reboot"),
    (_CMDPOS + r'init\s+[06]\b', "init 0/6 (shutdown/reboot)"),
    (_CMDPOS + r'systemctl\s+(poweroff|reboot|halt|kexec)\b', "systemctl poweroff/reboot"),
    (_CMDPOS + r'telinit\s+[06]\b', "telinit 0/6 (shutdown/reboot)"),
]


def detect_hardline_command(command: str) -> tuple[bool, str | None]:
    """Check if a command matches the unconditional hardline blocklist."""
    normalized = _normalize_command_for_detection(command).lower()
    for pattern, description in HARDLINE_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE | re.DOTALL):
            return True, description
    return False, None


def _hardline_block_result(description: str) -> dict[str, Any]:
    """Build the standard block result for a hardline match."""
    return {
        "approved": False,
        "hardline": True,
        "message": (
            f"BLOCKED (hardline): {description}. "
            "This command is on the unconditional blocklist and cannot be "
            "executed via the agent, even with approval bypasses enabled. "
            "If you genuinely need to run it, run it yourself in a terminal "
            "outside the agent."
        ),
    }


# Hermes dangerous command corpus. Source had 47 entries at the requested
# commit snapshot in /tmp/hermes; the expected 42 count is intentionally not
# forced or padded.
DANGEROUS_PATTERNS = [
    (r'\brm\s+(-[^\s]*\s+)*/', "delete in root path"),
    (r'\brm\s+-[^\s]*r', "recursive delete"),
    (r'\brm\s+--recursive\b', "recursive delete (long flag)"),
    (r'\bchmod\s+(-[^\s]*\s+)*(777|666|o\+[rwx]*w|a\+[rwx]*w)\b', "world/other-writable permissions"),
    (r'\bchmod\s+--recursive\b.*(777|666|o\+[rwx]*w|a\+[rwx]*w)', "recursive world/other-writable (long flag)"),
    (r'\bchown\s+(-[^\s]*)?R\s+root', "recursive chown to root"),
    (r'\bchown\s+--recursive\b.*root', "recursive chown to root (long flag)"),
    (r'\bmkfs\b', "format filesystem"),
    (r'\bdd\s+.*if=', "disk copy"),
    (r'>\s*/dev/sd', "write to block device"),
    (r'\bDROP\s+(TABLE|DATABASE)\b', "SQL DROP"),
    (r'\bDELETE\s+FROM\b(?!.*\bWHERE\b)', "SQL DELETE without WHERE"),
    (r'\bTRUNCATE\s+(TABLE)?\s*\w', "SQL TRUNCATE"),
    (r'>\s*/etc/', "overwrite system config"),
    (r'\bsystemctl\s+(-[^\s]+\s+)*(stop|restart|disable|mask)\b', "stop/restart system service"),
    (r'\bkill\s+-9\s+-1\b', "kill all processes"),
    (r'\bpkill\s+-9\b', "force kill processes"),
    (r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:', "fork bomb"),
    (r'\b(bash|sh|zsh|ksh)\s+-[^\s]*c(\s+|$)', "shell command via -c/-lc flag"),
    (r'\b(python[23]?|perl|ruby|node)\s+-[ec]\s+', "script execution via -e/-c flag"),
    (r'\b(curl|wget)\b.*\|\s*(ba)?sh\b', "pipe remote content to shell"),
    (r'\b(bash|sh|zsh|ksh)\s+<\s*<?\s*\(\s*(curl|wget)\b', "execute remote script via process substitution"),
    (rf'\btee\b.*["\']?{_SENSITIVE_WRITE_TARGET}', "overwrite system file via tee"),
    (rf'>>?\s*["\']?{_SENSITIVE_WRITE_TARGET}', "overwrite system file via redirection"),
    (rf'\btee\b.*["\']?{_PROJECT_SENSITIVE_WRITE_TARGET}["\']?{_COMMAND_TAIL}', "overwrite project env/config via tee"),
    (rf'>>?\s*["\']?{_PROJECT_SENSITIVE_WRITE_TARGET}["\']?{_COMMAND_TAIL}', "overwrite project env/config via redirection"),
    (r'\bxargs\s+.*\brm\b', "xargs with rm"),
    (r'\bfind\b.*-exec\s+(/\S*/)?rm\b', "find -exec rm"),
    (r'\bfind\b.*-delete\b', "find -delete"),
    (r'\bhermes\s+gateway\s+(stop|restart)\b', "stop/restart hermes gateway (kills running agents)"),
    (r'\bhermes\s+update\b', "hermes update (restarts gateway, kills running agents)"),
    (r'gateway\s+run\b.*(&\s*$|&\s*;|\bdisown\b|\bsetsid\b)', "start gateway outside systemd (use 'systemctl --user restart hermes-gateway')"),
    (r'\bnohup\b.*gateway\s+run\b', "start gateway outside systemd (use 'systemctl --user restart hermes-gateway')"),
    (r'\b(pkill|killall)\b.*\b(hermes|gateway|cli\.py)\b', "kill hermes/gateway process (self-termination)"),
    (r'\bkill\b.*\$\(\s*pgrep\b', "kill process via pgrep expansion (self-termination)"),
    (r'\bkill\b.*`\s*pgrep\b', "kill process via backtick pgrep expansion (self-termination)"),
    (r'\b(cp|mv|install)\b.*\s/etc/', "copy/move file into /etc/"),
    (rf'\b(cp|mv|install)\b.*\s["\']?{_PROJECT_SENSITIVE_WRITE_TARGET}["\']?{_COMMAND_TAIL}', "overwrite project env/config file"),
    (r'\bsed\s+-[^\s]*i.*\s/etc/', "in-place edit of system config"),
    (r'\bsed\s+--in-place\b.*\s/etc/', "in-place edit of system config (long flag)"),
    (r'\b(python[23]?|perl|ruby|node)\s+<<', "script execution via heredoc"),
    (r'\bgit\s+reset\s+--hard\b', "git reset --hard (destroys uncommitted changes)"),
    (r'\bgit\s+push\b.*--force\b', "git force push (rewrites remote history)"),
    (r'\bgit\s+push\b.*-f\b', "git force push short flag (rewrites remote history)"),
    (r'\bgit\s+clean\s+-[^\s]*f', "git clean with force (deletes untracked files)"),
    (r'\bgit\s+branch\s+-D\b', "git branch force delete"),
    (r'\bchmod\s+\+x\b.*[;&|]+\s*\./', "chmod +x followed by immediate execution"),
]

DANGEROUS_PATTERN_COUNT = len(DANGEROUS_PATTERNS)


def _legacy_pattern_key(pattern: str) -> str:
    """Reproduce the old regex-derived approval key for compatibility."""
    return pattern.split(r'\b')[1] if r'\b' in pattern else pattern[:20]


_PATTERN_KEY_ALIASES: dict[str, set[str]] = {}
for _pattern, _description in DANGEROUS_PATTERNS:
    _legacy_key = _legacy_pattern_key(_pattern)
    _canonical_key = _description
    _PATTERN_KEY_ALIASES.setdefault(_canonical_key, set()).update({_canonical_key, _legacy_key})
    _PATTERN_KEY_ALIASES.setdefault(_legacy_key, set()).update({_legacy_key, _canonical_key})


def _approval_key_aliases(pattern_key: str) -> set[str]:
    """Return all approval keys that should match this pattern."""
    return _PATTERN_KEY_ALIASES.get(pattern_key, {pattern_key})


_ANSI_RE = re.compile(
    r"""
    \x1B
    (?:
        [@-Z\\-_]
      | \[
        [0-?]*
        [ -/]*
        [@-~]
      | \]
        .*?
        (?:\x07|\x1B\\)
    )
    """,
    re.VERBOSE | re.DOTALL,
)


def _strip_ansi(command: str) -> str:
    """Strip common ANSI escape sequences without depending on Hermes tools."""
    return _ANSI_RE.sub("", command)


def _normalize_command_for_detection(command: str) -> str:
    """Normalize a command string before dangerous-pattern matching."""
    command = _strip_ansi(command)
    command = command.replace("\x00", "")
    return unicodedata.normalize("NFKC", command)


def detect_dangerous_command(command: str) -> tuple[bool, str | None, str | None]:
    """Check if a command matches any dangerous patterns.

    Returns:
        (is_dangerous, pattern_key, description) or (False, None, None).
    """
    command_lower = _normalize_command_for_detection(command).lower()
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command_lower, re.IGNORECASE | re.DOTALL):
            return True, description, description
    return False, None, None


_lock = threading.Lock()
_pending: dict[str, dict[str, Any]] = {}
_session_approved: dict[str, set[str]] = {}
_session_yolo: set[str] = set()
_permanent_approved: set[str] = set()


class _ApprovalEntry:
    """One pending dangerous-command approval inside a gateway session."""

    __slots__ = ("event", "data", "result")

    def __init__(self, data: dict[str, Any]):
        self.event = threading.Event()
        self.data = data
        self.result: str | None = None


_gateway_queues: dict[str, list[_ApprovalEntry]] = {}
_gateway_notify_cbs: dict[str, Callable[[dict[str, Any]], None]] = {}


def register_gateway_notify(
    session_key: str,
    cb: Callable[[dict[str, Any]], None],
) -> None:
    """Register a per-session callback for sending approval requests."""
    with _lock:
        _gateway_notify_cbs[session_key] = cb


def unregister_gateway_notify(session_key: str) -> None:
    """Unregister the per-session gateway approval callback."""
    with _lock:
        _gateway_notify_cbs.pop(session_key, None)
        entries = _gateway_queues.pop(session_key, [])
        for entry in entries:
            entry.event.set()


def resolve_gateway_approval(session_key: str, choice: str, resolve_all: bool = False) -> int:
    """Resolve one or all pending approvals for a session."""
    with _lock:
        queue = _gateway_queues.get(session_key)
        if not queue:
            return 0
        if resolve_all:
            targets = list(queue)
            queue.clear()
        else:
            targets = [queue.pop(0)]
        if not queue:
            _gateway_queues.pop(session_key, None)

    for entry in targets:
        entry.result = choice
        entry.event.set()
    return len(targets)


def has_blocking_approval(session_key: str) -> bool:
    """Check if a session has one or more blocking gateway approvals."""
    with _lock:
        return bool(_gateway_queues.get(session_key))


def submit_pending(session_key: str, approval: dict[str, Any]) -> None:
    """Store a pending approval request for a session."""
    with _lock:
        _pending[session_key] = approval


def approve_session(session_key: str, pattern_key: str) -> None:
    """Approve a pattern for this session only."""
    with _lock:
        _session_approved.setdefault(session_key, set()).add(pattern_key)


def enable_session_yolo(session_key: str) -> None:
    """Enable YOLO bypass for a single session key."""
    if not session_key:
        return
    with _lock:
        _session_yolo.add(session_key)


def disable_session_yolo(session_key: str) -> None:
    """Disable YOLO bypass for a single session key."""
    if not session_key:
        return
    with _lock:
        _session_yolo.discard(session_key)


def clear_session(session_key: str) -> None:
    """Remove all approval and yolo state for a given session."""
    if not session_key:
        return
    with _lock:
        _session_approved.pop(session_key, None)
        _session_yolo.discard(session_key)
        _pending.pop(session_key, None)
        _gateway_queues.pop(session_key, None)


def is_session_yolo_enabled(session_key: str) -> bool:
    """Return True when YOLO bypass is enabled for a specific session."""
    if not session_key:
        return False
    with _lock:
        return session_key in _session_yolo


def is_current_session_yolo_enabled() -> bool:
    """Return True when the active approval session has YOLO bypass enabled."""
    return is_session_yolo_enabled(get_current_session_key(default=""))


def is_approved(session_key: str, pattern_key: str) -> bool:
    """Check if a pattern is approved session-wide or permanently."""
    aliases = _approval_key_aliases(pattern_key)
    with _lock:
        if any(alias in _permanent_approved for alias in aliases):
            return True
        session_approvals = _session_approved.get(session_key, set())
        return any(alias in session_approvals for alias in aliases)


def approve_permanent(pattern_key: str) -> None:
    """Add a pattern to the permanent allowlist."""
    with _lock:
        _permanent_approved.add(pattern_key)


def load_permanent(patterns: set[str]) -> None:
    """Bulk-load permanent allowlist entries."""
    with _lock:
        _permanent_approved.update(patterns)


def _allowlist_file() -> Path | None:
    raw = os.getenv("LIFEOS_APPROVAL_ALLOWLIST_FILE", "").strip()
    return Path(raw).expanduser() if raw else None


def load_permanent_allowlist() -> set[str]:
    """Load permanently allowed command patterns from Life OS config/env."""
    patterns = {
        item.strip()
        for item in os.getenv("LIFEOS_APPROVAL_ALLOWLIST", "").split(",")
        if item.strip()
    }
    path = _allowlist_file()
    if path and path.is_file():
        try:
            patterns.update(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        except OSError as exc:
            logger.warning("Failed to load Life OS approval allowlist: %s", exc)
    if patterns:
        load_permanent(patterns)
    return patterns


def save_permanent_allowlist(patterns: set[str]) -> None:
    """Save permanently allowed command patterns when a file is configured."""
    path = _allowlist_file()
    if not path:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(sorted(patterns)) + "\n", encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not save Life OS approval allowlist: %s", exc)


def prompt_dangerous_approval(
    command: str,
    description: str,
    timeout_seconds: int | None = None,
    allow_permanent: bool = True,
    approval_callback: Callable[..., str] | None = None,
) -> str:
    """Prompt the user to approve a dangerous command."""
    if timeout_seconds is None:
        timeout_seconds = _get_approval_timeout()

    if approval_callback is not None:
        try:
            return str(approval_callback(command, description, allow_permanent=allow_permanent))
        except Exception as exc:
            logger.error("Approval callback failed: %s", exc, exc_info=True)
            return "deny"

    os.environ["LIFEOS_SPINNER_PAUSE"] = "1"
    try:
        while True:
            print()
            print(f"  WARNING: DANGEROUS COMMAND: {description}")
            print(f"      {command}")
            print()
            if allow_permanent:
                print("      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny")
                prompt = "      Choice [o/s/a/D]: "
            else:
                print("      [o]nce  |  [s]ession  |  [d]eny")
                prompt = "      Choice [o/s/D]: "
            print()
            sys.stdout.flush()

            result = {"choice": ""}

            # Pass loop variables `result` and `prompt` as default args so the
            # closure captures THIS iteration's values, not the loop's last
            # iteration. R-1.8.0-013 deep-audit fix (ruff B023).
            def get_input(result: dict[str, str] = result, prompt: str = prompt) -> None:
                try:
                    result["choice"] = input(prompt).strip().lower()
                except (EOFError, OSError):
                    result["choice"] = ""

            thread = threading.Thread(target=get_input, daemon=True)
            thread.start()
            thread.join(timeout=timeout_seconds)

            if thread.is_alive():
                print("\n      Timeout - denying command")
                return "deny"

            choice = result["choice"]
            if choice in ("o", "once"):
                print("      Allowed once")
                return "once"
            if choice in ("s", "session"):
                print("      Allowed for this session")
                return "session"
            if choice in ("a", "always") and allow_permanent:
                print("      Added to permanent allowlist")
                return "always"
            print("      Denied")
            return "deny"
    except (EOFError, KeyboardInterrupt):
        print("\n      Cancelled")
        return "deny"
    finally:
        os.environ.pop("LIFEOS_SPINNER_PAUSE", None)
        print()
        sys.stdout.flush()


def _normalize_approval_mode(mode: Any) -> str:
    """Normalize approval mode values loaded from env/config."""
    if isinstance(mode, bool):
        return "off" if mode is False else "manual"
    if isinstance(mode, str):
        normalized = mode.strip().lower()
        return normalized or "manual"
    return "manual"


def _get_approval_config() -> dict[str, Any]:
    """Read Life OS approval settings from environment variables."""
    return {
        "mode": os.getenv("LIFEOS_APPROVAL_MODE", "manual"),
        "timeout": os.getenv("LIFEOS_APPROVAL_TIMEOUT", "60"),
        "cron_mode": os.getenv("LIFEOS_APPROVAL_CRON_MODE", "deny"),
        "gateway_timeout": os.getenv("LIFEOS_APPROVAL_GATEWAY_TIMEOUT", "300"),
    }


def _get_approval_mode() -> str:
    """Read the approval mode. Returns 'manual', 'smart', or 'off'."""
    return _normalize_approval_mode(_get_approval_config().get("mode", "manual"))


def _get_approval_timeout() -> int:
    """Read the approval timeout in seconds."""
    try:
        return int(_get_approval_config().get("timeout", 60))
    except (ValueError, TypeError):
        return 60


def _get_cron_approval_mode() -> str:
    """Read cron approval mode. Returns 'deny' or 'approve'."""
    mode = str(_get_approval_config().get("cron_mode", "deny")).lower().strip()
    if mode in ("approve", "off", "allow", "yes"):
        return "approve"
    return "deny"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _bash_executable() -> str | None:
    bash = shutil.which("bash")
    if bash:
        return bash
    for candidate in (
        Path("C:/Program Files/Git/bin/bash.exe"),
        Path("C:/Program Files/Git/usr/bin/bash.exe"),
        Path("C:/msys64/usr/bin/bash.exe"),
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def _smart_approve(command: str, description: str) -> str:
    """Ask Life OS compliance tooling for a smart-approval decision.

    Returns 'approve', 'deny', or 'escalate'. If the compliance checker does
    not support the smart-approval scenario yet, this deliberately degrades to
    manual escalation instead of falling back to the Hermes auxiliary LLM.
    """
    root = _repo_root()
    script = root / "scripts" / "lifeos-compliance-check.sh"
    if not script.is_file():
        logger.debug("Smart approval: compliance checker missing, escalating")
        return "escalate"
    bash = _bash_executable()
    if bash is None:
        logger.debug("Smart approval: bash unavailable, escalating")
        return "escalate"

    payload_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            delete=False,
            prefix="lifeos-smart-approval-",
            suffix=".txt",
        ) as payload:
            payload_path = Path(payload.name)
            payload.write("Life OS smart approval candidate\n")
            payload.write("\nCommand:\n")
            payload.write(command)
            payload.write("\n\nFlagged reason:\n")
            payload.write(description)
            payload.write("\n")

        result = subprocess.run(
            [bash, script.as_posix(), payload_path.as_posix(), "smart-approval"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.debug("Smart approval: compliance checker failed (%s), escalating", exc)
        return "escalate"
    finally:
        if payload_path is not None:
            with contextlib.suppress(OSError):
                payload_path.unlink()

    combined_output = f"{result.stdout}\n{result.stderr}".lower()
    if "no compliance checks defined" in combined_output:
        logger.debug("Smart approval: compliance scenario unsupported, escalating")
        return "escalate"
    if result.returncode == 0:
        return "approve"
    if result.returncode == 1:
        return "deny"
    return "escalate"


def check_dangerous_command(
    command: str,
    env_type: str,
    approval_callback: Callable[..., str] | None = None,
) -> dict[str, Any]:
    """Check if a command is dangerous and handle approval."""
    if env_type in ("docker", "singularity", "modal", "daytona"):
        return {"approved": True, "message": None}

    is_hardline, hardline_desc = detect_hardline_command(command)
    if is_hardline:
        logger.warning("Hardline block: %s (command: %s)", hardline_desc, command[:200])
        return _hardline_block_result(hardline_desc or "hardline command")

    if os.getenv("LIFEOS_YOLO_MODE") or is_current_session_yolo_enabled():
        return {"approved": True, "message": None}

    is_dangerous, pattern_key, description = detect_dangerous_command(command)
    if not is_dangerous:
        return {"approved": True, "message": None}

    session_key = get_current_session_key()
    if pattern_key and is_approved(session_key, pattern_key):
        return {"approved": True, "message": None}

    is_cli = os.getenv("LIFEOS_INTERACTIVE")
    is_gateway = os.getenv("LIFEOS_GATEWAY_SESSION")

    if not is_cli and not is_gateway:
        if os.getenv("LIFEOS_CRON_SESSION") and _get_cron_approval_mode() == "deny":
            return {
                "approved": False,
                "message": (
                    f"BLOCKED: Command flagged as dangerous ({description}) "
                    "but cron jobs run without a user present to approve it."
                ),
                "pattern_key": pattern_key,
                "description": description,
            }
        return {"approved": True, "message": None}

    if is_gateway or os.getenv("LIFEOS_EXEC_ASK"):
        submit_pending(session_key, {
            "command": command,
            "pattern_key": pattern_key,
            "description": description,
        })
        return {
            "approved": False,
            "pattern_key": pattern_key,
            "status": "approval_required",
            "command": command,
            "description": description,
            "message": (
                f"This command is potentially dangerous ({description}). "
                f"Asking the user for approval.\n\n**Command:**\n```\n{command}\n```"
            ),
        }

    choice = prompt_dangerous_approval(command, description or "dangerous command", approval_callback=approval_callback)
    if choice == "deny":
        return {
            "approved": False,
            "message": (
                f"BLOCKED: User denied this potentially dangerous command "
                f"(matched '{description}' pattern). Do NOT retry this command."
            ),
            "pattern_key": pattern_key,
            "description": description,
        }

    if choice == "session" and pattern_key:
        approve_session(session_key, pattern_key)
    elif choice == "always" and pattern_key:
        approve_session(session_key, pattern_key)
        approve_permanent(pattern_key)
        save_permanent_allowlist(_permanent_approved)

    return {"approved": True, "message": None}


def _format_tirith_description(tirith_result: dict[str, Any]) -> str:
    """Build a human-readable description from tirith findings."""
    findings = tirith_result.get("findings") or []
    if not findings:
        summary = tirith_result.get("summary") or "security issue detected"
        return f"Security scan: {summary}"

    parts = []
    for finding in findings:
        severity = finding.get("severity", "")
        title = finding.get("title", "")
        desc = finding.get("description", "")
        if title and desc:
            parts.append(f"[{severity}] {title}: {desc}" if severity else f"{title}: {desc}")
        elif title:
            parts.append(f"[{severity}] {title}" if severity else title)
    if not parts:
        summary = tirith_result.get("summary") or "security issue detected"
        return f"Security scan: {summary}"
    return "Security scan - " + "; ".join(parts)


def check_all_command_guards(
    command: str,
    env_type: str,
    approval_callback: Callable[..., str] | None = None,
) -> dict[str, Any]:
    """Run all pre-exec security checks and return one approval decision."""
    if env_type in ("docker", "singularity", "modal", "daytona"):
        return {"approved": True, "message": None}

    is_hardline, hardline_desc = detect_hardline_command(command)
    if is_hardline:
        logger.warning("Hardline block: %s (command: %s)", hardline_desc, command[:200])
        return _hardline_block_result(hardline_desc or "hardline command")

    approval_mode = _get_approval_mode()
    if os.getenv("LIFEOS_YOLO_MODE") or is_current_session_yolo_enabled() or approval_mode == "off":
        return {"approved": True, "message": None}

    is_cli = os.getenv("LIFEOS_INTERACTIVE")
    is_gateway = os.getenv("LIFEOS_GATEWAY_SESSION")
    is_ask = os.getenv("LIFEOS_EXEC_ASK")

    if not is_cli and not is_gateway and not is_ask:
        if os.getenv("LIFEOS_CRON_SESSION") and _get_cron_approval_mode() == "deny":
            is_dangerous, _pattern_key, description = detect_dangerous_command(command)
            if is_dangerous:
                return {
                    "approved": False,
                    "message": (
                        f"BLOCKED: Command flagged as dangerous ({description}) "
                        "but cron jobs run without a user present to approve it."
                    ),
                }
        return {"approved": True, "message": None}

    # Tirith is an OPTIONAL secondary security check (semantic analysis on
    # top of pattern matching). When the optional tools.tirith_security module
    # is absent, the previous code silently swallowed ImportError — making
    # setup-hooks.sh's "tirith enabled" disclosure inaccurate. R-1.8.0-013
    # deep-audit fix: log the unavailability ONCE per process to stderr so
    # operators see that Tirith is not actually running, then continue with
    # pattern-only checks. Pattern matching alone still blocks 47+ dangerous
    # invocations and is sufficient for the documented baseline guarantees.
    tirith_result: dict[str, Any] = {"action": "allow", "findings": [], "summary": ""}
    global _TIRITH_UNAVAILABLE_WARNED  # noqa: PLW0603
    try:
        from tools.tirith_security import check_command_security

        tirith_result = check_command_security(command)
    except ImportError:
        if not _TIRITH_UNAVAILABLE_WARNED:
            print(
                "[approval] tirith_security module not installed — "
                "running pattern-only checks. setup-hooks.sh disclosure "
                "may overstate coverage. Install tools/tirith_security.py "
                "or update the disclosure text.",
                file=sys.stderr,
            )
            _TIRITH_UNAVAILABLE_WARNED = True

    is_dangerous, pattern_key, description = detect_dangerous_command(command)
    warnings: list[tuple[str, str, bool]] = []
    session_key = get_current_session_key()

    if tirith_result["action"] in ("block", "warn"):
        findings = tirith_result.get("findings") or []
        rule_id = findings[0].get("rule_id", "unknown") if findings else "unknown"
        tirith_key = f"tirith:{rule_id}"
        tirith_desc = _format_tirith_description(tirith_result)
        if not is_approved(session_key, tirith_key):
            warnings.append((tirith_key, tirith_desc, True))

    if is_dangerous and pattern_key and not is_approved(session_key, pattern_key):
        warnings.append((pattern_key, description or pattern_key, False))

    if not warnings:
        return {"approved": True, "message": None}

    combined_desc = "; ".join(desc for _, desc, _ in warnings)
    if approval_mode == "smart":
        verdict = _smart_approve(command, combined_desc)
        if verdict == "approve":
            for key, _, _ in warnings:
                approve_session(session_key, key)
            logger.debug("Smart approval: auto-approved '%s' (%s)", command[:60], combined_desc)
            return {
                "approved": True,
                "message": None,
                "smart_approved": True,
                "description": combined_desc,
            }
        if verdict == "deny":
            return {
                "approved": False,
                "message": (
                    f"BLOCKED by Life OS smart approval: {combined_desc}. "
                    "The command was assessed as genuinely dangerous. Do NOT retry."
                ),
                "smart_denied": True,
            }

    primary_key = warnings[0][0]
    all_keys = [key for key, _, _ in warnings]
    has_tirith = any(is_tirith for _, _, is_tirith in warnings)

    if is_gateway or is_ask:
        with _lock:
            notify_cb = _gateway_notify_cbs.get(session_key)

        if notify_cb is not None:
            approval_data = {
                "command": command,
                "pattern_key": primary_key,
                "pattern_keys": all_keys,
                "description": combined_desc,
            }
            entry = _ApprovalEntry(approval_data)
            with _lock:
                _gateway_queues.setdefault(session_key, []).append(entry)

            try:
                notify_cb(approval_data)
            except Exception as exc:
                logger.warning("Gateway approval notify failed: %s", exc)
                with _lock:
                    queue = _gateway_queues.get(session_key, [])
                    if entry in queue:
                        queue.remove(entry)
                    if not queue:
                        _gateway_queues.pop(session_key, None)
                return {
                    "approved": False,
                    "message": "BLOCKED: Failed to send approval request to user. Do NOT retry.",
                    "pattern_key": primary_key,
                    "description": combined_desc,
                }

            timeout = _get_approval_config().get("gateway_timeout", 300)
            try:
                timeout = int(timeout)
            except (ValueError, TypeError):
                timeout = 300

            deadline = time.monotonic() + max(timeout, 0)
            resolved = False
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                if entry.event.wait(timeout=min(1.0, remaining)):
                    resolved = True
                    break

            with _lock:
                queue = _gateway_queues.get(session_key, [])
                if entry in queue:
                    queue.remove(entry)
                if not queue:
                    _gateway_queues.pop(session_key, None)

            choice = entry.result
            if not resolved or choice is None or choice == "deny":
                reason = "timed out" if not resolved else "denied by user"
                return {
                    "approved": False,
                    "message": f"BLOCKED: Command {reason}. Do NOT retry this command.",
                    "pattern_key": primary_key,
                    "description": combined_desc,
                }

            for key, _, is_tirith in warnings:
                if choice == "session" or (choice == "always" and is_tirith):
                    approve_session(session_key, key)
                elif choice == "always":
                    approve_session(session_key, key)
                    approve_permanent(key)
                    save_permanent_allowlist(_permanent_approved)

            return {
                "approved": True,
                "message": None,
                "user_approved": True,
                "description": combined_desc,
            }

        submit_pending(session_key, {
            "command": command,
            "pattern_key": primary_key,
            "pattern_keys": all_keys,
            "description": combined_desc,
        })
        return {
            "approved": False,
            "pattern_key": primary_key,
            "status": "approval_required",
            "command": command,
            "description": combined_desc,
            "message": f"{combined_desc}. Asking the user for approval.\n\n**Command:**\n```\n{command}\n```",
        }

    choice = prompt_dangerous_approval(
        command,
        combined_desc,
        allow_permanent=not has_tirith,
        approval_callback=approval_callback,
    )
    if choice == "deny":
        return {
            "approved": False,
            "message": "BLOCKED: User denied. Do NOT retry.",
            "pattern_key": primary_key,
            "description": combined_desc,
        }

    for key, _, is_tirith in warnings:
        if choice == "session" or (choice == "always" and is_tirith):
            approve_session(session_key, key)
        elif choice == "always":
            approve_session(session_key, key)
            approve_permanent(key)
            save_permanent_allowlist(_permanent_approved)

    return {
        "approved": True,
        "message": None,
        "user_approved": True,
        "description": combined_desc,
    }


def _main(argv: list[str] | None = None) -> int:
    """Small CLI used by shell hooks: read stdin and report first match."""
    argv = argv if argv is not None else sys.argv[1:]
    command = " ".join(argv) if argv else sys.stdin.read()
    is_dangerous, pattern_key, description = detect_dangerous_command(command)
    if is_dangerous:
        print(f"{pattern_key}\t{description}")
        return 1
    return 0


__all__ = [
    "PUBLIC_NAMESPACE",
    "HERMES_SOURCE_COMMIT",
    "EXPECTED_HERMES_DANGEROUS_PATTERN_COUNT",
    "DANGEROUS_PATTERNS",
    "DANGEROUS_PATTERN_COUNT",
    "HARDLINE_PATTERNS",
    "set_current_session_key",
    "reset_current_session_key",
    "get_current_session_key",
    "detect_hardline_command",
    "detect_dangerous_command",
    "register_gateway_notify",
    "unregister_gateway_notify",
    "resolve_gateway_approval",
    "has_blocking_approval",
    "submit_pending",
    "approve_session",
    "enable_session_yolo",
    "disable_session_yolo",
    "clear_session",
    "is_session_yolo_enabled",
    "is_current_session_yolo_enabled",
    "is_approved",
    "approve_permanent",
    "load_permanent",
    "load_permanent_allowlist",
    "save_permanent_allowlist",
    "prompt_dangerous_approval",
    "check_dangerous_command",
    "check_all_command_guards",
]


load_permanent_allowlist()

if __name__ == "__main__":
    raise SystemExit(_main())
