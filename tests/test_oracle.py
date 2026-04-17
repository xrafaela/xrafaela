"""Tests for File Oracle orchestrator."""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

from src.oracle import FileOracle


@pytest.fixture
async def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as watch_dir, tempfile.TemporaryDirectory() as output_dir:
        yield Path(watch_dir), Path(output_dir)


@pytest.fixture
def mock_assistant():
    """Create a mock AI assistant."""
    with patch("src.oracle.AIAssistant") as mock:
        assistant = MagicMock()
        assistant.process_request = AsyncMock(return_value="Mock response")
        assistant.analyze_files = AsyncMock(return_value="Mock analysis")
        assistant.generate_code = AsyncMock(return_value="# Mock code")
        assistant.modify_file = AsyncMock(return_value="Modified content")
        assistant.execute_task = AsyncMock(return_value={"test.txt": "Test content"})
        assistant.chat = AsyncMock(return_value="Mock chat response")
        mock.return_value = assistant
        yield assistant


@pytest.mark.asyncio
async def test_oracle_initialization(temp_dirs):
    """Test File Oracle initialization."""
    watch_dir, output_dir = temp_dirs

    oracle = FileOracle(watch_directory=watch_dir, output_directory=output_dir)

    assert oracle.watch_directory == watch_dir
    assert oracle.output_directory == output_dir
    assert oracle.reader is not None
    assert oracle.writer is not None
    assert oracle.assistant is not None


@pytest.mark.asyncio
async def test_list_files(temp_dirs):
    """Test listing files."""
    watch_dir, output_dir = temp_dirs

    # Create some test files
    (watch_dir / "test1.txt").write_text("Test 1")
    (watch_dir / "test2.txt").write_text("Test 2")

    oracle = FileOracle(watch_directory=watch_dir, output_directory=output_dir)
    files = oracle.list_files()

    assert len(files) == 2
    assert all(f.suffix == ".txt" for f in files)


@pytest.mark.asyncio
async def test_read_files(temp_dirs):
    """Test reading files."""
    watch_dir, output_dir = temp_dirs

    # Create test files
    (watch_dir / "test.txt").write_text("Test content")

    oracle = FileOracle(watch_directory=watch_dir, output_directory=output_dir)
    files_content = await oracle.read_files()

    assert len(files_content) > 0
    assert any("Test content" in content for content in files_content.values())


@pytest.mark.asyncio
async def test_process_request(temp_dirs, mock_assistant):
    """Test processing a request."""
    watch_dir, output_dir = temp_dirs

    oracle = FileOracle(watch_directory=watch_dir, output_directory=output_dir)
    oracle.assistant = mock_assistant

    response = await oracle.process_request("Test request")

    assert response == "Mock response"
    mock_assistant.process_request.assert_called_once()


@pytest.mark.asyncio
async def test_chat(temp_dirs, mock_assistant):
    """Test chat functionality."""
    watch_dir, output_dir = temp_dirs

    oracle = FileOracle(watch_directory=watch_dir, output_directory=output_dir)
    oracle.assistant = mock_assistant

    response = await oracle.chat("Hello")

    assert response == "Mock chat response"
    mock_assistant.chat.assert_called_once()
