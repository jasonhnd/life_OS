---
title: "Life OS MCP Server"
scope: "Hermes Local MCP wrapper"
audience: "maintainers"
status: "implementation note"
last_updated: 2026-04-26
related:
  - tools/mcp_server.py
  - docs/architecture/hermes-local.md
  - docs/architecture/execution-layer.md
---

# Life OS MCP Server

`tools/mcp_server.py` is a lightweight stdio-oriented MCP wrapper around the
existing Life OS Python tools. It does not replace `life-os-tool`; it exposes
the same command modules to MCP clients while keeping command behavior in the
existing argparse tools.

The server is part of Hermes Local's optional integration surface. It does not
run as an always-on daemon and does not decide orchestration semantics. Cortex
remains always-on in v1.7.2 at the host protocol layer; MCP tools only provide
local maintenance commands such as reindexing, migration, search, and backup.

## Exposed Tools

The server registers these 16 MCP tools:

- `stats`
- `migrate`
- `reconcile`
- `search`
- `daily-briefing`
- `research`
- `export`
- `sync-notion`
- `embed`
- `seed`
- `extract`
- `backup`
- `reindex`
- `rebuild-session-index`
- `rebuild-concept-index`
- `cli`

Every tool accepts one optional field:

```json
{
  "args": ["--root", "C:\\Users\\owner\\Dropbox\\CCCoder\\lifeos"]
}
```

`args` is the exact argv tail you would pass after the CLI command. For
example, MCP `search` with `{"args": ["dream", "--top", "5"]}` is equivalent
to:

```powershell
life-os-tool search dream --top 5
```

The `cli` MCP tool is the generic dispatcher. Its first arg is the Life OS
subcommand:

```json
{
  "args": ["reindex", "--root", "C:\\Users\\owner\\Dropbox\\CCCoder\\lifeos"]
}
```

## Return Shape

Tools return a JSON-serializable object:

```json
{
  "ok": true,
  "command": "search",
  "args": ["dream", "--top", "5"],
  "exit_code": 0,
  "stdout": "...",
  "stderr": ""
}
```

Argparse errors, missing optional tool dependencies, and tool exceptions are
captured into `exit_code` and `stderr` instead of crashing the MCP process when
possible.

## Dependency Model

The wrapper is dependency-light:

- Importing `tools.mcp_server` uses only the Python standard library.
- Running the server requires the optional `mcp` Python package.
- If `mcp` is not installed, the script exits with a clear setup message.

Install the optional server dependency into the same Python environment used by
your MCP client. Either command is acceptable depending on how the environment
is managed:

```powershell
pip install mcp
uv pip install mcp
```

You can list the exposed tools without installing `mcp`:

```powershell
python tools\mcp_server.py --list-tools
```

## Client Configuration

Launch the server with stdio from the repo root. Example MCP client config:

```json
{
  "mcpServers": {
    "life-os": {
      "command": "python",
      "args": [
        "C:\\Users\\owner\\Dropbox\\CCCoder\\lifeos\\tools\\mcp_server.py"
      ],
      "cwd": "C:\\Users\\owner\\Dropbox\\CCCoder\\lifeos"
    }
  }
}
```

The server runs tools in-process with the same filesystem and environment
permissions as the MCP client. Use normal tool flags such as `--root`,
`--dry-run`, and output paths to control side effects.

## Cortex Config Boundary

The MCP wrapper should not introduce a second Cortex config location. Tools that
need user-editable settings read `_meta/config.md`; `_meta/cortex/` remains for
compiled/log artifacts such as `bootstrap-status.md` and `decay-log.md`.
