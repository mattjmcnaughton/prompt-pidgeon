"""Data models for prompt-pidgeon."""

# Core models
# Configuration models
from prompt_pidgeon.models.config import (
    ConfigManager,
    EnvironmentSettings,
    PidgeonConfig,
    SyncJobConfig,
)
from prompt_pidgeon.models.core import Prompt, SyncScope, TagFilter
from prompt_pidgeon.models.platforms.coding_assistants import (
    ClaudeCodePrompt,
    CodingAssistantSinkConfig,
    CursorPrompt,
)
from prompt_pidgeon.models.platforms.filesystem import (
    FilesystemPrompt,
    FilesystemSinkConfig,
    GitConfig,
)

# Platform-specific models
from prompt_pidgeon.models.platforms.langfuse import (
    LangfuseCredentials,
    LangfusePrompt,
    LangfuseSourceConfig,
)
from prompt_pidgeon.models.platforms.openwebui import (
    OpenWebUICredentials,
    OpenWebUIModel,
    OpenWebUISinkConfig,
    OpenWebUIUserPrompt,
)

__all__ = [
    # Core
    "Prompt",
    "TagFilter",
    "SyncScope",
    # Langfuse
    "LangfusePrompt",
    "LangfuseCredentials",
    "LangfuseSourceConfig",
    # Open-WebUI
    "OpenWebUIUserPrompt",
    "OpenWebUIModel",
    "OpenWebUICredentials",
    "OpenWebUISinkConfig",
    # Coding Assistants
    "ClaudeCodePrompt",
    "CursorPrompt",
    "CodingAssistantSinkConfig",
    # Filesystem
    "FilesystemPrompt",
    "FilesystemSinkConfig",
    "GitConfig",
    # Configuration
    "PidgeonConfig",
    "SyncJobConfig",
    "EnvironmentSettings",
    "ConfigManager",
]
