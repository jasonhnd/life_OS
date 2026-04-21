"""Verify the public import surface of tools.lib.cortex package.

Catches regressions where __init__.py exports drift out of sync with
submodule contents (added function not exported, removed function still
exported, etc).
"""

from __future__ import annotations

import pytest


# ─── tools.lib.cortex package-level imports ────────────────────────────────


class TestCortexPackageExports:
    def test_all_session_symbols_importable(self):
        from tools.lib.cortex import (
            compile_index,
            compile_index_line,
            rebuild_index,
            session_summary_to_markdown,
            truncate_subject,
            write_index,
            write_session_summary,
        )
        # Sanity: each is callable
        for fn in (
            compile_index,
            compile_index_line,
            rebuild_index,
            session_summary_to_markdown,
            truncate_subject,
            write_index,
            write_session_summary,
        ):
            assert callable(fn), f"{fn.__name__} not callable"

    def test_all_concept_symbols_importable(self):
        from tools.lib.cortex import (
            compile_concept_index,
            compile_concept_index_line,
            compile_synapses_index,
            concept_to_markdown,
            hebbian_update,
            read_concept,
            rebuild_concept_index,
            write_concept,
        )
        for fn in (
            compile_concept_index,
            compile_concept_index_line,
            compile_synapses_index,
            concept_to_markdown,
            hebbian_update,
            read_concept,
            rebuild_concept_index,
            write_concept,
        ):
            assert callable(fn), f"{fn.__name__} not callable"

    def test_all_snapshot_symbols_importable(self):
        from tools.lib.cortex import (
            find_latest_snapshot,
            find_previous_snapshot,
            list_active_snapshots,
            list_archive_snapshots,
            should_archive,
            should_delete,
            snapshot_to_markdown,
            write_snapshot,
        )
        for fn in (
            find_latest_snapshot,
            find_previous_snapshot,
            list_active_snapshots,
            list_archive_snapshots,
            should_archive,
            should_delete,
            snapshot_to_markdown,
            write_snapshot,
        ):
            assert callable(fn), f"{fn.__name__} not callable"

    def test_all_exports_in_dunder_all(self):
        """Every symbol in __all__ should be importable from the package."""
        import tools.lib.cortex as cortex_pkg

        for name in cortex_pkg.__all__:
            assert hasattr(cortex_pkg, name), (
                f"{name} in __all__ but not actually exported"
            )

    def test_no_unexpected_extras(self):
        """Top-level symbols (excluding _private + submodules) should match __all__."""
        import tools.lib.cortex as cortex_pkg

        # Submodule names are accessible as attrs but not part of the public API
        SUBMODULES = {"session_index", "concept", "snapshot", "extraction"}
        public_attrs = {
            name
            for name in dir(cortex_pkg)
            if not name.startswith("_") and name not in SUBMODULES
        }
        unexpected = public_attrs - set(cortex_pkg.__all__)
        assert not unexpected, f"Public attrs not in __all__: {unexpected}"


# ─── tools.lib.second_brain package-level imports ───────────────────────────


class TestSecondBrainImports:
    def test_all_dataclasses_importable(self):
        from tools.lib.second_brain import (
            ActionItem,
            Concept,
            ConceptEdge,
            ConceptProvenance,
            EvalEntry,
            Method,
            ParsedMarkdown,
            SecondBrainEntity,
            SessionSummary,
            SnapshotDimension,
            SoulSnapshot,
            WikiNote,
        )
        # Verify all are actually classes (dataclasses)
        from dataclasses import is_dataclass

        for cls in (
            ActionItem,
            Concept,
            ConceptEdge,
            ConceptProvenance,
            EvalEntry,
            Method,
            ParsedMarkdown,
            SecondBrainEntity,
            SessionSummary,
            SnapshotDimension,
            SoulSnapshot,
            WikiNote,
        ):
            assert is_dataclass(cls), f"{cls.__name__} not a dataclass"

    def test_helper_functions_importable(self):
        from tools.lib.second_brain import (
            dump_frontmatter,
            load_markdown,
            parse_frontmatter,
            resolve_path,
        )
        for fn in (dump_frontmatter, load_markdown, parse_frontmatter, resolve_path):
            assert callable(fn)
