"""Filesystem platform-specific data models."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from prompt_pidgeon.models.core import Prompt


class FilesystemPrompt(BaseModel):
    """Filesystem prompt model for local file storage with metadata."""

    filename: str = Field(..., description="Generated filename (without extension)")
    content: str = Field(..., description="Prompt content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata to preserve in frontmatter")
    file_extension: str = Field(default="md", description="File extension")

    @classmethod
    def from_universal_prompt(cls, prompt: Prompt) -> "FilesystemPrompt":
        """Create filesystem prompt from universal Prompt."""
        # Generate filename from prompt name
        filename = prompt.name.lower().replace(" ", "-").replace("_", "-")

        # Preserve all metadata from universal prompt
        metadata = {
            "id": prompt.id,
            "name": prompt.name,
            "tags": prompt.tags,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat(),
            "version": prompt.version,
            "source_platform": prompt.source_platform,
            "source_id": prompt.source_id,
            **prompt.metadata,  # Include any additional platform-specific metadata
        }

        return cls(filename=filename, content=prompt.content, metadata=metadata, file_extension="md")

    def generate_frontmatter(self) -> str:
        """Generate YAML frontmatter for metadata preservation."""
        if not self.metadata:
            return ""

        lines = ["---"]

        # Handle different data types in metadata
        for key, value in self.metadata.items():
            if isinstance(value, str):
                lines.append(f'{key}: "{value}"')
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f'  - "{item}"')
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str):
                        lines.append(f'  {subkey}: "{subvalue}"')
                    else:
                        lines.append(f"  {subkey}: {subvalue}")
            else:
                lines.append(f"{key}: {value}")

        lines.append("---")
        return "\n".join(lines)

    def generate_full_content(self) -> str:
        """Generate the complete file content with frontmatter."""
        frontmatter = self.generate_frontmatter()
        if frontmatter:
            return f"{frontmatter}\n\n{self.content}"
        return self.content

    def get_file_path(self, base_path: Path) -> Path:
        """Get the full file path for this filesystem prompt."""
        return base_path / f"{self.filename}.{self.file_extension}"


class FilesystemSinkConfig(BaseModel):
    """Configuration for filesystem as a sink."""

    name: str = Field(..., description="Sink name identifier")
    type: str = Field(default="filesystem", description="Sink type")
    enabled: bool = Field(default=True, description="Whether this sink is enabled")
    path: Path = Field(..., description="Base directory path for storing prompts")

    # File organization
    create_subdirectories: bool = Field(default=False, description="Create subdirectories based on tags")
    subdirectory_tag: str | None = Field(None, description="Specific tag to use for subdirectory creation")
    file_extension: str = Field(default="md", description="File extension for prompt files")

    # Metadata handling
    include_frontmatter: bool = Field(default=True, description="Include YAML frontmatter with metadata")
    preserve_timestamps: bool = Field(default=True, description="Preserve original timestamps in metadata")

    # File management
    overwrite_existing: bool = Field(default=True, description="Whether to overwrite existing files")
    backup_existing: bool = Field(default=False, description="Create backup of existing files before overwrite")

    # Git integration
    git_integration: bool = Field(default=False, description="Enable Git integration")
    auto_commit: bool = Field(default=False, description="Automatically commit changes")
    commit_message_template: str = Field(
        default="Update prompts via prompt-pidgeon sync", description="Template for commit messages"
    )

    def get_prompt_path(self, prompt: Prompt, filesystem_prompt: FilesystemPrompt) -> Path:
        """Get the full path for storing a prompt, including subdirectories if configured."""
        base_path = self.path

        # Create subdirectories based on configuration
        if self.create_subdirectories:
            if self.subdirectory_tag and prompt.has_tag(self.subdirectory_tag):
                # Use specific tag for subdirectory
                subdir = self.subdirectory_tag
            elif prompt.tags:
                # Use first tag for subdirectory
                subdir = prompt.tags[0]
            else:
                # Use 'untagged' for prompts without tags
                subdir = "untagged"

            base_path = base_path / subdir

        return filesystem_prompt.get_file_path(base_path)


class GitConfig(BaseModel):
    """Configuration for Git integration."""

    enabled: bool = Field(default=False, description="Enable Git operations")
    auto_add: bool = Field(default=True, description="Automatically add files to Git")
    auto_commit: bool = Field(default=False, description="Automatically commit changes")
    commit_message: str = Field(default="Update prompts via prompt-pidgeon", description="Commit message")
    author_name: str | None = Field(None, description="Git author name override")
    author_email: str | None = Field(None, description="Git author email override")
