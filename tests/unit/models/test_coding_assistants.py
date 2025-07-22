"""Unit tests for coding assistant platform models."""

from pathlib import Path

from prompt_pidgeon.models.core import Prompt, SyncScope
from prompt_pidgeon.models.platforms.coding_assistants import (
    ClaudeCodePrompt,
    CodingAssistantSinkConfig,
    CursorPrompt,
)


class TestClaudeCodePrompt:
    """Test cases for the ClaudeCodePrompt model."""

    def test_claude_code_prompt_creation(self):
        """Test creating a Claude Code prompt."""
        scope = SyncScope(scope_type="global")

        prompt = ClaudeCodePrompt(filename="review-code", content="You are a code reviewer...", scope=scope)

        assert prompt.filename == "review-code"
        assert prompt.content == "You are a code reviewer..."
        assert prompt.scope == scope

    def test_from_universal_prompt(self):
        """Test creating from universal prompt."""
        universal = Prompt(name="user/review-code", content="You are a code reviewer...")
        scope = SyncScope(scope_type="project", path="/home/user/project")

        claude_prompt = ClaudeCodePrompt.from_universal_prompt(universal, scope)

        assert claude_prompt.filename == "user/review-code"
        assert claude_prompt.content == "You are a code reviewer..."
        assert claude_prompt.scope == scope

    def test_from_universal_prompt_name_normalization(self):
        """Test that spaces and underscores are converted to hyphens."""
        universal = Prompt(name="user/My Complex_Prompt Name", content="Test content")
        scope = SyncScope(scope_type="global")

        claude_prompt = ClaudeCodePrompt.from_universal_prompt(universal, scope)

        assert claude_prompt.filename == "user/my-complex-prompt-name"

    def test_get_file_path_global_scope(self):
        """Test getting file path for global scope."""
        scope = SyncScope(scope_type="global")
        prompt = ClaudeCodePrompt(filename="review-code", content="test", scope=scope)

        expected_path = Path.home() / ".claude" / "commands" / "review-code.md"
        assert prompt.get_file_path() == expected_path

    def test_get_file_path_project_scope_with_path(self):
        """Test getting file path for project scope with specified path."""
        scope = SyncScope(scope_type="project", path="/home/user/myproject")
        prompt = ClaudeCodePrompt(filename="review-code", content="test", scope=scope)

        expected_path = Path("/home/user/myproject") / ".claude" / "commands" / "review-code.md"
        assert prompt.get_file_path() == expected_path

    def test_get_file_path_project_scope_current_dir(self):
        """Test getting file path for project scope using current directory."""
        scope = SyncScope(scope_type="project")
        prompt = ClaudeCodePrompt(filename="review-code", content="test", scope=scope)

        expected_path = Path.cwd() / ".claude" / "commands" / "review-code.md"
        assert prompt.get_file_path() == expected_path


class TestCursorPrompt:
    """Test cases for the CursorPrompt model."""

    def test_cursor_prompt_creation(self):
        """Test creating a Cursor prompt."""
        prompt = CursorPrompt(
            filename="review-code",
            content="You are a code reviewer...",
            description="Code review assistant",
            globs=["*.py", "*.js"],
            always_apply=True,
        )

        assert prompt.filename == "review-code"
        assert prompt.content == "You are a code reviewer..."
        assert prompt.description == "Code review assistant"
        assert prompt.globs == ["*.py", "*.js"]
        assert prompt.always_apply is True

    def test_cursor_prompt_defaults(self):
        """Test Cursor prompt with default values."""
        prompt = CursorPrompt(filename="test", content="test content")

        assert prompt.description is None
        assert prompt.globs == []
        assert prompt.always_apply is False

    def test_from_universal_prompt(self):
        """Test creating from universal prompt."""
        universal = Prompt(name="user/review-code", content="You are a code reviewer...")

        cursor_prompt = CursorPrompt.from_universal_prompt(universal, always_apply=True)

        assert cursor_prompt.filename == "user/review-code"
        assert cursor_prompt.content == "You are a code reviewer..."
        assert cursor_prompt.description == "user/review-code"
        assert cursor_prompt.globs == []
        assert cursor_prompt.always_apply is True

    def test_from_universal_prompt_name_normalization(self):
        """Test that spaces and underscores are converted to hyphens."""
        universal = Prompt(name="user/My Complex_Prompt Name", content="Test content")

        cursor_prompt = CursorPrompt.from_universal_prompt(universal)

        assert cursor_prompt.filename == "user/my-complex-prompt-name"
        assert cursor_prompt.description == "user/My Complex_Prompt Name"  # Description keeps original

    def test_get_file_path_default(self):
        """Test getting file path with default project path."""
        prompt = CursorPrompt(filename="review-code", content="test")

        expected_path = Path.cwd() / ".cursor" / "rules" / "review-code.mdc"
        assert prompt.get_file_path() == expected_path

    def test_get_file_path_custom_project(self):
        """Test getting file path with custom project path."""
        prompt = CursorPrompt(filename="review-code", content="test")

        project_path = Path("/home/user/myproject")
        expected_path = project_path / ".cursor" / "rules" / "review-code.mdc"
        assert prompt.get_file_path(project_path) == expected_path

    def test_generate_frontmatter_minimal(self):
        """Test generating frontmatter with minimal fields."""
        prompt = CursorPrompt(filename="test", content="test content", always_apply=False)

        frontmatter = prompt.generate_frontmatter()
        expected_lines = ["---", "alwaysApply: false", "---"]

        assert frontmatter == "\n".join(expected_lines)

    def test_generate_frontmatter_all_fields(self):
        """Test generating frontmatter with all fields."""
        prompt = CursorPrompt(
            filename="test", content="test content", description="Test rule", globs=["*.py", "*.js"], always_apply=True
        )

        frontmatter = prompt.generate_frontmatter()
        expected_lines = [
            "---",
            'description: "Test rule"',
            "globs:",
            '  - "*.py"',
            '  - "*.js"',
            "alwaysApply: true",
            "---",
        ]

        assert frontmatter == "\n".join(expected_lines)

    def test_generate_full_content(self):
        """Test generating full content with frontmatter."""
        prompt = CursorPrompt(
            filename="test", content="You are a helpful assistant.", description="Test rule", always_apply=True
        )

        full_content = prompt.generate_full_content()

        assert "---" in full_content
        assert 'description: "Test rule"' in full_content
        assert "alwaysApply: true" in full_content
        assert "You are a helpful assistant." in full_content

        # Check structure
        parts = full_content.split("\n\n", 1)
        assert len(parts) == 2
        assert parts[0].startswith("---")
        assert parts[0].endswith("---")
        assert parts[1] == "You are a helpful assistant."


class TestCodingAssistantSinkConfig:
    """Test cases for the CodingAssistantSinkConfig model."""

    def test_sink_config_creation(self):
        """Test creating a coding assistant sink config."""
        scope = SyncScope(scope_type="global")

        config = CodingAssistantSinkConfig(
            name="claude-commands",
            type="claude-code",
            platform="claude-code",
            scope=scope,
            always_apply=True,
            filename_prefix="dev",
            overwrite_existing=False,
        )

        assert config.name == "claude-commands"
        assert config.type == "claude-code"
        assert config.platform == "claude-code"
        assert config.enabled is True  # Default from base class
        assert config.scope == scope
        assert config.always_apply is True
        assert config.filename_prefix == "dev"
        assert config.overwrite_existing is False

    def test_sink_config_defaults(self):
        """Test creating sink config with default values."""
        scope = SyncScope(scope_type="project")

        config = CodingAssistantSinkConfig(name="cursor-rules", type="cursor", platform="cursor", scope=scope)

        assert config.name == "cursor-rules"
        assert config.type == "cursor"
        assert config.platform == "cursor"
        assert config.enabled is True
        assert config.scope == scope
        assert config.always_apply is False
        assert config.filename_prefix is None
        assert config.overwrite_existing is True
