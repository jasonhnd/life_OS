from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def load_module() -> Any:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "translate-i18n.py"
    spec = importlib.util.spec_from_file_location("translate_i18n", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_glossary(root: Path) -> None:
    glossary_path = root / "scripts" / "i18n-glossary.yaml"
    glossary_path.parent.mkdir(parents=True)
    glossary_path.write_text(
        """
terms:
  Cortex:
    zh: Cortex
    ja: Cortex
  Life OS:
    zh: Life OS
    ja: Life OS
  三省六部:
    zh: 三省六部
    ja: 三省六部
""".lstrip(),
        encoding="utf-8",
    )


class FakeClient:
    def __init__(self, *, fail_on_call: int | None = None) -> None:
        self.fail_on_call = fail_on_call
        self.calls: list[dict[str, Any]] = []

    def translate_chunk(
        self,
        *,
        source_name: str,
        chunk: str,
        target_language: str,
        glossary: dict[str, dict[str, str]],
        chunk_number: int,
        chunk_count: int,
    ) -> str:
        self.calls.append(
            {
                "source_name": source_name,
                "chunk": chunk,
                "target_language": target_language,
                "glossary": glossary,
                "chunk_number": chunk_number,
                "chunk_count": chunk_count,
            }
        )
        if self.fail_on_call == len(self.calls):
            module = sys.modules["translate_i18n"]
            raise module.TranslationError("mocked API failure")
        return f"{target_language}: {source_name}: {chunk}"


def test_load_glossary_contains_required_life_os_terms() -> None:
    module = load_module()
    glossary = module.load_glossary()
    required_terms = {
        "Cortex",
        "SKILL",
        "Life OS",
        "Hippocampus",
        "GWT",
        "Narrator",
        "三省六部",
        "ROUTER",
        "ADVISOR",
        "RETROSPECTIVE",
        "Second Brain",
        "Skill Observability",
    }
    assert required_terms <= set(glossary)
    for term in required_terms:
        assert glossary[term]["zh"] == term
        assert glossary[term]["ja"] == term


def test_missing_api_key_exits_2_and_does_not_write(tmp_path: Path, capsys: Any) -> None:
    module = load_module()
    write_glossary(tmp_path)
    (tmp_path / "README.md").write_text("Hello Life OS\n", encoding="utf-8")
    zh_output = tmp_path / "i18n" / "zh" / "README.md"
    ja_output = tmp_path / "i18n" / "ja" / "README.md"
    zh_output.parent.mkdir(parents=True)
    ja_output.parent.mkdir(parents=True)
    zh_output.write_text("old zh\n", encoding="utf-8")
    ja_output.write_text("old ja\n", encoding="utf-8")

    result = module.run(["README.md"], root=tmp_path, env={})

    captured = capsys.readouterr()
    assert result == 2
    assert "CLAUDE_API_KEY is required" in captured.err
    assert zh_output.read_text(encoding="utf-8") == "old zh\n"
    assert ja_output.read_text(encoding="utf-8") == "old ja\n"


def test_successful_translation_writes_both_languages(tmp_path: Path) -> None:
    module = load_module()
    write_glossary(tmp_path)
    (tmp_path / "README.md").write_text("Hello Life OS\n", encoding="utf-8")
    client = FakeClient()

    result = module.run(
        ["README.md"],
        root=tmp_path,
        env={"CLAUDE_API_KEY": "test-key"},
        client_factory=lambda _env: client,
    )

    assert result == 0
    assert (tmp_path / "i18n" / "zh" / "README.md").read_text(encoding="utf-8") == (
        "Simplified Chinese: README.md: Hello Life OS\n"
    )
    assert (tmp_path / "i18n" / "ja" / "README.md").read_text(encoding="utf-8") == (
        "Japanese: README.md: Hello Life OS\n"
    )
    assert [call["target_language"] for call in client.calls] == [
        "Simplified Chinese",
        "Japanese",
    ]


def test_failed_second_translation_does_not_partially_overwrite(tmp_path: Path) -> None:
    module = load_module()
    write_glossary(tmp_path)
    (tmp_path / "README.md").write_text("Hello Life OS\n", encoding="utf-8")
    zh_output = tmp_path / "i18n" / "zh" / "README.md"
    ja_output = tmp_path / "i18n" / "ja" / "README.md"
    zh_output.parent.mkdir(parents=True)
    ja_output.parent.mkdir(parents=True)
    zh_output.write_text("old zh\n", encoding="utf-8")
    ja_output.write_text("old ja\n", encoding="utf-8")
    client = FakeClient(fail_on_call=2)

    result = module.run(
        ["README.md"],
        root=tmp_path,
        env={"CLAUDE_API_KEY": "test-key"},
        client_factory=lambda _env: client,
    )

    assert result == 1
    assert zh_output.read_text(encoding="utf-8") == "old zh\n"
    assert ja_output.read_text(encoding="utf-8") == "old ja\n"
