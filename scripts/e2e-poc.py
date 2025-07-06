#!/usr/bin/env python3
"""
End-to-End Proof of Concept: Langfuse to Open-WebUI Sync

This script demonstrates:
1. Reading all prompts from Langfuse
2. Filtering by naming conventions:
   - user/* -> Open-WebUI user prompts
   - system/* -> Open-WebUI models
3. Creating models with multiple base model IDs
4. Hard failing on any errors for debugging
"""

import os
from typing import Any

import httpx
from langfuse import get_client
from pydantic import BaseModel

# Constants
PROMPT_PREFIX = "lf"
MODEL_PREFIX = "sme"
DEFAULT_TAGS = ["prompt-pidgeon-managed", "langfuse-sync"]
DEFAULT_MODEL = "anthropic-claude-4-sonnet"


class BaseModelConfig(BaseModel):
    """Configuration for a base model."""
    full_name: str
    short_name: str
    is_active: bool = True


class LangfusePrompt(BaseModel):
    """Langfuse prompt data structure."""
    name: str
    content: str


class SyncConfig(BaseModel):
    """Configuration for sync operation."""
    base_models: list[BaseModelConfig]
    langfuse_client: Any
    openwebui_client: httpx.Client
    openwebui_base_url: str

    class Config:
        arbitrary_types_allowed = True


def validate_env_vars() -> None:
    """Validate that required environment variables are set."""
    required_vars = [
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_HOST",
        "OPEN_WEBUI_API_KEY",
        "OPEN_WEBUI_URL"
    ]

    for var in required_vars:
        value = os.getenv(var)
        print(f"{var}: {'SET' if value else 'NOT SET'}")
        assert value, f"{var} environment variable is required"


def get_openwebui_auth_headers() -> dict[str, str]:
    """Get authentication headers for Open-WebUI API."""
    api_key = os.getenv("OPEN_WEBUI_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


def fetch_langfuse_prompts(client: Any) -> list[LangfusePrompt]:
    """Fetch all prompts from Langfuse."""
    print("Fetching prompts from Langfuse...")

    # Get all prompts metadata
    response = client.api.prompts.list()
    assert response and response.data, "No prompts found in Langfuse"

    prompts = []
    for prompt_meta in response.data:
        print(f"Fetching prompt: {prompt_meta.name}")

        # Get full prompt content
        full_prompt = client.get_prompt(prompt_meta.name)
        assert full_prompt and full_prompt.prompt, f"Could not fetch content for {prompt_meta.name}"

        prompts.append(LangfusePrompt(
            name=prompt_meta.name,
            content=str(full_prompt.prompt),
        ))

    print(f"Fetched {len(prompts)} prompts from Langfuse")
    return prompts


def filter_prompts_by_type(prompts: list[LangfusePrompt]) -> tuple[list[LangfusePrompt], list[LangfusePrompt]]:
    """Filter prompts by naming convention."""
    user_prompts = []
    system_prompts = []

    for prompt in prompts:
        if prompt.name.startswith("user/"):
            user_prompts.append(prompt)
        elif prompt.name.startswith("system/"):
            system_prompts.append(prompt)
        else:
            print(f"Skipping prompt (no prefix): {prompt.name}")

    print(f"Filtered: {len(user_prompts)} user prompts, {len(system_prompts)} system prompts")
    return user_prompts, system_prompts


def delete_openwebui_user_prompt(config: SyncConfig, command: str) -> None:
    """Delete a user prompt from Open-WebUI if it exists."""
    # Remove leading slash for the API endpoint
    clean_command = command.lstrip("/")

    try:
        response = config.openwebui_client.delete(
            f"{config.openwebui_base_url}/api/v1/prompts/command/{clean_command}/delete",
            headers=get_openwebui_auth_headers()
        )

        if response.status_code == 200:
            print(f"Deleted existing prompt: {command}")
        elif response.status_code == 401:
            # Prompt not found or unauthorized (treating as not found)
            print(f"Prompt {command} does not exist (skipping delete)")
        else:
            print(f"Delete prompt failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Error deleting prompt {command}: {e}")


def delete_openwebui_model(config: SyncConfig, model_id: str) -> None:
    """Delete a model from Open-WebUI if it exists."""
    try:
        # Using the model delete endpoint with id as query parameter
        response = config.openwebui_client.delete(
            f"{config.openwebui_base_url}/api/v1/models/model/delete",
            params={"id": model_id},
            headers=get_openwebui_auth_headers()
        )

        if response.status_code == 200:
            print(f"Deleted existing model: {model_id}")
        elif response.status_code == 401:
            # Model not found or unauthorized (treating as not found)
            print(f"Model {model_id} does not exist (skipping delete)")
        else:
            print(f"Delete model failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Error deleting model {model_id}: {e}")


def create_openwebui_user_prompt(config: SyncConfig, prompt: LangfusePrompt) -> None:
    """Create a user prompt in Open-WebUI."""
    print(f"\nSyncing user prompt: {prompt.name}")

    # Convert user/prompt-name to /prompt-name format
    # The command MUST include `/`. Otherwise, we can't access/delete from the UI.
    # If we _do_ create without a `/`, we have to delete directly from the database.
    command = f"/{PROMPT_PREFIX}-{prompt.name.replace('user/', '')}"
    title = f"{PROMPT_PREFIX}-{prompt.name.replace('user/', '')}"

    # Delete existing prompt first
    delete_openwebui_user_prompt(config, command)

    prompt_data = {
        "command": command,
        "title": title,
        "content": prompt.content,
        "access_control": {}
    }

    response = config.openwebui_client.post(
        f"{config.openwebui_base_url}/api/v1/prompts/create",
        json=prompt_data,
        headers=get_openwebui_auth_headers()
    )

    # Hard fail on error
    response.raise_for_status()

    result = response.json()
    print(f"Created user prompt: {result.get('command')} - {result.get('title')}")


def create_openwebui_system_model(config: SyncConfig, prompt: LangfusePrompt, base_model_config: BaseModelConfig) -> None:
    """Create a system prompt model in Open-WebUI."""
    print(f"\nSyncing system model: {prompt.name} with base model {base_model_config.full_name}")

    # Convert system/prompt-name to model ID and name
    prompt_base = prompt.name.replace('system/', '').replace('/', '-')
    model_id = f"{MODEL_PREFIX}-{prompt_base}-{base_model_config.short_name}"

    # Delete existing model first
    delete_openwebui_model(config, model_id)

    model_data = {
        "id": model_id,
        "name": model_id,
        "base_model_id": base_model_config.full_name,
        "params": {
            "system": prompt.content
        },
        "is_active": base_model_config.is_active,
        "meta": {},
        "tags": DEFAULT_TAGS
    }

    response = config.openwebui_client.post(
        f"{config.openwebui_base_url}/api/v1/models/create",
        json=model_data,
        headers=get_openwebui_auth_headers()
    )

    # Hard fail on error
    response.raise_for_status()

    result = response.json()
    print(f"Created system model: {result.get('id')} - {result.get('name')}")


def sync_user_prompts(config: SyncConfig, user_prompts: list[LangfusePrompt]) -> None:
    """Sync user prompts to Open-WebUI."""
    print(f"\n=== Syncing {len(user_prompts)} User Prompts ===")

    for prompt in user_prompts:
        create_openwebui_user_prompt(config, prompt)


def sync_system_prompts(config: SyncConfig, system_prompts: list[LangfusePrompt]) -> None:
    """Sync system prompts to Open-WebUI models."""
    print(f"\n=== Syncing {len(system_prompts)} System Prompts ===")
    print(f"Creating models with {len(config.base_models)} base models: {[model.full_name for model in config.base_models]}")

    for prompt in system_prompts:
        for base_model_config in config.base_models:
            create_openwebui_system_model(config, prompt, base_model_config)


def get_base_model_configs() -> list[BaseModelConfig]:
    """Get the configured base models."""
    return [
        BaseModelConfig(
            full_name=DEFAULT_MODEL,
            short_name="default",
            is_active=True
        ),
        BaseModelConfig(
            full_name="google-gemini-2.5-flash",
            short_name="gemini-fast",
            is_active=True
        ),
        BaseModelConfig(
            full_name="google-gemini-2.5-pro",
            short_name="gemini-pro",
            is_active=True
        ),
        BaseModelConfig(
            full_name="anthropic-claude-4-sonnet",
            short_name="claude-fast",
            is_active=True
        ),
        BaseModelConfig(
            full_name="anthropic-claude-4-opus",
            short_name="claude-pro",
            is_active=True
        ),
        BaseModelConfig(
            full_name="openai-gpt-4o",
            short_name="openai-fast",
            is_active=False
        ),
        BaseModelConfig(
            full_name="openai-gpt-4.5-preview-2025-02-27",
            short_name="openai-pro",
            is_active=True
        ),
        BaseModelConfig(
            full_name="mistral-8x7b-instruct",
            short_name="mistral-fast",
            is_active=True
        )
    ]


def main() -> None:
    """Main entry point for the end-to-end proof-of-concept."""
    print("Langfuse to Open-WebUI E2E Sync")
    print("=" * 50)

    # Validate environment variables
    validate_env_vars()

    # Configuration
    base_models = get_base_model_configs()

    # Initialize clients
    print("Initializing clients...")
    langfuse_client = get_client()
    openwebui_base_url = os.getenv("OPEN_WEBUI_URL").rstrip("/")

    with httpx.Client(timeout=30.0) as openwebui_client:
        config = SyncConfig(
            base_models=base_models,
            langfuse_client=langfuse_client,
            openwebui_client=openwebui_client,
            openwebui_base_url=openwebui_base_url
        )

        # Fetch all prompts from Langfuse
        all_prompts = fetch_langfuse_prompts(langfuse_client)

        # Filter by naming convention
        user_prompts, system_prompts = filter_prompts_by_type(all_prompts)

        # Sync user prompts
        sync_user_prompts(config, user_prompts)

        # Sync system prompts
        sync_system_prompts(config, system_prompts)

    print("\n=== E2E Sync Completed Successfully ===")
    print(f"Synced {len(user_prompts)} user prompts")
    print(f"Synced {len(system_prompts)} system prompts to {len(base_models)} base models each")
    print(f"Total models created: {len(system_prompts) * len(base_models)}")


if __name__ == "__main__":
    main()
