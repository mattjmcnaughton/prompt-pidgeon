"""Unit tests for Open-WebUI platform models."""

from prompt_pidgeon.models.config import (
    OpenWebUISinkConfig,
)
from prompt_pidgeon.models.core import Prompt
from prompt_pidgeon.models.platforms.openwebui import (
    OpenWebUICredentials,
    OpenWebUIModel,
    OpenWebUIUserPrompt,
)


class TestOpenWebUIUserPrompt:
    """Test cases for the OpenWebUIUserPrompt model."""

    def test_user_prompt_creation(self):
        """Test creating an OpenWebUI user prompt."""
        prompt = OpenWebUIUserPrompt(
            command="/lf-review-code",
            title="Review Code",
            content="You are a code reviewer. Analyze: {{code}}",
            access_control={"owner": "user123"},
        )

        assert prompt.command == "/lf-review-code"
        assert prompt.title == "Review Code"
        assert prompt.content == "You are a code reviewer. Analyze: {{code}}"
        assert prompt.access_control == {"owner": "user123"}

    def test_user_prompt_defaults(self):
        """Test OpenWebUI user prompt with default values."""
        prompt = OpenWebUIUserPrompt(command="/test", title="Test", content="Test content")

        assert prompt.access_control == {}

    def test_from_universal_prompt_default_prefix(self):
        """Test creating from universal prompt with default prefix."""
        universal = Prompt(name="user/review-code", content="You are a code reviewer...")

        user_prompt = OpenWebUIUserPrompt.from_universal_prompt(universal)

        assert user_prompt.command == "/lf-user/review-code"
        assert user_prompt.title == "user/review-code"
        assert user_prompt.content == "You are a code reviewer..."
        assert user_prompt.access_control == {}

    def test_from_universal_prompt_custom_prefix(self):
        """Test creating from universal prompt with custom prefix."""
        universal = Prompt(name="user/improve-writing", content="You are a writing assistant...")

        user_prompt = OpenWebUIUserPrompt.from_universal_prompt(universal, command_prefix="dev")

        assert user_prompt.command == "/dev-user/improve-writing"
        assert user_prompt.title == "user/improve-writing"
        assert user_prompt.content == "You are a writing assistant..."

    def test_from_universal_prompt_name_normalization(self):
        """Test that spaces and underscores are converted to hyphens."""
        universal = Prompt(name="user/My Complex_Prompt Name", content="Test content")

        user_prompt = OpenWebUIUserPrompt.from_universal_prompt(universal)

        assert user_prompt.command == "/lf-user/my-complex-prompt-name"


class TestOpenWebUIModel:
    """Test cases for the OpenWebUIModel model."""

    def test_model_creation(self):
        """Test creating an OpenWebUI model."""
        model = OpenWebUIModel(
            id="sme-test-model",
            name="sme-test-model",
            base_model_id="anthropic-claude-4-sonnet",
            params={"system": "You are a helpful assistant"},
            is_active=True,
            meta={"description": "Test model"},
            tags=["test", "prompt-pidgeon-managed"],
        )

        assert model.id == "sme-test-model"
        assert model.name == "sme-test-model"
        assert model.base_model_id == "anthropic-claude-4-sonnet"
        assert model.params == {"system": "You are a helpful assistant"}
        assert model.is_active is True
        assert model.meta == {"description": "Test model"}
        assert model.tags == ["test", "prompt-pidgeon-managed"]

    def test_model_defaults(self):
        """Test OpenWebUI model with default values."""
        model = OpenWebUIModel(name="test-model", base_model_id="test-base")

        assert len(model.id) == 36  # UUID string
        assert model.is_active is True
        assert model.params == {}
        assert model.meta == {}
        assert model.tags == []

    def test_from_universal_prompt_defaults(self):
        """Test creating from universal prompt with defaults."""
        universal = Prompt(
            name="system/design-expert", content="You are a system architect...", tags=["technical", "architecture"]
        )

        model = OpenWebUIModel.from_universal_prompt(universal, base_model_id="anthropic-claude-4-sonnet")

        assert model.id == "sme-system/design-expert-default"
        assert model.name == "sme-system/design-expert-default"
        assert model.base_model_id == "anthropic-claude-4-sonnet"
        assert model.params == {"system": "You are a system architect..."}
        assert model.is_active is True
        assert model.meta == {}
        expected_tags = ["prompt-pidgeon-managed", "technical", "architecture"]
        assert set(model.tags) == set(expected_tags)

    def test_from_universal_prompt_custom_params(self):
        """Test creating from universal prompt with custom parameters."""
        universal = Prompt(name="system/code-reviewer", content="You are a code reviewer...", tags=["development"])

        model = OpenWebUIModel.from_universal_prompt(
            universal, base_model_id="google-gemini-2.5-flash", model_prefix="dev", base_model_short="gemini"
        )

        assert model.id == "dev-system/code-reviewer-gemini"
        assert model.name == "dev-system/code-reviewer-gemini"
        assert model.base_model_id == "google-gemini-2.5-flash"
        assert model.params == {"system": "You are a code reviewer..."}
        expected_tags = ["prompt-pidgeon-managed", "development"]
        assert set(model.tags) == set(expected_tags)


class TestOpenWebUICredentials:
    """Test cases for the OpenWebUICredentials model."""

    def test_credentials_creation(self):
        """Test creating OpenWebUI credentials."""
        creds = OpenWebUICredentials(api_key="owui_123456", base_url="https://my-openwebui.com")

        assert creds.api_key == "owui_123456"
        assert creds.base_url == "https://my-openwebui.com"

    def test_credentials_strips_whitespace(self):
        """Test that credentials strip whitespace."""
        creds = OpenWebUICredentials(api_key="  owui_123456  ", base_url="  https://my-openwebui.com  ")

        assert creds.api_key == "owui_123456"
        assert creds.base_url == "https://my-openwebui.com"


class TestOpenWebUISinkConfig:
    """Test cases for the OpenWebUISinkConfig model."""

    def test_sink_config_defaults(self):
        """Test creating sink config with default values."""
        config = OpenWebUISinkConfig(name="my-openwebui")

        assert config.name == "my-openwebui"
        assert config.type == "open-webui"
        assert config.enabled is True
        assert config.credentials is None
        assert config.prompt_type == "user"
        assert config.command_prefix == "lf"
        assert config.base_models == []
        assert config.model_prefix == "sme"

    def test_sink_config_all_fields(self):
        """Test creating sink config with all fields."""
        creds = OpenWebUICredentials(api_key="test_key", base_url="https://test.com")

        config = OpenWebUISinkConfig(
            name="my-openwebui",
            credentials=creds,
            enabled=False,
            prompt_type="system",
            command_prefix="dev",
            base_models=["anthropic-claude-4-sonnet", "google-gemini-2.5-flash"],
            model_prefix="custom",
        )

        assert config.name == "my-openwebui"
        assert config.type == "open-webui"
        assert config.enabled is False
        assert config.credentials == creds
        assert config.prompt_type == "system"
        assert config.command_prefix == "dev"
        assert config.base_models == ["anthropic-claude-4-sonnet", "google-gemini-2.5-flash"]
        assert config.model_prefix == "custom"
