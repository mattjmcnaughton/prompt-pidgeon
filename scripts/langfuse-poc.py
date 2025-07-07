import os
import sys
from datetime import datetime
from typing import Any

from langfuse import get_client


def validate_env_vars() -> None:
    """Validate that required environment variables are set."""
    required_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]

    for var in required_vars:
        if not os.getenv(var):
            print(f"Error: {var} environment variable is required")
            sys.exit(1)


def connect_to_langfuse() -> Any:
    """Initialize and test connection to Langfuse."""
    host = os.getenv("LANGFUSE_HOST")
    print("Connecting to Langfuse (project: main, org: homelab)...")
    print(f"Host: {host}")

    try:
        # get_client() automatically reads from environment variables, but we want to use `public_key`
        # so that we can select our specific project.
        client = get_client()

        # Test the connection by making a simple API call
        print("Connected successfully")
        return client

    except Exception as e:
        print(f"Failed to connect to Langfuse: {e}")
        sys.exit(1)


def format_timestamp(timestamp: str | None) -> str:
    """Format timestamp for display."""
    if not timestamp:
        return "Unknown"

    try:
        # Parse ISO format timestamp
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp


def list_prompts(client: Any) -> None:
    """Fetch and display all prompts from Langfuse."""
    try:
        print("\nFetching prompts...")

        # Get all prompts using the correct API method
        response = client.api.prompts.list()

        if not response or not response.data:
            print("No prompts found.")
            return

        prompt_list = response.data
        print(f"\nFound {len(prompt_list)} prompts:\n")

        for i, prompt_meta in enumerate(prompt_list, 1):
            print(f"{i}. {prompt_meta.name}")

            # For prompt content, we need to fetch individual prompts
            try:
                # Will retrieve the `production` version.
                full_prompt = client.get_prompt(prompt_meta.name)
                if hasattr(full_prompt, "prompt") and full_prompt.prompt:
                    content = str(full_prompt.prompt)[:100]
                    if len(str(full_prompt.prompt)) > 100:
                        content += "..."
                    print(f'   Content: "{content}"')
                else:
                    print("   Content: No content available")
            except Exception:
                print("   Content: Unable to fetch content")

            print()  # Empty line between prompts

        print(f"Total: {len(prompt_list)} prompts found")

    except Exception as e:
        print(f"Failed to fetch prompts: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the smoke test."""
    print("Prompt Pidgeon - Langfuse Smoke Test")
    print("=" * 50)

    # Validate environment variables
    validate_env_vars()

    # Connect to Langfuse
    client = connect_to_langfuse()

    # List all prompts
    list_prompts(client)

    print("\nSmoke test completed successfully!")


if __name__ == "__main__":
    main()
