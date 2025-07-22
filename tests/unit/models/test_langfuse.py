"""Unit tests for Langfuse platform models."""

from datetime import datetime

from prompt_pidgeon.models.core import Prompt
from prompt_pidgeon.models.platforms.langfuse import (
    LangfuseCredentials,
    LangfusePrompt,
    LangfuseSourceConfig,
)


class TestLangfusePrompt:
    """Test cases for the LangfusePrompt model."""

    def test_langfuse_prompt_creation(self):
        """Test creating a LangfusePrompt with all fields."""
        created_at = datetime(2024, 1, 15, 10, 0, 0)
        updated_at = datetime(2024, 1, 16, 11, 0, 0)

        prompt = LangfusePrompt(
            id="lf-123",
            name="user/review-code",
            prompt="You are a code reviewer...",
            version=2,
            type="text",
            labels=["agentic-coding", "code-review"],
            tags=["technical"],
            created_at=created_at,
            updated_at=updated_at,
            config={"temperature": 0.3, "max_tokens": 1000},
        )

        assert prompt.id == "lf-123"
        assert prompt.name == "user/review-code"
        assert prompt.prompt == "You are a code reviewer..."
        assert prompt.version == 2
        assert prompt.type == "text"
        assert prompt.labels == ["agentic-coding", "code-review"]
        assert prompt.tags == ["technical"]
        assert prompt.created_at == created_at
        assert prompt.updated_at == updated_at
        assert prompt.config == {"temperature": 0.3, "max_tokens": 1000}

    def test_langfuse_prompt_defaults(self):
        """Test LangfusePrompt with default values."""
        created_at = datetime(2024, 1, 15, 10, 0, 0)
        updated_at = datetime(2024, 1, 16, 11, 0, 0)

        prompt = LangfusePrompt(
            id="lf-123",
            name="test-prompt",
            prompt="Test content",
            version=1,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert prompt.type == "text"
        assert prompt.labels == []
        assert prompt.tags == []
        assert prompt.config == {}

    def test_to_universal_prompt(self):
        """Test conversion to universal Prompt model."""
        created_at = datetime(2024, 1, 15, 10, 0, 0)
        updated_at = datetime(2024, 1, 16, 11, 0, 0)

        lf_prompt = LangfusePrompt(
            id="lf-123",
            name="user/review-code",
            prompt="You are a code reviewer...",
            version=2,
            labels=["agentic-coding", "code-review"],
            tags=["technical"],
            created_at=created_at,
            updated_at=updated_at,
            config={"temperature": 0.3},
        )

        universal = lf_prompt.to_universal_prompt()

        # Check basic fields
        assert isinstance(universal, Prompt)
        assert len(universal.id) == 36  # New UUID generated
        assert universal.name == "user/review-code"
        assert universal.content == "You are a code reviewer..."
        assert universal.created_at == created_at
        assert universal.updated_at == updated_at
        assert universal.version == "2"  # Converted to string

        # Check tags (should combine labels and tags)
        expected_tags = ["agentic-coding", "code-review", "technical"]
        assert set(universal.tags) == set(expected_tags)

        # Check source metadata
        assert universal.source_platform == "langfuse"
        assert universal.source_id == "lf-123"

        # Check preserved metadata
        assert universal.metadata["langfuse_version"] == 2
        assert universal.metadata["langfuse_type"] == "text"
        assert universal.metadata["langfuse_config"] == {"temperature": 0.3}
        assert universal.metadata["langfuse_labels"] == ["agentic-coding", "code-review"]

    def test_to_universal_prompt_deduplicates_tags(self):
        """Test that conversion deduplicates tags from labels and tags."""
        lf_prompt = LangfusePrompt(
            id="lf-123",
            name="test",
            prompt="test",
            version=1,
            labels=["technical", "code-review"],
            tags=["technical", "development"],  # "technical" appears in both
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        universal = lf_prompt.to_universal_prompt()

        # Should have unique tags only
        expected_tags = ["technical", "code-review", "development"]
        assert len(universal.tags) == 3
        assert set(universal.tags) == set(expected_tags)


class TestLangfuseCredentials:
    """Test cases for the LangfuseCredentials model."""

    def test_credentials_creation_with_host(self):
        """Test creating credentials with all fields."""
        creds = LangfuseCredentials(public_key="pk_123", secret_key="sk_456", host="https://cloud.langfuse.com")

        assert creds.public_key == "pk_123"
        assert creds.secret_key == "sk_456"
        assert creds.host == "https://cloud.langfuse.com"

    def test_credentials_creation_without_host(self):
        """Test creating credentials without host."""
        creds = LangfuseCredentials(public_key="pk_123", secret_key="sk_456")

        assert creds.public_key == "pk_123"
        assert creds.secret_key == "sk_456"
        assert creds.host is None

    def test_credentials_strips_whitespace(self):
        """Test that credentials strip whitespace."""
        creds = LangfuseCredentials(
            public_key="  pk_123  ", secret_key="  sk_456  ", host="  https://cloud.langfuse.com  "
        )

        assert creds.public_key == "pk_123"
        assert creds.secret_key == "sk_456"
        assert creds.host == "https://cloud.langfuse.com"


class TestLangfuseSourceConfig:
    """Test cases for the LangfuseSourceConfig model."""

    def test_source_config_creation_with_defaults(self):
        """Test creating source config with default values."""
        config = LangfuseSourceConfig(name="my-langfuse")

        assert config.name == "my-langfuse"
        assert config.type == "langfuse"
        assert config.enabled is True
        assert config.credentials is None
        assert config.tag_filter is None
        assert config.include_archived is False
        assert config.batch_size == 100

    def test_source_config_creation_with_all_fields(self):
        """Test creating source config with all fields."""
        creds = LangfuseCredentials(public_key="pk_123", secret_key="sk_456")
        config = LangfuseSourceConfig(
            name="my-langfuse",
            credentials=creds,
            enabled=False,
            tag_filter=["technical", "code-review"],
            include_archived=True,
            batch_size=50,
        )

        assert config.name == "my-langfuse"
        assert config.type == "langfuse"
        assert config.enabled is False
        assert config.credentials == creds
        assert config.tag_filter == ["technical", "code-review"]
        assert config.include_archived is True
        assert config.batch_size == 50
