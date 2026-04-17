"""Main File Oracle orchestrator."""

from pathlib import Path
from typing import Any

from src.ai_assistant import AIAssistant
from src.config import settings
from src.file_reader import FileReader
from src.file_writer import FileWriter


class FileOracle:
    """Main orchestrator for the File Oracle application."""

    def __init__(
        self,
        watch_directory: Path | None = None,
        output_directory: Path | None = None,
        ai_provider: str | None = None,
        auto_save: bool | None = None,
    ):
        """Initialize the File Oracle.

        Args:
            watch_directory: Directory to watch for files
            output_directory: Directory to save generated files
            ai_provider: AI provider to use (nvidia or openrouter)
            auto_save: Automatically save generated files
        """
        self.watch_directory = watch_directory or settings.watch_directory
        self.output_directory = output_directory or settings.output_directory
        self.auto_save = auto_save if auto_save is not None else settings.auto_save

        # Initialize components
        self.reader = FileReader(self.watch_directory, settings.max_file_size_mb)
        self.writer = FileWriter(self.output_directory, self.auto_save)
        self.assistant = AIAssistant(provider=ai_provider)

    async def read_files(self, pattern: str = "*") -> dict[str, str]:
        """Read all files matching the pattern.

        Args:
            pattern: Glob pattern to match files

        Returns:
            Dictionary mapping file paths to their contents
        """
        return await self.reader.read_directory(pattern)

    async def process_request(
        self,
        request: str,
        include_files: bool = True,
        file_pattern: str = "*",
    ) -> str:
        """Process a user request with AI assistance.

        Args:
            request: User request/question
            include_files: Include file contents as context
            file_pattern: Pattern to match files for context

        Returns:
            AI assistant response
        """
        context = None

        if include_files:
            files_content = await self.read_files(file_pattern)
            if files_content:
                context = {"files": files_content}

        return await self.assistant.process_request(request, context)

    async def analyze_files(self, question: str, pattern: str = "*") -> str:
        """Analyze files and answer a question.

        Args:
            question: Question to answer about the files
            pattern: Pattern to match files

        Returns:
            AI assistant response
        """
        files_content = await self.read_files(pattern)
        return await self.assistant.analyze_files(files_content, question)

    async def generate_file(
        self,
        description: str,
        filename: str,
        language: str | None = None,
    ) -> Path:
        """Generate a new file based on a description.

        Args:
            description: Description of what to generate
            filename: Name for the generated file
            language: Programming language (optional)

        Returns:
            Path to the generated file
        """
        # Get context from existing files
        files_content = await self.read_files()
        context = {"existing_files": list(files_content.keys())} if files_content else None

        # Generate content
        content = await self.assistant.generate_code(description, language, context)

        # Save the file
        if self.auto_save:
            return await self.writer.write_file(filename, content)
        else:
            return Path(filename)

    async def modify_file(
        self,
        file_path: str,
        modification_request: str,
        save_as: str | None = None,
    ) -> Path:
        """Modify an existing file.

        Args:
            file_path: Path to the file to modify
            modification_request: What to modify
            save_as: Optional new filename (default: overwrite original)

        Returns:
            Path to the modified file
        """
        # Read the file
        file_path_obj = Path(file_path)
        if not file_path_obj.is_absolute():
            file_path_obj = self.watch_directory / file_path_obj

        content = await self.reader.read_file(file_path_obj)

        # Modify the content
        modified_content = await self.assistant.modify_file(
            content, modification_request, str(file_path_obj)
        )

        # Save the modified file
        output_filename = save_as or file_path_obj.name
        if self.auto_save:
            return await self.writer.write_file(output_filename, modified_content)
        else:
            return Path(output_filename)

    async def execute_task(self, task_description: str) -> dict[str, Path]:
        """Execute a complex task that may involve multiple files.

        Args:
            task_description: Description of the task

        Returns:
            Dictionary mapping filenames to their paths
        """
        # Get context from existing files
        files_content = await self.read_files()

        # Execute the task
        files_to_create = await self.assistant.execute_task(task_description, files_content)

        # Save the files
        if self.auto_save and files_to_create:
            return await self.writer.write_files(files_to_create)
        else:
            return {name: Path(name) for name in files_to_create.keys()}

    async def chat(self, message: str, history: list[dict[str, str]] | None = None) -> str:
        """Chat with the AI assistant.

        Args:
            message: User message
            history: Conversation history

        Returns:
            AI assistant response
        """
        return await self.assistant.chat(message, history)

    def list_files(self, pattern: str = "*") -> list[Path]:
        """List all files in the watch directory.

        Args:
            pattern: Pattern to match files

        Returns:
            List of file paths
        """
        return self.reader.list_files(pattern)

    async def get_file_info(self, file_path: str) -> dict[str, Any]:
        """Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.is_absolute():
            file_path_obj = self.watch_directory / file_path_obj

        return await self.reader.get_file_info(file_path_obj)
