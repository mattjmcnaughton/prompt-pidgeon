"""Unit tests for filesystem platform models."""

from datetime import datetime
from pathlib import Path

from prompt_pidgeon.models.core import Prompt
from prompt_pidgeon.models.platforms.filesystem import (
    FilesystemPrompt,
    FilesystemSinkConfig,
    GitConfig,
)


class TestFilesystemPrompt:
    """Test cases for the FilesystemPrompt model."""

    def test_filesystem_prompt_creation(self):
        """Test creating a filesystem prompt."""
        metadata = {"id": "123", "tags": ["test"]}

        prompt = FilesystemPrompt(
            filename="review-code", content="You are a code reviewer...", metadata=metadata, file_extension="txt"
        )

        assert prompt.filename == "review-code"
        assert prompt.content == "You are a code reviewer..."
        assert prompt.metadata == metadata
        assert prompt.file_extension == "txt"

    def test_filesystem_prompt_defaults(self):
        """Test filesystem prompt with default values."""
        prompt = FilesystemPrompt(filename="test", content="test content")

        assert prompt.metadata == {}
        assert prompt.file_extension == "md"

    def test_from_universal_prompt(self):
        """Test creating from universal prompt."""
        created_at = datetime(2024, 1, 15, 10, 0, 0)
        updated_at = datetime(2024, 1, 16, 11, 0, 0)

        universal = Prompt(
            id="test-123",
            name="user/review-code",
            content="You are a code reviewer...",
            tags=["technical", "code-review"],
            created_at=created_at,
            updated_at=updated_at,
            version="2",
            source_platform="langfuse",
            source_id="lf-123",
            metadata={"temperature": 0.3},
        )

        fs_prompt = FilesystemPrompt.from_universal_prompt(universal)

        assert fs_prompt.filename == "user/review-code"
        assert fs_prompt.content == "You are a code reviewer..."
        assert fs_prompt.file_extension == "md"

        # Check preserved metadata
        expected_metadata = {
            "id": "test-123",
            "name": "user/review-code",
            "tags": ["technical", "code-review"],
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "version": "2",
            "source_platform": "langfuse",
            "source_id": "lf-123",
            "temperature": 0.3,  # From original metadata
        }
        assert fs_prompt.metadata == expected_metadata

    def test_from_universal_prompt_name_normalization(self):
        """Test that spaces and underscores are converted to hyphens."""
        universal = Prompt(name="user/My Complex_Prompt Name", content="Test content")

        fs_prompt = FilesystemPrompt.from_universal_prompt(universal)

        assert fs_prompt.filename == "user/my-complex-prompt-name"

    def test_generate_frontmatter_empty(self):
        """Test generating frontmatter with no metadata."""
        prompt = FilesystemPrompt(filename="test", content="test", metadata={})

        frontmatter = prompt.generate_frontmatter()
        assert frontmatter == ""

    def test_generate_frontmatter_simple(self):
        """Test generating frontmatter with simple metadata."""
        metadata = {"id": "123", "name": "test-prompt", "version": "1"}

        prompt = FilesystemPrompt(filename="test", content="test", metadata=metadata)

        frontmatter = prompt.generate_frontmatter()
        expected_lines = ["---", 'id: "123"', 'name: "test-prompt"', 'version: "1"', "---"]

        assert frontmatter == "\n".join(expected_lines)

    def test_generate_frontmatter_with_list(self):
        """Test generating frontmatter with list metadata."""
        metadata = {"name": "test", "tags": ["technical", "code-review"], "version": "1"}

        prompt = FilesystemPrompt(filename="test", content="test", metadata=metadata)

        frontmatter = prompt.generate_frontmatter()

        assert "---" in frontmatter
        assert 'name: "test"' in frontmatter
        assert 'version: "1"' in frontmatter
        assert "tags:" in frontmatter
        assert '  - "technical"' in frontmatter
        assert '  - "code-review"' in frontmatter

    def test_generate_frontmatter_with_dict(self):
        """Test generating frontmatter with nested dict metadata."""
        metadata = {"name": "test", "config": {"temperature": 0.3, "model": "gpt-4"}}

        prompt = FilesystemPrompt(filename="test", content="test", metadata=metadata)

        frontmatter = prompt.generate_frontmatter()

        assert "---" in frontmatter
        assert 'name: "test"' in frontmatter
        assert "config:" in frontmatter
        assert "  temperature: 0.3" in frontmatter
        assert '  model: "gpt-4"' in frontmatter

    def test_generate_full_content_with_frontmatter(self):
        """Test generating full content with frontmatter."""
        metadata = {"name": "test", "version": "1"}

        prompt = FilesystemPrompt(filename="test", content="You are a helpful assistant.", metadata=metadata)

        full_content = prompt.generate_full_content()

        assert "---" in full_content
        assert 'name: "test"' in full_content
        assert 'version: "1"' in full_content
        assert "You are a helpful assistant." in full_content

        # Check structure
        parts = full_content.split("\n\n", 1)
        assert len(parts) == 2
        assert parts[0].startswith("---")
        assert parts[0].endswith("---")
        assert parts[1] == "You are a helpful assistant."

    def test_generate_full_content_without_frontmatter(self):
        """Test generating full content without frontmatter."""
        prompt = FilesystemPrompt(filename="test", content="You are a helpful assistant.", metadata={})

        full_content = prompt.generate_full_content()
        assert full_content == "You are a helpful assistant."

    def test_get_file_path(self):
        """Test getting file path."""
        prompt = FilesystemPrompt(filename="review-code", content="test", file_extension="txt")

        base_path = Path("/home/user/prompts")
        expected_path = base_path / "review-code.txt"

        assert prompt.get_file_path(base_path) == expected_path


class TestFilesystemSinkConfig:
    """Test cases for the FilesystemSinkConfig model."""

    def test_sink_config_creation(self):
        """Test creating a filesystem sink config."""
        config = FilesystemSinkConfig(
            name="local-backup",
            path=Path("/home/user/prompts"),
            create_subdirectories=True,
            subdirectory_tag="technical",
            file_extension="txt",
            include_frontmatter=False,
            preserve_timestamps=False,
            overwrite_existing=False,
            backup_existing=True,
            git_integration=True,
            auto_commit=True,
            commit_message_template="Custom commit: {}",
        )

        assert config.name == "local-backup"
        assert config.type == "filesystem"
        assert config.enabled is True  # Default from base class
        assert config.path == Path("/home/user/prompts")
        assert config.create_subdirectories is True
        assert config.subdirectory_tag == "technical"
        assert config.file_extension == "txt"
        assert config.include_frontmatter is False
        assert config.preserve_timestamps is False
        assert config.overwrite_existing is False
        assert config.backup_existing is True
        assert config.git_integration is True
        assert config.auto_commit is True
        assert config.commit_message_template == "Custom commit: {}"

    def test_sink_config_defaults(self):
        """Test creating sink config with default values."""
        config = FilesystemSinkConfig(name="local-backup", path=Path("/home/user/prompts"))

        assert config.name == "local-backup"
        assert config.type == "filesystem"
        assert config.path == Path("/home/user/prompts")
        assert config.create_subdirectories is False
        assert config.subdirectory_tag is None
        assert config.file_extension == "md"
        assert config.include_frontmatter is True
        assert config.preserve_timestamps is True
        assert config.overwrite_existing is True
        assert config.backup_existing is False
        assert config.git_integration is False
        assert config.auto_commit is False
        assert config.commit_message_template == "Update prompts via prompt-pidgeon sync"

    def test_get_prompt_path_no_subdirectories(self):
        """Test getting prompt path without subdirectories."""
        config = FilesystemSinkConfig(name="test", path=Path("/home/user/prompts"), create_subdirectories=False)

        prompt = Prompt(name="user/review-code", content="test", tags=["technical"])
        fs_prompt = FilesystemPrompt.from_universal_prompt(prompt)

        expected_path = Path("/home/user/prompts") / "user/review-code.md"
        assert config.get_prompt_path(prompt, fs_prompt) == expected_path

    def test_get_prompt_path_with_subdirectories_specific_tag(self):
        """Test getting prompt path with subdirectories using specific tag."""
        config = FilesystemSinkConfig(
            name="test", path=Path("/home/user/prompts"), create_subdirectories=True, subdirectory_tag="technical"
        )

        prompt = Prompt(name="user/review-code", content="test", tags=["technical", "development"])
        fs_prompt = FilesystemPrompt.from_universal_prompt(prompt)

        expected_path = Path("/home/user/prompts") / "technical" / "user/review-code.md"
        assert config.get_prompt_path(prompt, fs_prompt) == expected_path

    def test_get_prompt_path_with_subdirectories_first_tag(self):
        """Test getting prompt path with subdirectories using first tag."""
        config = FilesystemSinkConfig(name="test", path=Path("/home/user/prompts"), create_subdirectories=True)

        prompt = Prompt(name="user/review-code", content="test", tags=["development", "technical"])
        fs_prompt = FilesystemPrompt.from_universal_prompt(prompt)

        expected_path = Path("/home/user/prompts") / "development" / "user/review-code.md"
        assert config.get_prompt_path(prompt, fs_prompt) == expected_path

    def test_get_prompt_path_with_subdirectories_no_tags(self):
        """Test getting prompt path with subdirectories for untagged prompt."""
        config = FilesystemSinkConfig(name="test", path=Path("/home/user/prompts"), create_subdirectories=True)

        prompt = Prompt(name="user/review-code", content="test", tags=[])
        fs_prompt = FilesystemPrompt.from_universal_prompt(prompt)

        expected_path = Path("/home/user/prompts") / "untagged" / "user/review-code.md"
        assert config.get_prompt_path(prompt, fs_prompt) == expected_path

    def test_get_prompt_path_specific_tag_not_present(self):
        """Test getting prompt path when specific tag is not present."""
        config = FilesystemSinkConfig(
            name="test", path=Path("/home/user/prompts"), create_subdirectories=True, subdirectory_tag="missing"
        )

        prompt = Prompt(name="user/review-code", content="test", tags=["technical"])
        fs_prompt = FilesystemPrompt.from_universal_prompt(prompt)

        # Should use first tag when specific tag is not present
        expected_path = Path("/home/user/prompts") / "technical" / "user/review-code.md"
        assert config.get_prompt_path(prompt, fs_prompt) == expected_path


class TestGitConfig:
    """Test cases for the GitConfig model."""

    def test_git_config_creation(self):
        """Test creating a Git config."""
        config = GitConfig(
            enabled=True,
            auto_add=False,
            auto_commit=True,
            commit_message="Custom commit message",
            author_name="Test User",
            author_email="test@example.com",
        )

        assert config.enabled is True
        assert config.auto_add is False
        assert config.auto_commit is True
        assert config.commit_message == "Custom commit message"
        assert config.author_name == "Test User"
        assert config.author_email == "test@example.com"

    def test_git_config_defaults(self):
        """Test Git config with default values."""
        config = GitConfig()

        assert config.enabled is False
        assert config.auto_add is True
        assert config.auto_commit is False
        assert config.commit_message == "Update prompts via prompt-pidgeon"
        assert config.author_name is None
        assert config.author_email is None
