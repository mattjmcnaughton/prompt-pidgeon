"""Open-WebUI platform-specific data models."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from prompt_pidgeon.models.core import Prompt


class OpenWebUIUserPrompt(BaseModel):
    """Open-WebUI user prompt model for the prompts API."""

    command: str = Field(..., description="Command with '/' prefix (e.g., '/my-prompt')")
    title: str = Field(..., description="Human-readable title")
    content: str = Field(..., description="Prompt content with variable placeholders")
    access_control: dict[str, Any] = Field(default_factory=dict, description="Access control settings")

    @classmethod
    def from_universal_prompt(cls, prompt: Prompt, command_prefix: str = "lf") -> "OpenWebUIUserPrompt":
        """Create Open-WebUI user prompt from universal Prompt."""
        # Generate command from prompt name
        command_name = prompt.name.lower().replace(" ", "-").replace("_", "-")
        command = f"/{command_prefix}-{command_name}"

        return cls(command=command, title=prompt.name, content=prompt.content, access_control={})


class OpenWebUIModel(BaseModel):
    """Open-WebUI model for system prompts via models API."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Model ID")
    name: str = Field(..., description="Model name (usually same as ID)")
    base_model_id: str = Field(..., description="Base model to use")
    params: dict[str, Any] = Field(default_factory=dict, description="Model parameters including system prompt")
    is_active: bool = Field(default=True, description="Whether model is active")
    meta: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: list[str] = Field(default_factory=list, description="Model tags")

    @classmethod
    def from_universal_prompt(
        cls, prompt: Prompt, base_model_id: str, model_prefix: str = "sme", base_model_short: str = "default"
    ) -> "OpenWebUIModel":
        """Create Open-WebUI system model from universal Prompt."""
        # Generate model ID from prompt name
        prompt_base = prompt.name.lower().replace(" ", "-").replace("_", "-")
        model_id = f"{model_prefix}-{prompt_base}-{base_model_short}"

        return cls(
            id=model_id,
            name=model_id,
            base_model_id=base_model_id,
            params={"system": prompt.content},
            is_active=True,
            meta={},
            tags=["prompt-pidgeon-managed"] + prompt.tags,
        )


class OpenWebUICredentials(BaseModel):
    """Open-WebUI authentication credentials."""

    api_key: str = Field(..., description="Open-WebUI API key")
    base_url: str = Field(..., description="Open-WebUI base URL")

    class Config:
        str_strip_whitespace = True


class OpenWebUISinkConfig(BaseModel):
    """Configuration for Open-WebUI as a sink."""

    name: str = Field(..., description="Sink name identifier")
    type: str = Field(default="open-webui", description="Sink type")
    enabled: bool = Field(default=True, description="Whether this sink is enabled")
    credentials: OpenWebUICredentials | None = Field(
        None, description="Authentication credentials (optional, can use env vars)"
    )
    prompt_type: str = Field(default="user", description="Type: 'user' for prompts API, 'system' for models API")

    # Configuration for user prompts
    command_prefix: str = Field(default="lf", description="Prefix for prompt commands")

    # Configuration for system models
    base_models: list[str] = Field(default_factory=list, description="Base models to create system prompts for")
    model_prefix: str = Field(default="sme", description="Prefix for model IDs")
    default_tags: list[str] = Field(
        default_factory=lambda: ["prompt-pidgeon-managed"], description="Default model tags"
    )
