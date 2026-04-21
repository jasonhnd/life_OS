"""Life OS Cortex helpers — v1.7 Phase 1.

Read/write helpers for the v1.7 Cortex layer artifacts:
- _meta/sessions/ (SessionSummary + INDEX.md)
- _meta/concepts/ (Concept files + INDEX.md + SYNAPSES-INDEX.md)
- _meta/snapshots/soul/ (SoulSnapshot files + archive policy)

Used by:
- archiver Phase 2 (write SessionSummary, Concept, SoulSnapshot)
- retrospective Mode 0 (compile INDEX.md files)
- tools/rebuild_*.py CLIs (manual recompile)
- AUDITOR Mode 3 + check_cortex (read for compliance)

See references/cortex-spec.md for architecture and per-component specs:
- references/session-index-spec.md
- references/concept-spec.md
- references/snapshot-spec.md
- references/hippocampus-spec.md (consumer)
- references/gwt-spec.md (consumer)
"""

from tools.lib.cortex.concept import (
    compile_concept_index,
    compile_concept_index_line,
    compile_synapses_index,
    concept_to_markdown,
    hebbian_update,
    read_concept,
    rebuild_concept_index,
    write_concept,
)
from tools.lib.cortex.session_index import (
    compile_index,
    compile_index_line,
    rebuild_index,
    session_summary_to_markdown,
    truncate_subject,
    write_index,
    write_session_summary,
)
from tools.lib.cortex.snapshot import (
    find_latest_snapshot,
    find_previous_snapshot,
    list_active_snapshots,
    list_archive_snapshots,
    should_archive,
    should_delete,
    snapshot_to_markdown,
    write_snapshot,
)

__all__ = [
    # Session helpers
    "compile_index",
    "compile_index_line",
    "rebuild_index",
    "session_summary_to_markdown",
    "truncate_subject",
    "write_index",
    "write_session_summary",
    # Concept helpers
    "compile_concept_index",
    "compile_concept_index_line",
    "compile_synapses_index",
    "concept_to_markdown",
    "hebbian_update",
    "read_concept",
    "rebuild_concept_index",
    "write_concept",
    # Snapshot helpers
    "find_latest_snapshot",
    "find_previous_snapshot",
    "list_active_snapshots",
    "list_archive_snapshots",
    "should_archive",
    "should_delete",
    "snapshot_to_markdown",
    "write_snapshot",
]
