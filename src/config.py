"""Configuration management for File Oracle."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # NVIDIA API Configuration
    nvidia_api_key: str = Field(default="", description="NVIDIA API key")
    nvidia_api_base: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="NVIDIA API base URL",
    )
    nvidia_model: str = Field(
        default="nvidia/llama-3.1-nemotron-70b-instruct",
        description="Default NVIDIA model",
    )

    # OpenRouter API Configuration
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")
    openrouter_api_base: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL",
    )
    openrouter_model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="Default OpenRouter model",
    )

    # Default AI Provider
    default_ai_provider: Literal["nvidia", "openrouter"] = Field(
        default="nvidia",
        description="Default AI provider to use",
    )

    # File Oracle Configuration
    watch_directory: Path = Field(
        default=Path("./workspace"),
        description="Directory to watch for files",
    )
    output_directory: Path = Field(
        default=Path("./output"),
        description="Directory to save generated files",
    )
    auto_save: bool = Field(
        default=True,
        description="Automatically save generated/edited files",
    )
    max_file_size_mb: int = Field(
        default=10,
        description="Maximum file size to process in MB",
    )

    def get_api_key(self, provider: str | None = None) -> str:
        """Get API key for the specified provider."""
        provider = provider or self.default_ai_provider
        if provider == "nvidia":
            return self.nvidia_api_key
        elif provider == "openrouter":
            return self.openrouter_api_key
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_api_base(self, provider: str | None = None) -> str:
        """Get API base URL for the specified provider."""
        provider = provider or self.default_ai_provider
        if provider == "nvidia":
            return self.nvidia_api_base
        elif provider == "openrouter":
            return self.openrouter_api_base
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_model(self, provider: str | None = None) -> str:
        """Get default model for the specified provider."""
        provider = provider or self.default_ai_provider
        if provider == "nvidia":
            return self.nvidia_model
        elif provider == "openrouter":
            return self.openrouter_model
        else:
            raise ValueError(f"Unknown provider: {provider}")


# Global settings instance
settings = Settings()
