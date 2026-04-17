"""Tests for file reader module."""

import pytest
from pathlib import Path
import tempfile
import aiofiles

from src.file_reader import FileReader


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
async def sample_files(temp_dir):
    """Create sample files for testing."""
    files = {
        "test1.txt": "Hello, World!",
        "test2.txt": "This is a test file.",
        "test3.py": "print('Hello from Python')",
    }

    for filename, content in files.items():
        file_path = temp_dir / filename
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)

    return files


@pytest.mark.asyncio
async def test_read_file(temp_dir, sample_files):
    """Test reading a single file."""
    reader = FileReader(temp_dir)
    file_path = temp_dir / "test1.txt"

    content = await reader.read_file(file_path)
    assert content == "Hello, World!"


@pytest.mark.asyncio
async def test_read_file_not_found(temp_dir):
    """Test reading a non-existent file."""
    reader = FileReader(temp_dir)
    file_path = temp_dir / "nonexistent.txt"

    with pytest.raises(FileNotFoundError):
        await reader.read_file(file_path)


@pytest.mark.asyncio
async def test_read_directory(temp_dir, sample_files):
    """Test reading all files in a directory."""
    reader = FileReader(temp_dir)

    files_content = await reader.read_directory()

    assert len(files_content) == 3
    assert any("Hello, World!" in content for content in files_content.values())


@pytest.mark.asyncio
async def test_read_directory_with_pattern(temp_dir, sample_files):
    """Test reading files matching a pattern."""
    reader = FileReader(temp_dir)

    files_content = await reader.read_directory("*.txt")

    assert len(files_content) == 2
    assert all(str(path).endswith(".txt") for path in files_content.keys())


@pytest.mark.asyncio
async def test_list_files(temp_dir, sample_files):
    """Test listing files in a directory."""
    reader = FileReader(temp_dir)

    files = reader.list_files()

    assert len(files) == 3
    assert all(isinstance(f, Path) for f in files)


@pytest.mark.asyncio
async def test_get_file_info(temp_dir, sample_files):
    """Test getting file information."""
    reader = FileReader(temp_dir)
    file_path = temp_dir / "test1.txt"

    info = await reader.get_file_info(file_path)

    assert info["name"] == "test1.txt"
    assert info["is_file"] is True
    assert info["suffix"] == ".txt"
    assert info["size"] > 0


@pytest.mark.asyncio
async def test_max_file_size(temp_dir):
    """Test maximum file size limit."""
    reader = FileReader(temp_dir, max_size_mb=0.001)  # Very small limit

    # Create a file larger than the limit
    large_file = temp_dir / "large.txt"
    async with aiofiles.open(large_file, mode="w", encoding="utf-8") as f:
        await f.write("x" * 2000)  # 2KB file

    with pytest.raises(ValueError, match="File too large"):
        await reader.read_file(large_file)
