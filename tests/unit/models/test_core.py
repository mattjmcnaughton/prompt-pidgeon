"""Unit tests for core data models."""

from datetime import datetime

from prompt_pidgeon.models.core import Prompt, SyncScope, TagFilter


class TestPrompt:
    """Test cases for the Prompt model."""

    def test_prompt_creation_with_defaults(self):
        """Test creating a prompt with minimal required fields."""
        prompt = Prompt(name="test-prompt", content="Test content")

        assert prompt.name == "test-prompt"
        assert prompt.content == "Test content"
        assert isinstance(prompt.id, str)
        assert len(prompt.id) == 36  # UUID string length
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)
        assert prompt.tags == []
        assert prompt.version == "1"
        assert prompt.source_platform is None
        assert prompt.source_id is None
        assert prompt.metadata == {}

    def test_prompt_creation_with_all_fields(self):
        """Test creating a prompt with all fields specified."""
        created_at = datetime(2024, 1, 15, 10, 0, 0)
        updated_at = datetime(2024, 1, 16, 11, 0, 0)

        prompt = Prompt(
            id="custom-id-123",
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

        assert prompt.id == "custom-id-123"
        assert prompt.name == "user/review-code"
        assert prompt.content == "You are a code reviewer..."
        assert prompt.tags == ["technical", "code-review"]
        assert prompt.created_at == created_at
        assert prompt.updated_at == updated_at
        assert prompt.version == "2"
        assert prompt.source_platform == "langfuse"
        assert prompt.source_id == "lf-123"
        assert prompt.metadata == {"temperature": 0.3}

    def test_has_tag(self):
        """Test the has_tag method."""
        prompt = Prompt(name="test", content="test", tags=["technical", "code-review"])

        assert prompt.has_tag("technical") is True
        assert prompt.has_tag("code-review") is True
        assert prompt.has_tag("nonexistent") is False

    def test_has_any_tags(self):
        """Test the has_any_tags method."""
        prompt = Prompt(name="test", content="test", tags=["technical", "code-review"])

        assert prompt.has_any_tags(["technical"]) is True
        assert prompt.has_any_tags(["technical", "writing"]) is True
        assert prompt.has_any_tags(["writing", "general"]) is False
        assert prompt.has_any_tags([]) is False

    def test_has_all_tags(self):
        """Test the has_all_tags method."""
        prompt = Prompt(name="test", content="test", tags=["technical", "code-review", "development"])

        assert prompt.has_all_tags(["technical"]) is True
        assert prompt.has_all_tags(["technical", "code-review"]) is True
        assert prompt.has_all_tags(["technical", "code-review", "development"]) is True
        assert prompt.has_all_tags(["technical", "nonexistent"]) is False
        assert prompt.has_all_tags([]) is True


class TestTagFilter:
    """Test cases for the TagFilter model."""

    def test_tag_filter_creation_with_defaults(self):
        """Test creating a TagFilter with default values."""
        filter = TagFilter()

        assert filter.include_tags == []
        assert filter.exclude_tags == []
        assert filter.require_all is False

    def test_tag_filter_creation_with_values(self):
        """Test creating a TagFilter with specified values."""
        filter = TagFilter(include_tags=["technical", "code-review"], exclude_tags=["deprecated"], require_all=True)

        assert filter.include_tags == ["technical", "code-review"]
        assert filter.exclude_tags == ["deprecated"]
        assert filter.require_all is True

    def test_matches_with_include_tags_any(self):
        """Test matching with include tags (require_all=False)."""
        filter = TagFilter(include_tags=["technical", "writing"], require_all=False)

        # Should match if has any of the include tags
        prompt1 = Prompt(name="test1", content="test", tags=["technical"])
        prompt2 = Prompt(name="test2", content="test", tags=["writing", "general"])
        prompt3 = Prompt(name="test3", content="test", tags=["general"])

        assert filter.matches(prompt1) is True
        assert filter.matches(prompt2) is True
        assert filter.matches(prompt3) is False

    def test_matches_with_include_tags_all(self):
        """Test matching with include tags (require_all=True)."""
        filter = TagFilter(include_tags=["technical", "code-review"], require_all=True)

        # Should match only if has all include tags
        prompt1 = Prompt(name="test1", content="test", tags=["technical", "code-review"])
        prompt2 = Prompt(name="test2", content="test", tags=["technical", "code-review", "development"])
        prompt3 = Prompt(name="test3", content="test", tags=["technical"])

        assert filter.matches(prompt1) is True
        assert filter.matches(prompt2) is True
        assert filter.matches(prompt3) is False

    def test_matches_with_exclude_tags(self):
        """Test matching with exclude tags."""
        filter = TagFilter(include_tags=["technical"], exclude_tags=["deprecated", "experimental"])

        # Should not match if has any exclude tags
        prompt1 = Prompt(name="test1", content="test", tags=["technical"])
        prompt2 = Prompt(name="test2", content="test", tags=["technical", "deprecated"])
        prompt3 = Prompt(name="test3", content="test", tags=["technical", "experimental"])

        assert filter.matches(prompt1) is True
        assert filter.matches(prompt2) is False
        assert filter.matches(prompt3) is False

    def test_matches_empty_filter(self):
        """Test matching with empty filter (should match all)."""
        filter = TagFilter()

        prompt1 = Prompt(name="test1", content="test", tags=["technical"])
        prompt2 = Prompt(name="test2", content="test", tags=[])

        assert filter.matches(prompt1) is True
        assert filter.matches(prompt2) is True


class TestSyncScope:
    """Test cases for the SyncScope model."""

    def test_sync_scope_global(self):
        """Test creating a global scope."""
        scope = SyncScope(scope_type="global")

        assert scope.scope_type == "global"
        assert scope.path is None
        assert scope.is_global is True
        assert scope.is_project is False

    def test_sync_scope_project(self):
        """Test creating a project scope."""
        scope = SyncScope(scope_type="project", path="/home/user/project")

        assert scope.scope_type == "project"
        assert scope.path == "/home/user/project"
        assert scope.is_global is False
        assert scope.is_project is True

    def test_sync_scope_project_without_path(self):
        """Test creating a project scope without path."""
        scope = SyncScope(scope_type="project")

        assert scope.scope_type == "project"
        assert scope.path is None
        assert scope.is_global is False
        assert scope.is_project is True
