"""Tests for file writer module."""

import pytest
from pathlib import Path
import tempfile
import aiofiles

from src.file_writer import FileWriter


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.asyncio
async def test_write_file(temp_dir):
    """Test writing a single file."""
    writer = FileWriter(temp_dir)

    content = "Hello, World!"
    file_path = await writer.write_file("test.txt", content)

    assert file_path.exists()
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
        read_content = await f.read()
    assert read_content == content


@pytest.mark.asyncio
async def test_write_file_with_subdirectory(temp_dir):
    """Test writing a file in a subdirectory."""
    writer = FileWriter(temp_dir)

    content = "Test content"
    file_path = await writer.write_file("subdir/test.txt", content)

    assert file_path.exists()
    assert file_path.parent.name == "subdir"


@pytest.mark.asyncio
async def test_write_files(temp_dir):
    """Test writing multiple files."""
    writer = FileWriter(temp_dir)

    files = {
        "file1.txt": "Content 1",
        "file2.txt": "Content 2",
        "file3.txt": "Content 3",
    }

    written_files = await writer.write_files(files)

    assert len(written_files) == 3
    for original_path, written_path in written_files.items():
        assert written_path.exists()


@pytest.mark.asyncio
async def test_append_to_file(temp_dir):
    """Test appending to a file."""
    writer = FileWriter(temp_dir)

    # Write initial content
    file_path = await writer.write_file("test.txt", "Initial content\n")

    # Append more content
    await writer.append_to_file("test.txt", "Appended content\n")

    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
        content = await f.read()

    assert "Initial content" in content
    assert "Appended content" in content


@pytest.mark.asyncio
async def test_get_output_path(temp_dir):
    """Test getting output path."""
    writer = FileWriter(temp_dir)

    output_path = writer.get_output_path("test.txt")

    assert output_path == temp_dir / "test.txt"


@pytest.mark.asyncio
async def test_backup_file(temp_dir):
    """Test creating a backup of a file."""
    writer = FileWriter(temp_dir)

    # Create a file
    content = "Original content"
    file_path = await writer.write_file("test.txt", content)

    # Create backup
    backup_path = await writer.backup_file(file_path)

    assert backup_path.exists()
    assert backup_path.suffix == ".bak"

    async with aiofiles.open(backup_path, mode="r", encoding="utf-8") as f:
        backup_content = await f.read()

    assert backup_content == content


@pytest.mark.asyncio
async def test_auto_save_disabled(temp_dir):
    """Test that auto_save flag is respected."""
    writer = FileWriter(temp_dir, auto_save=False)

    assert writer.auto_save is False
