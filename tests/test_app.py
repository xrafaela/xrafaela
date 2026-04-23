from __future__ import annotations

from pathlib import Path

import pytest

from src.app import FileOracle


class AssistantObject:
    def answer(self, question: str, files: dict[str, str]) -> str:
        return f"{question}|{len(files)}"


def test_list_and_read_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.md").write_text("world")

    oracle = FileOracle(tmp_path)

    assert oracle.list_files() == ["a.txt", "nested/b.md"]
    assert oracle.read_file("a.txt") == "hello"


def test_read_file_blocks_path_traversal(tmp_path: Path) -> None:
    oracle = FileOracle(tmp_path)

    with pytest.raises(ValueError):
        oracle.read_file("../outside.txt")


def test_ask_with_callable_assistant(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("copilot helps")

    def assistant(question: str, files: dict[str, str]) -> str:
        return f"Q={question};F={sorted(files)}"

    oracle = FileOracle(tmp_path, assistant=assistant)

    assert oracle.ask("what is here?") == "Q=what is here?;F=['notes.txt']"


def test_ask_with_object_assistant(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("copilot helps")
    oracle = FileOracle(tmp_path, assistant=AssistantObject())

    assert oracle.ask("count") == "count|1"


def test_ask_without_assistant_returns_fallback_context(tmp_path: Path) -> None:
    (tmp_path / "doc.txt").write_text("example content")
    oracle = FileOracle(tmp_path)

    answer = oracle.ask("summarize")

    assert "Question: summarize" in answer
    assert "doc.txt" in answer
    assert "example content" in answer


def test_file_size_guard(tmp_path: Path) -> None:
    (tmp_path / "big.txt").write_text("x" * 11)
    oracle = FileOracle(tmp_path, max_file_size=10)

    with pytest.raises(ValueError):
        oracle.read_file("big.txt")
