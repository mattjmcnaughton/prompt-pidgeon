"""Langfuse platform-specific data models."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from prompt_pidgeon.models.core import Prompt


class LangfusePrompt(BaseModel):
    """Langfuse prompt model matching their API structure."""

    id: str = Field(..., description="Langfuse prompt ID")
    name: str = Field(..., description="Prompt name")
    prompt: str = Field(..., description="Prompt content/template")
    version: int = Field(..., description="Prompt version number")
    type: str = Field(default="text", description="Prompt type")
    labels: list[str] = Field(default_factory=list, description="Langfuse labels/tags")
    tags: list[str] = Field(default_factory=list, description="Additional tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    config: dict[str, Any] = Field(default_factory=dict, description="Prompt configuration")

    def to_universal_prompt(self) -> Prompt:
        """Convert Langfuse prompt to universal Prompt model."""
        # Combine labels and tags for universal model
        all_tags = list(set(self.labels + self.tags))

        return Prompt(
            id=str(uuid4()),  # Generate new universal ID
            name=self.name,
            content=self.prompt,
            tags=all_tags,
            created_at=self.created_at,
            updated_at=self.updated_at,
            version=str(self.version),
            source_platform="langfuse",
            source_id=self.id,
            metadata={
                "langfuse_version": self.version,
                "langfuse_type": self.type,
                "langfuse_config": self.config,
                "langfuse_labels": self.labels,
            },
        )


class LangfuseCredentials(BaseModel):
    """Langfuse authentication credentials."""

    public_key: str = Field(..., description="Langfuse public key")
    secret_key: str = Field(..., description="Langfuse secret key")
    host: str | None = Field(None, description="Langfuse host URL")

    class Config:
        # Ensure sensitive data doesn't leak in logs
        str_strip_whitespace = True


class LangfuseSourceConfig(BaseModel):
    """Configuration for Langfuse as a source."""

    name: str = Field(..., description="Source name identifier")
    type: str = Field(default="langfuse", description="Source type")
    enabled: bool = Field(default=True, description="Whether this source is enabled")
    credentials: LangfuseCredentials | None = Field(
        None, description="Authentication credentials (optional, can use env vars)"
    )
    tag_filter: list[str] | None = Field(None, description="Filter prompts by specific tags/labels")
    include_archived: bool = Field(default=False, description="Include archived prompts")
    batch_size: int = Field(default=100, description="Batch size for fetching prompts")
