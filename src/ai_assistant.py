"""AI Assistant integration with NVIDIA and OpenRouter APIs."""

from typing import Any, Literal

from openai import AsyncOpenAI

from src.config import settings


class AIAssistant:
    """AI Assistant that can use NVIDIA or OpenRouter APIs."""

    def __init__(
        self,
        provider: Literal["nvidia", "openrouter"] | None = None,
        model: str | None = None,
    ):
        """Initialize the AI Assistant.

        Args:
            provider: AI provider to use (nvidia or openrouter)
            model: Model to use (provider-specific)
        """
        self.provider = provider or settings.default_ai_provider
        self.model = model or settings.get_model(self.provider)

        # Initialize OpenAI client with provider-specific settings
        api_key = settings.get_api_key(self.provider)
        api_base = settings.get_api_base(self.provider)

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base,
        )

    async def process_request(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Process a request using the AI assistant.

        Args:
            prompt: User prompt/request
            context: Additional context (e.g., file contents)
            system_prompt: System prompt to guide the assistant

        Returns:
            AI assistant response
        """
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant specialized in file processing "
                        "and code generation. You have access to file contents and can "
                        "help users analyze, modify, and generate files. Always provide "
                        "accurate and helpful responses."
                    ),
                }
            )

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            messages.append({"role": "system", "content": f"Context:\n{context_str}"})

        # Add user prompt
        messages.append({"role": "user", "content": prompt})

        # Call the API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )

        return response.choices[0].message.content or ""

    async def analyze_files(self, files_content: dict[str, str], question: str) -> str:
        """Analyze files and answer a question about them.

        Args:
            files_content: Dictionary mapping file paths to their contents
            question: Question to answer about the files

        Returns:
            AI assistant response
        """
        context = {"files": files_content}
        system_prompt = (
            "You are analyzing files. Provide detailed and accurate analysis "
            "based on the file contents provided in the context."
        )

        return await self.process_request(question, context, system_prompt)

    async def generate_code(
        self,
        description: str,
        language: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Generate code based on a description.

        Args:
            description: Description of what code to generate
            language: Programming language (optional)
            context: Additional context

        Returns:
            Generated code
        """
        prompt = f"Generate code: {description}"
        if language:
            prompt += f"\nLanguage: {language}"

        system_prompt = (
            "You are a code generation expert. Generate clean, well-documented, "
            "and efficient code based on the user's requirements. Only output the "
            "code without additional explanations unless specifically asked."
        )

        return await self.process_request(prompt, context, system_prompt)

    async def modify_file(
        self,
        file_content: str,
        modification_request: str,
        file_path: str | None = None,
    ) -> str:
        """Modify a file based on a request.

        Args:
            file_content: Current file content
            modification_request: What to modify
            file_path: Path to the file (for context)

        Returns:
            Modified file content
        """
        context = {"current_content": file_content}
        if file_path:
            context["file_path"] = file_path

        system_prompt = (
            "You are a file modification expert. Modify the file content based on "
            "the user's request. Return ONLY the complete modified file content, "
            "without any explanations or markdown formatting."
        )

        return await self.process_request(modification_request, context, system_prompt)

    async def execute_task(
        self,
        task_description: str,
        files_content: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Execute a task that may involve multiple files.

        Args:
            task_description: Description of the task to execute
            files_content: Available files and their contents

        Returns:
            Dictionary of files to create/modify with their contents
        """
        context = {}
        if files_content:
            context["available_files"] = files_content

        system_prompt = (
            "You are a task execution expert. Based on the task description and "
            "available files, determine what files need to be created or modified. "
            "Return your response in the following JSON format:\n"
            '{"files": {"path/to/file1.ext": "content1", "path/to/file2.ext": "content2"}}\n'
            "Only include the JSON object in your response."
        )

        response = await self.process_request(task_description, context, system_prompt)

        # Parse the response to extract files
        try:
            import json

            # Try to extract JSON from the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return result.get("files", {})
        except Exception:
            pass

        # If parsing fails, return empty dict
        return {}

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context dictionary into a readable string.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}:")
                    if isinstance(sub_value, str) and len(sub_value) > 500:
                        lines.append(f"    {sub_value[:500]}...")
                    else:
                        lines.append(f"    {sub_value}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    async def chat(self, message: str, history: list[dict[str, str]] | None = None) -> str:
        """Have a conversation with the AI assistant.

        Args:
            message: User message
            history: Conversation history

        Returns:
            AI assistant response
        """
        messages = []

        # Add system prompt
        messages.append(
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant for the File Oracle application. "
                    "You can help users with file processing, code generation, and "
                    "answering questions about their files."
                ),
            }
        )

        # Add history
        if history:
            messages.extend(history)

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call the API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )

        return response.choices[0].message.content or ""
