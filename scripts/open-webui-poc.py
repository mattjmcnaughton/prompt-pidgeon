#!/usr/bin/env python3
"""
Open-WebUI Proof of Concept

This script demonstrates:
1. Uploading a user prompt to Open-WebUI prompts endpoint
2. Creating a model with a system prompt using the models endpoint
3. Using httpx for HTTP requests with proper authentication
"""

import os

import httpx


def validate_env_vars() -> None:
    """Validate that required environment variables are set."""
    required_vars = ["OPEN_WEBUI_API_KEY", "OPEN_WEBUI_URL"]

    for var in required_vars:
        value = os.getenv(var)
        print(f"{var}: {'SET' if value else 'NOT SET'}")
        assert value, f"{var} environment variable is required"


def get_auth_headers() -> dict[str, str]:
    """Get authentication headers for Open-WebUI API."""
    api_key = os.getenv("OPEN_WEBUI_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


def create_user_prompt(client: httpx.Client, base_url: str) -> None:
    """Create a user prompt in Open-WebUI."""
    print("\nCreating user prompt...")

    title = "lf-test-user"

    # Hardcoded user prompt data - based on PromptForm structure
    prompt_data = {
        "command": f"/{title}",  # MUST have a "/" prefix.
        "title": title,
        "content": "You are a helpful assistant. Please help the user with their question: {{question}}",
        "access_control": {}
    }

    response = client.post(
        f"{base_url}/api/v1/prompts/create",
        json=prompt_data,
        headers=get_auth_headers()
    )

    result = response.json()
    print(f"User prompt response ({response.status_code}):")
    print(f"  Command: {result.get('command', 'N/A')}")
    print(f"  Title: {result.get('title', 'N/A')}")
    print(f"  Content: {result.get('content', 'N/A')[:100]}...")


def delete_user_prompts(client: httpx.Client, base_url: str, commands: list[str]) -> None:
    """Delete user prompts by command."""
    print(f"\nDeleting {len(commands)} user prompts...")

    for command in commands:
        print(f"\nDeleting command: {command}")

        # Remove leading slash if present since the endpoint expects it
        clean_command = command.lstrip("/")

        response = client.delete(
            f"{base_url}/api/v1/prompts/command/{clean_command}/delete",
            headers=get_auth_headers()
        )

        result = response.json()
        print(f"Delete response ({response.status_code}): {result}")


def create_system_prompt_model(client: httpx.Client, base_url: str) -> None:
    """Create a model with a system prompt in Open-WebUI."""
    print("\nCreating model with system prompt...")

    # Hardcoded system prompt model data - simplified based on user changes
    model_data = {
        "id": "test-system-model-v2",  # Using v2 to avoid conflicts
        "name": "test-system-model-v2",
        "base_model_id": "google-gemini-2.5-flash",
        "params": {
            "system": "You are a coding assistant specialized in Python development. Always provide clear, well-commented code examples and explain your reasoning."
        },
        "meta": {},
        "tags": ["test", "prompt-pidgeon-managed"]
    }

    response = client.post(
        f"{base_url}/api/v1/models/create",
        json=model_data,
        headers=get_auth_headers()
    )

    result = response.json()
    print(f"System prompt model response ({response.status_code}):")
    print(f"  ID: {result.get('id', 'N/A')}")
    print(f"  Name: {result.get('name', 'N/A')}")
    print(f"  Base Model: {result.get('base_model_id', 'N/A')}")
    print(f"  System Prompt: {result['params']['system'][:100]}...")


def test_connection(client: httpx.Client, base_url: str) -> None:
    """Test connection to Open-WebUI API."""
    print("Testing connection to Open-WebUI...")

    # Test prompts endpoint
    response = client.get(
        f"{base_url}/api/v1/prompts/",
        headers=get_auth_headers()
    )

    print(f"Prompts API response ({response.status_code})")
    print(f"Raw response: {response.content}")
    prompts = response.json()
    print(f"Found {len(prompts)} existing prompts")

    # Show some details about existing prompts
    for i, prompt in enumerate(prompts[:3]):  # Show first 3
        print(f"  {i+1}. {prompt.get('command', 'N/A')} - {prompt.get('title', 'N/A')}")

    # Test models endpoint
    print("\nTesting models API...")
    response = client.get(
        f"{base_url}/api/v1/models/",
        headers=get_auth_headers()
    )

    print(f"Models API response ({response.status_code})")
    models = response.json()
    print(f"Found {len(models)} existing models")

    # Show some details about existing models
    for i, model in enumerate(models[:3]):  # Show first 3
        print(f"  {i+1}. {model.get('id', 'N/A')} - {model.get('name', 'N/A')}")


def main() -> None:
    """Main entry point for the Open-WebUI proof-of-concept."""
    print("Open-WebUI Proof of Concept")
    print("=" * 50)

    # Validate environment variables
    validate_env_vars()

    # Get configuration
    base_url = os.getenv("OPEN_WEBUI_URL").rstrip("/")
    print(f"Base URL: {base_url}")

    # Create HTTP client
    with httpx.Client(timeout=30.0) as client:
        # Test connection
        test_connection(client, base_url)

        # Create user prompt
        create_user_prompt(client, base_url)

        # Create system prompt model
        create_system_prompt_model(client, base_url)

    print("\nProof of concept completed successfully!")
    print("You must now perform manual clean-up of the test prompts and model.")


if __name__ == "__main__":
    main()
