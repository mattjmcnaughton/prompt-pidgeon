"""Core data models for prompt-pidgeon."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    """Universal prompt model that serves as the canonical representation."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the prompt")
    name: str = Field(..., description="Human-readable name for the prompt")
    content: str = Field(..., description="The actual prompt content/text")
    tags: list[str] = Field(default_factory=list, description="Tags for filtering and categorization")

    # Metadata for sync and versioning
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the prompt was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the prompt was last updated")
    version: str = Field(default="1", description="Version identifier for the prompt")

    # Platform-specific metadata preservation
    source_platform: str | None = Field(None, description="Original platform this prompt came from")
    source_id: str | None = Field(None, description="Original platform-specific ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional platform-specific metadata")

    def has_tag(self, tag: str) -> bool:
        """Check if the prompt has a specific tag."""
        return tag in self.tags

    def has_any_tags(self, tags: list[str]) -> bool:
        """Check if the prompt has any of the specified tags."""
        return bool(set(tags) & set(self.tags))

    def has_all_tags(self, tags: list[str]) -> bool:
        """Check if the prompt has all of the specified tags."""
        return set(tags).issubset(set(self.tags))


class TagFilter(BaseModel):
    """Model for tag-based filtering configuration."""

    include_tags: list[str] = Field(default_factory=list, description="Tags that must be present")
    exclude_tags: list[str] = Field(default_factory=list, description="Tags that must not be present")
    require_all: bool = Field(default=False, description="Whether all include_tags must be present")

    def matches(self, prompt: Prompt) -> bool:
        """Check if a prompt matches this filter."""
        # Check exclude tags first
        if prompt.has_any_tags(self.exclude_tags):
            return False

        # Check include tags
        if not self.include_tags:
            return True

        if self.require_all:
            return prompt.has_all_tags(self.include_tags)
        else:
            return prompt.has_any_tags(self.include_tags)


class SyncScope(BaseModel):
    """Model for defining sync scope (global vs project)."""

    scope_type: str = Field(..., description="Type of scope: 'global' or 'project'")
    path: str | None = Field(None, description="Path for project scope")

    @property
    def is_global(self) -> bool:
        """Check if this is a global scope."""
        return self.scope_type == "global"

    @property
    def is_project(self) -> bool:
        """Check if this is a project scope."""
        return self.scope_type == "project"
