"""File writing and saving utilities."""

import asyncio
from pathlib import Path
from typing import Any

import aiofiles


class FileWriter:
    """Handles writing and saving files to a directory."""

    def __init__(self, directory: Path, auto_save: bool = True):
        """Initialize the file writer.

        Args:
            directory: Directory to write files to
            auto_save: Automatically save files when requested
        """
        self.directory = Path(directory)
        self.auto_save = auto_save
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure the output directory exists."""
        self.directory.mkdir(parents=True, exist_ok=True)

    async def write_file(self, file_path: Path | str, content: str) -> Path:
        """Write content to a file asynchronously.

        Args:
            file_path: Path to the file (relative to output directory or absolute)
            content: Content to write

        Returns:
            Path to the written file
        """
        file_path = Path(file_path)

        # If relative path, make it relative to output directory
        if not file_path.is_absolute():
            file_path = self.directory / file_path

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)

        return file_path

    async def write_files(self, files: dict[str, str]) -> dict[str, Path]:
        """Write multiple files concurrently.

        Args:
            files: Dictionary mapping file paths to their contents

        Returns:
            Dictionary mapping original paths to written file paths
        """
        tasks = []
        file_paths = []

        for file_path, content in files.items():
            tasks.append(self.write_file(file_path, content))
            file_paths.append(file_path)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        written_files: dict[str, Path] = {}
        for original_path, result in zip(file_paths, results):
            if isinstance(result, Exception):
                written_files[original_path] = Path(f"Error: {result}")
            else:
                written_files[original_path] = result

        return written_files

    async def append_to_file(self, file_path: Path | str, content: str) -> Path:
        """Append content to a file.

        Args:
            file_path: Path to the file
            content: Content to append

        Returns:
            Path to the file
        """
        file_path = Path(file_path)

        if not file_path.is_absolute():
            file_path = self.directory / file_path

        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="a", encoding="utf-8") as f:
            await f.write(content)

        return file_path

    def get_output_path(self, filename: str) -> Path:
        """Get the full output path for a filename.

        Args:
            filename: Name of the file

        Returns:
            Full path to the output file
        """
        return self.directory / filename

    async def backup_file(self, file_path: Path) -> Path:
        """Create a backup of a file.

        Args:
            file_path: Path to the file to backup

        Returns:
            Path to the backup file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        backup_path = file_path.with_suffix(file_path.suffix + ".bak")

        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as src:
            content = await src.read()

        async with aiofiles.open(backup_path, mode="w", encoding="utf-8") as dst:
            await dst.write(content)

        return backup_path
