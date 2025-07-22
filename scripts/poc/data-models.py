#!/usr/bin/env python3
"""
Data Models Proof of Concept

This script demonstrates how all the data models interact with each other:
1. Create mock Langfuse prompts
2. Convert to universal Prompt models
3. Transform to various sink formats (Open-WebUI, Coding Assistants, Filesystem)
4. Show configuration loading and validation
"""

from datetime import datetime
from pathlib import Path

from prompt_pidgeon.models import (
    ClaudeCodePrompt,
    CursorPrompt,
    FilesystemPrompt,
    # Platform models
    LangfusePrompt,
    OpenWebUIModel,
    OpenWebUIUserPrompt,
    # Configuration
    PidgeonConfig,
    # Core models
    Prompt,
    SyncJobConfig,
    SyncScope,
    TagFilter,
)
from prompt_pidgeon.models.config import (
    CodingAssistantSinkConfig,
    FilesystemSinkConfig,
    LangfuseSourceConfig,
    OpenWebUISinkConfig,
)


def create_mock_langfuse_prompts() -> list[LangfusePrompt]:
    """Create mock Langfuse prompts for demonstration."""
    prompts = [
        LangfusePrompt(
            id="lf-prompt-1",
            name="user/review-code",
            prompt=(
                "You are a senior software engineer conducting a code review. Please analyze the provided code for:\n\n"
                "1. Code quality and best practices\n2. Potential bugs or security issues\n"
                "3. Performance considerations\n4. Maintainability and readability\n\n"
                "Provide specific, actionable feedback."
            ),
            version=1,
            labels=["agentic-coding", "code-review"],
            tags=["technical", "development"],
            created_at=datetime(2024, 1, 15, 10, 0, 0),
            updated_at=datetime(2024, 1, 15, 10, 0, 0),
            config={"temperature": 0.3, "max_tokens": 1000},
        ),
        LangfusePrompt(
            id="lf-prompt-2",
            name="system/design-expert",
            prompt=(
                "You are an expert system architect. Help design scalable, maintainable systems by:\n\n"
                "1. Understanding requirements and constraints\n2. Proposing appropriate architectures\n"
                "3. Identifying potential bottlenecks\n4. Recommending technologies and patterns\n\n"
                "Focus on practical, production-ready solutions."
            ),
            version=2,
            labels=["agentic-coding", "architecture"],
            tags=["technical", "system-design"],
            created_at=datetime(2024, 1, 10, 14, 30, 0),
            updated_at=datetime(2024, 1, 20, 16, 45, 0),
            config={"temperature": 0.5, "max_tokens": 1500},
        ),
        LangfusePrompt(
            id="lf-prompt-3",
            name="user/improve-writing",
            prompt=(
                "You are a professional writing assistant. Help improve written communication by:\n\n"
                "1. Enhancing clarity and conciseness\n2. Improving tone and style\n3. Correcting grammar and syntax\n"
                "4. Ensuring logical flow\n\nProvide constructive suggestions while preserving the author's voice."
            ),
            version=1,
            labels=["general", "writing"],
            tags=["productivity", "communication"],
            created_at=datetime(2024, 1, 12, 9, 15, 0),
            updated_at=datetime(2024, 1, 12, 9, 15, 0),
            config={"temperature": 0.7, "max_tokens": 800},
        ),
    ]

    return prompts


def demonstrate_universal_conversion(langfuse_prompts: list[LangfusePrompt]) -> list[Prompt]:
    """Demonstrate conversion from Langfuse to universal Prompt models."""
    print("=== Universal Prompt Conversion ===")

    universal_prompts = []
    for lf_prompt in langfuse_prompts:
        universal = lf_prompt.to_universal_prompt()
        universal_prompts.append(universal)

        print(f"Converted: {universal.name}")
        print(f"  ID: {universal.id}")
        print(f"  Tags: {universal.tags}")
        print(f"  Source: {universal.source_platform} ({universal.source_id})")
        print(f"  Content preview: {universal.content[:80]}...")
        print()

    return universal_prompts


def demonstrate_tag_filtering(universal_prompts: list[Prompt]) -> None:
    """Demonstrate tag-based filtering capabilities."""
    print("=== Tag Filtering Demonstration ===")

    # Create various filters
    filters = [
        TagFilter(include_tags=["agentic-coding"], require_all=False),
        TagFilter(include_tags=["technical"], require_all=False),
        TagFilter(include_tags=["general"], exclude_tags=["technical"], require_all=False),
        TagFilter(include_tags=["agentic-coding", "code-review"], require_all=True),
    ]

    for i, tag_filter in enumerate(filters, 1):
        matching_prompts = [p for p in universal_prompts if tag_filter.matches(p)]
        print(f"Filter {i}: {tag_filter.model_dump()}")
        print(f"  Matches: {[p.name for p in matching_prompts]}")
        print()


def demonstrate_prompt_types(universal_prompts: list[Prompt]) -> None:
    """Demonstrate user vs system prompt distinction."""
    print("=== User vs System Prompt Distinction ===")

    user_prompts = [p for p in universal_prompts if p.name.startswith("user/")]
    system_prompts = [p for p in universal_prompts if p.name.startswith("system/")]

    print("User Prompts (for Open-WebUI prompts API):")
    for prompt in user_prompts:
        print(f"  {prompt.name} - {prompt.content[:50]}...")

    print("\nSystem Prompts (for Open-WebUI models API):")
    for prompt in system_prompts:
        print(f"  {prompt.name} - {prompt.content[:50]}...")
    print()


def demonstrate_openwebui_conversion(universal_prompts: list[Prompt]) -> None:
    """Demonstrate conversion to Open-WebUI formats."""
    print("=== Open-WebUI Conversion ===")

    # Separate user and system prompts
    user_prompts = [p for p in universal_prompts if p.name.startswith("user/")]
    system_prompts = [p for p in universal_prompts if p.name.startswith("system/")]

    print("User Prompts (→ Open-WebUI prompts API):")
    for prompt in user_prompts:
        user_prompt = OpenWebUIUserPrompt.from_universal_prompt(prompt, command_prefix="lf")
        print(f"  {user_prompt.command} - {user_prompt.title}")

    print("\nSystem Models (→ Open-WebUI models API):")
    base_models = ["anthropic-claude-4-sonnet", "google-gemini-2.5-flash"]
    for prompt in system_prompts:
        for base_model in base_models:
            model = OpenWebUIModel.from_universal_prompt(
                prompt, base_model_id=base_model, model_prefix="sme", base_model_short=base_model.split("-")[-1]
            )
            print(f"  {model.id} -> {model.base_model_id}")
    print()


def demonstrate_coding_assistants(universal_prompts: list[Prompt]) -> None:
    """Demonstrate conversion to coding assistant formats."""
    print("=== Coding Assistants Conversion ===")

    # Filter for agentic-coding prompts
    coding_prompts = [p for p in universal_prompts if p.has_tag("agentic-coding")]

    # Claude Code (global scope)
    print("Claude Code (Global):")
    global_scope = SyncScope(scope_type="global")
    for prompt in coding_prompts:
        claude_prompt = ClaudeCodePrompt.from_universal_prompt(prompt, global_scope)
        print(f"  {claude_prompt.get_file_path()}")

    # Claude Code (project scope)
    print("\nClaude Code (Project):")
    project_scope = SyncScope(scope_type="project", path="/home/user/my-project")
    for prompt in coding_prompts:
        claude_prompt = ClaudeCodePrompt.from_universal_prompt(prompt, project_scope)
        print(f"  {claude_prompt.get_file_path()}")

    # Cursor
    print("\nCursor Rules:")
    for prompt in coding_prompts:
        cursor_prompt = CursorPrompt.from_universal_prompt(prompt, always_apply=True)
        print(f"  {cursor_prompt.get_file_path()}")
        print("    Frontmatter preview:")
        frontmatter_lines = cursor_prompt.generate_frontmatter().split("\n")[:4]
        for line in frontmatter_lines:
            print(f"      {line}")
    print()


def demonstrate_filesystem_conversion(universal_prompts: list[Prompt]) -> None:
    """Demonstrate conversion to filesystem format."""
    print("=== Filesystem Conversion ===")

    for prompt in universal_prompts:
        fs_prompt = FilesystemPrompt.from_universal_prompt(prompt)
        print(f"File: {fs_prompt.filename}.{fs_prompt.file_extension}")
        print(f"  Metadata keys: {list(fs_prompt.metadata.keys())}")

        # Show frontmatter preview
        frontmatter_lines = fs_prompt.generate_frontmatter().split("\n")[:6]
        print("  Frontmatter preview:")
        for line in frontmatter_lines:
            print(f"    {line}")
        print()


def demonstrate_configuration() -> None:
    """Demonstrate configuration model usage."""
    print("=== Configuration Demonstration ===")

    # Create a sample configuration
    config = PidgeonConfig(
        version="1",
        sources=[LangfuseSourceConfig(name="my-langfuse", tag_filter=["agentic-coding", "general"], batch_size=50)],
        sinks=[
            OpenWebUISinkConfig(name="my-openwebui", prompt_type="user", command_prefix="lf"),
            FilesystemSinkConfig(
                name="local-backup", path=Path("./prompts"), create_subdirectories=True, git_integration=True
            ),
            CodingAssistantSinkConfig(
                name="cursor-rules",
                type="cursor",
                platform="cursor",
                scope=SyncScope(scope_type="project"),
                always_apply=False,
            ),
        ],
        sync=[
            SyncJobConfig(
                name="Sync coding prompts to Cursor",
                source="my-langfuse",
                sink="cursor-rules",
                filter=TagFilter(include_tags=["agentic-coding"]),
            ),
            SyncJobConfig(name="Backup all prompts", source="my-langfuse", sink="local-backup"),
        ],
    )

    print(f"Configuration version: {config.version}")
    print(f"Sources: {[s.name for s in config.sources]}")
    print(f"Sinks: {[s.name for s in config.sinks]}")
    print(f"Sync jobs: {[j.name for j in config.sync]}")

    # Demonstrate validation
    print(f"\nEnabled sync jobs: {len(config.get_enabled_sync_jobs())}")

    # Show how to find configurations by name
    langfuse_source = config.get_source_by_name("my-langfuse")
    if langfuse_source:
        print(f"Found source: {langfuse_source.name} ({langfuse_source.type})")

    cursor_sink = config.get_sink_by_name("cursor-rules")
    if cursor_sink:
        print(f"Found sink: {cursor_sink.name} ({cursor_sink.type})")
    print()


def main() -> None:
    """Main demonstration function."""
    print("Prompt Pidgeon Data Models Proof of Concept")
    print("=" * 50)
    print()

    # 1. Create mock data
    langfuse_prompts = create_mock_langfuse_prompts()
    print(f"Created {len(langfuse_prompts)} mock Langfuse prompts")
    print()

    # 2. Convert to universal format
    universal_prompts = demonstrate_universal_conversion(langfuse_prompts)

    # 3. Show user/system prompt distinction
    demonstrate_prompt_types(universal_prompts)

    # 4. Demonstrate filtering
    demonstrate_tag_filtering(universal_prompts)

    # 5. Convert to various sink formats
    demonstrate_openwebui_conversion(universal_prompts)
    demonstrate_coding_assistants(universal_prompts)
    demonstrate_filesystem_conversion(universal_prompts)

    # 6. Show configuration usage
    demonstrate_configuration()

    print("=== Data Models PoC Complete ===")
    print("All models successfully created and demonstrated their interactions!")


if __name__ == "__main__":
    main()
