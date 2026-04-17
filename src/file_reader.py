"""File reading and processing utilities."""

import asyncio
from pathlib import Path
from typing import Any

import aiofiles


class FileReader:
    """Handles reading and processing files from a directory."""

    def __init__(self, directory: Path, max_size_mb: int = 10):
        """Initialize the file reader.

        Args:
            directory: Directory to read files from
            max_size_mb: Maximum file size to process in MB
        """
        self.directory = Path(directory)
        self.max_size_bytes = max_size_mb * 1024 * 1024

    async def read_file(self, file_path: Path) -> str:
        """Read a single file asynchronously.

        Args:
            file_path: Path to the file to read

        Returns:
            File content as string

        Raises:
            ValueError: If file is too large
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        if file_size > self.max_size_bytes:
            raise ValueError(
                f"File too large: {file_size / 1024 / 1024:.2f}MB "
                f"(max: {self.max_size_bytes / 1024 / 1024:.2f}MB)"
            )

        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            return await f.read()

    async def read_directory(self, pattern: str = "*") -> dict[str, str]:
        """Read all files in the directory matching the pattern.

        Args:
            pattern: Glob pattern to match files (default: all files)

        Returns:
            Dictionary mapping file paths to their contents
        """
        files_content: dict[str, str] = {}

        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)
            return files_content

        # Get all matching files
        file_paths = list(self.directory.glob(pattern))

        # Read files concurrently
        tasks = []
        for file_path in file_paths:
            if file_path.is_file():
                tasks.append(self._read_file_safe(file_path))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for file_path, result in zip(file_paths, results):
            if isinstance(result, Exception):
                files_content[str(file_path)] = f"Error reading file: {result}"
            else:
                files_content[str(file_path)] = result

        return files_content

    async def _read_file_safe(self, file_path: Path) -> str:
        """Safely read a file, handling errors gracefully."""
        try:
            return await self.read_file(file_path)
        except Exception as e:
            return f"Error: {e}"

    def list_files(self, pattern: str = "*") -> list[Path]:
        """List all files in the directory matching the pattern.

        Args:
            pattern: Glob pattern to match files

        Returns:
            List of file paths
        """
        if not self.directory.exists():
            return []

        return [p for p in self.directory.glob(pattern) if p.is_file()]

    async def get_file_info(self, file_path: Path) -> dict[str, Any]:
        """Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": stat.st_size,
            "size_mb": stat.st_size / 1024 / 1024,
            "modified": stat.st_mtime,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "suffix": file_path.suffix,
        }
