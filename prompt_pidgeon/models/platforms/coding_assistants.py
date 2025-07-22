"""Coding assistant platform-specific data models."""

from pathlib import Path

from pydantic import BaseModel, Field

from prompt_pidgeon.models.core import Prompt, SyncScope


class ClaudeCodePrompt(BaseModel):
    """Claude Code prompt model for .md file generation."""

    filename: str = Field(..., description="Generated filename (without extension)")
    content: str = Field(..., description="Markdown content for the command")
    scope: SyncScope = Field(..., description="Global or project scope")

    @classmethod
    def from_universal_prompt(cls, prompt: Prompt, scope: SyncScope) -> "ClaudeCodePrompt":
        """Create Claude Code prompt from universal Prompt."""
        # Generate filename from prompt name
        filename = prompt.name.lower().replace(" ", "-").replace("_", "-")

        return cls(filename=filename, content=prompt.content, scope=scope)

    def get_file_path(self) -> Path:
        """Get the full file path for this Claude Code prompt."""
        if self.scope.is_global:
            base_path = Path.home() / ".claude" / "commands"
        else:
            project_path = Path(self.scope.path) if self.scope.path else Path.cwd()
            base_path = project_path / ".claude" / "commands"

        return base_path / f"{self.filename}.md"


class CursorPrompt(BaseModel):
    """Cursor prompt model for .mdc file generation with YAML frontmatter."""

    filename: str = Field(..., description="Generated filename (without extension)")
    content: str = Field(..., description="Markdown content for the rule")
    description: str | None = Field(None, description="Rule description")
    globs: list[str] = Field(default_factory=list, description="File glob patterns")
    always_apply: bool = Field(default=False, description="Whether rule always applies")

    @classmethod
    def from_universal_prompt(cls, prompt: Prompt, always_apply: bool = False) -> "CursorPrompt":
        """Create Cursor prompt from universal Prompt."""
        # Generate filename from prompt name
        filename = prompt.name.lower().replace(" ", "-").replace("_", "-")

        # Extract description from tags or use name
        description = prompt.name

        return cls(
            filename=filename, content=prompt.content, description=description, globs=[], always_apply=always_apply
        )

    def get_file_path(self, project_path: Path | None = None) -> Path:
        """Get the full file path for this Cursor prompt (project scope only)."""
        base_path = project_path if project_path else Path.cwd()
        return base_path / ".cursor" / "rules" / f"{self.filename}.mdc"

    def generate_frontmatter(self) -> str:
        """Generate YAML frontmatter for the .mdc file."""
        frontmatter_lines = ["---"]

        if self.description:
            frontmatter_lines.append(f'description: "{self.description}"')

        if self.globs:
            frontmatter_lines.append("globs:")
            for glob in self.globs:
                frontmatter_lines.append(f'  - "{glob}"')

        frontmatter_lines.append(f"alwaysApply: {str(self.always_apply).lower()}")
        frontmatter_lines.append("---")

        return "\n".join(frontmatter_lines)

    def generate_full_content(self) -> str:
        """Generate the complete .mdc file content with frontmatter."""
        return f"{self.generate_frontmatter()}\n\n{self.content}"


class CodingAssistantSinkConfig(BaseModel):
    """Configuration for coding assistant sinks."""

    name: str = Field(..., description="Sink name identifier")
    type: str = Field(..., description="Sink type: 'claude-code' or 'cursor'")
    enabled: bool = Field(default=True, description="Whether this sink is enabled")
    platform: str = Field(..., description="Platform: 'claude-code' or 'cursor'")
    scope: SyncScope = Field(..., description="Scope configuration")

    # Claude Code specific
    global_commands_path: Path | None = Field(None, description="Override global commands path")

    # Cursor specific
    always_apply: bool = Field(default=False, description="Default alwaysApply setting")
    default_globs: list[str] = Field(default_factory=list, description="Default glob patterns")

    # Common settings
    filename_prefix: str | None = Field(None, description="Prefix for generated filenames")
    overwrite_existing: bool = Field(default=True, description="Whether to overwrite existing files")
