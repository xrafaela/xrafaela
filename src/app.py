from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol, runtime_checkable

MAX_SNIPPET_LENGTH = 120


@runtime_checkable
class AssistantProtocol(Protocol):
    """Contract for assistant objects used by FileOracle."""

    def answer(self, question: str, files: dict[str, str]) -> str:  # pragma: no cover - protocol
        ...


class FileOracle:
    """Oráculo de Ficheiros with optional AI assistant integration."""

    def __init__(
        self,
        root_path: str | Path,
        assistant: AssistantProtocol | Callable[[str, dict[str, str]], str] | None = None,
        *,
        max_file_size: int = 1_000_000,
    ) -> None:
        self.root_path = Path(root_path).resolve()
        self.assistant = assistant
        self.max_file_size = max_file_size

    def list_files(self, *, recursive: bool = True) -> list[str]:
        """Return visible files relative to the oracle root."""
        pattern = "**/*" if recursive else "*"
        files = [
            str(path.relative_to(self.root_path))
            for path in self.root_path.glob(pattern)
            if path.is_file()
        ]
        return sorted(files)

    def read_file(self, file_path: str | Path, *, encoding: str = "utf-8") -> str:
        """Read a file below root_path with traversal and size guards."""
        path = self._resolve_under_root(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.stat().st_size > self.max_file_size:
            raise ValueError(f"File exceeds max size: {file_path}")

        return path.read_text(encoding=encoding)

    def ask(self, question: str, *, files: list[str] | None = None) -> str:
        """Answer a question using selected files and an optional assistant."""
        selected_files = files or self.list_files()
        context: dict[str, str] = {
            file_name: self.read_file(file_name) for file_name in selected_files
        }

        if self.assistant is None:
            return self._fallback_answer(question, context)

        if hasattr(self.assistant, "answer") and callable(self.assistant.answer):
            return self.assistant.answer(question, context)

        if callable(self.assistant):
            return self.assistant(question, context)

        raise TypeError("assistant must be callable or implement answer(question, files)")

    def _resolve_under_root(self, file_path: str | Path) -> Path:
        candidate = (self.root_path / file_path).resolve()
        if self.root_path != candidate and self.root_path not in candidate.parents:
            raise ValueError(f"Path outside oracle root: {file_path}")
        return candidate

    @staticmethod
    def _fallback_answer(question: str, files: dict[str, str]) -> str:
        if not files:
            return f"Question: {question}\nNo files available for analysis."

        file_list = ", ".join(sorted(files.keys()))
        snippets = "\n".join(
            f"[{name}] {content[:MAX_SNIPPET_LENGTH].strip()}"
            for name, content in sorted(files.items())
        )
        return f"Question: {question}\nFiles: {file_list}\nContext:\n{snippets}"
