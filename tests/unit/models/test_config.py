"""Unit tests for configuration models."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from prompt_pidgeon.models.config import (
    ConfigManager,
    EnvironmentSettings,
    PidgeonConfig,
    SyncJobConfig,
)
from prompt_pidgeon.models.core import TagFilter
from prompt_pidgeon.models.platforms.filesystem import FilesystemSinkConfig
from prompt_pidgeon.models.platforms.langfuse import LangfuseSourceConfig
from prompt_pidgeon.models.platforms.openwebui import OpenWebUISinkConfig


class TestSyncJobConfig:
    """Test cases for the SyncJobConfig model."""

    def test_sync_job_config_creation(self):
        """Test creating a sync job config."""
        tag_filter = TagFilter(include_tags=["technical"], require_all=True)

        config = SyncJobConfig(
            name="Sync technical prompts",
            source="my-langfuse",
            sink="cursor-rules",
            enabled=False,
            filter=tag_filter,
            schedule="0 */6 * * *",
            dry_run=True,
            force_update=True,
        )

        assert config.name == "Sync technical prompts"
        assert config.source == "my-langfuse"
        assert config.sink == "cursor-rules"
        assert config.enabled is False
        assert config.filter == tag_filter
        assert config.schedule == "0 */6 * * *"
        assert config.dry_run is True
        assert config.force_update is True

    def test_sync_job_config_defaults(self):
        """Test sync job config with default values."""
        config = SyncJobConfig(name="Test sync", source="test-source", sink="test-sink")

        assert config.enabled is True
        assert config.filter is None
        assert config.schedule is None
        assert config.dry_run is False
        assert config.force_update is False


class TestPidgeonConfig:
    """Test cases for the PidgeonConfig model."""

    def test_pidgeon_config_creation(self):
        """Test creating a complete Pidgeon config."""
        langfuse_source = LangfuseSourceConfig(name="my-langfuse")
        openwebui_sink = OpenWebUISinkConfig(name="my-openwebui")
        sync_job = SyncJobConfig(name="Test sync", source="my-langfuse", sink="my-openwebui")

        config = PidgeonConfig(
            version="2",
            sources=[langfuse_source],
            sinks=[openwebui_sink],
            sync=[sync_job],
            log_level="DEBUG",
            max_concurrent_jobs=10,
            timeout_seconds=600,
        )

        assert config.version == "2"
        assert len(config.sources) == 1
        assert len(config.sinks) == 1
        assert len(config.sync) == 1
        assert config.log_level == "DEBUG"
        assert config.max_concurrent_jobs == 10
        assert config.timeout_seconds == 600

    def test_pidgeon_config_defaults(self):
        """Test Pidgeon config with default values."""
        config = PidgeonConfig()

        assert config.version == "1"
        assert config.sources == []
        assert config.sinks == []
        assert config.sync == []
        assert config.log_level == "INFO"
        assert config.max_concurrent_jobs == 5
        assert config.timeout_seconds == 300

    def test_get_source_by_name(self):
        """Test getting source by name."""
        source1 = LangfuseSourceConfig(name="source1")
        source2 = LangfuseSourceConfig(name="source2")

        config = PidgeonConfig(sources=[source1, source2])

        assert config.get_source_by_name("source1") == source1
        assert config.get_source_by_name("source2") == source2
        assert config.get_source_by_name("nonexistent") is None

    def test_get_sink_by_name(self):
        """Test getting sink by name."""
        sink1 = OpenWebUISinkConfig(name="sink1")
        sink2 = FilesystemSinkConfig(name="sink2", path=Path("/tmp"))

        config = PidgeonConfig(sinks=[sink1, sink2])

        assert config.get_sink_by_name("sink1") == sink1
        assert config.get_sink_by_name("sink2") == sink2
        assert config.get_sink_by_name("nonexistent") is None

    def test_get_enabled_sync_jobs(self):
        """Test getting enabled sync jobs."""
        job1 = SyncJobConfig(name="job1", source="s1", sink="k1", enabled=True)
        job2 = SyncJobConfig(name="job2", source="s2", sink="k2", enabled=False)
        job3 = SyncJobConfig(name="job3", source="s3", sink="k3", enabled=True)

        config = PidgeonConfig(sync=[job1, job2, job3])

        enabled_jobs = config.get_enabled_sync_jobs()
        assert len(enabled_jobs) == 2
        assert job1 in enabled_jobs
        assert job3 in enabled_jobs
        assert job2 not in enabled_jobs


class TestEnvironmentSettings:
    """Test cases for the EnvironmentSettings model."""

    def test_environment_settings_defaults(self):
        """Test environment settings with default values."""
        with patch.dict("os.environ", {}, clear=True):
            settings = EnvironmentSettings()

            assert settings.langfuse_public_key is None
            assert settings.langfuse_secret_key is None
            assert settings.langfuse_url is None
            assert settings.open_webui_api_key is None
            assert settings.open_webui_url is None
            assert settings.config_file == "prompt-pidgeon.yml"
            assert settings.log_level == "INFO"
            assert settings.dry_run is False

    def test_environment_settings_from_prefixed_env(self):
        """Test environment settings from prefixed environment variables (preferred)."""
        env_vars = {
            "PROMPT_PIDGEON_LANGFUSE_PUBLIC_KEY": "pk_123",
            "PROMPT_PIDGEON_LANGFUSE_SECRET_KEY": "sk_456",
            "PROMPT_PIDGEON_LANGFUSE_URL": "https://cloud.langfuse.com",
            "PROMPT_PIDGEON_OPEN_WEBUI_API_KEY": "owui_789",
            "PROMPT_PIDGEON_OPEN_WEBUI_URL": "https://my-openwebui.com",
            "PROMPT_PIDGEON_CONFIG_FILE": "custom-config.yml",
            "PROMPT_PIDGEON_LOG_LEVEL": "DEBUG",
            "PROMPT_PIDGEON_DRY_RUN": "true",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = EnvironmentSettings()

            assert settings.langfuse_public_key == "pk_123"
            assert settings.langfuse_secret_key == "sk_456"
            assert settings.langfuse_url == "https://cloud.langfuse.com"
            assert settings.open_webui_api_key == "owui_789"
            assert settings.open_webui_url == "https://my-openwebui.com"
            assert settings.config_file == "custom-config.yml"
            assert settings.log_level == "DEBUG"
            assert settings.dry_run is True

    def test_environment_settings_from_direct_env(self):
        """Test environment settings from direct environment variables (fallback)."""
        env_vars = {
            "LANGFUSE_PUBLIC_KEY": "pk_direct",
            "LANGFUSE_SECRET_KEY": "sk_direct",
            "LANGFUSE_URL": "https://direct.langfuse.com",
            "OPEN_WEBUI_API_KEY": "owui_direct",
            "OPEN_WEBUI_URL": "https://direct-openwebui.com",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = EnvironmentSettings()

            assert settings.langfuse_public_key == "pk_direct"
            assert settings.langfuse_secret_key == "sk_direct"
            assert settings.langfuse_url == "https://direct.langfuse.com"
            assert settings.open_webui_api_key == "owui_direct"
            assert settings.open_webui_url == "https://direct-openwebui.com"

    def test_environment_settings_preference_system(self):
        """Test that prefixed variables take precedence over direct ones."""
        env_vars = {
            # Both prefixed and direct variables set
            "PROMPT_PIDGEON_LANGFUSE_PUBLIC_KEY": "pk_prefixed",
            "LANGFUSE_PUBLIC_KEY": "pk_direct",
            "PROMPT_PIDGEON_LANGFUSE_SECRET_KEY": "sk_prefixed",
            "LANGFUSE_SECRET_KEY": "sk_direct",
            "PROMPT_PIDGEON_OPEN_WEBUI_API_KEY": "owui_prefixed",
            "OPEN_WEBUI_API_KEY": "owui_direct",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = EnvironmentSettings()

            # Prefixed variables should take precedence
            assert settings.langfuse_public_key == "pk_prefixed"
            assert settings.langfuse_secret_key == "sk_prefixed"
            assert settings.open_webui_api_key == "owui_prefixed"

    def test_environment_settings_mixed_variables(self):
        """Test mixed environment variables (some prefixed, some direct)."""
        env_vars = {
            "PROMPT_PIDGEON_LANGFUSE_PUBLIC_KEY": "pk_prefixed",
            "LANGFUSE_SECRET_KEY": "sk_direct",  # Only direct available
            "OPEN_WEBUI_API_KEY": "owui_direct",  # Only direct available
            "PROMPT_PIDGEON_OPEN_WEBUI_URL": "https://prefixed-openwebui.com",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = EnvironmentSettings()

            assert settings.langfuse_public_key == "pk_prefixed"  # Prefixed available
            assert settings.langfuse_secret_key == "sk_direct"  # Only direct available
            assert settings.open_webui_api_key == "owui_direct"  # Only direct available
            assert settings.open_webui_url == "https://prefixed-openwebui.com"  # Prefixed available

    def test_environment_settings_langfuse_host_backward_compatibility(self):
        """Test backward compatibility with LANGFUSE_HOST variable."""
        env_vars = {
            "LANGFUSE_HOST": "https://legacy.langfuse.com",  # Old HOST variable
            "PROMPT_PIDGEON_LANGFUSE_HOST": "https://legacy-prefixed.langfuse.com",  # Old prefixed HOST
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = EnvironmentSettings()

            # Should fall back to HOST variables when URL not available
            assert settings.langfuse_url == "https://legacy-prefixed.langfuse.com"  # Prefixed HOST preferred

    def test_environment_settings_url_precedence_over_host(self):
        """Test that URL variables take precedence over HOST variables."""
        env_vars = {
            "LANGFUSE_URL": "https://url.langfuse.com",
            "LANGFUSE_HOST": "https://host.langfuse.com",
            "PROMPT_PIDGEON_LANGFUSE_URL": "https://prefixed-url.langfuse.com",
            "PROMPT_PIDGEON_LANGFUSE_HOST": "https://prefixed-host.langfuse.com",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = EnvironmentSettings()

            # Prefixed URL should take highest precedence
            assert settings.langfuse_url == "https://prefixed-url.langfuse.com"

    def test_environment_settings_dry_run_boolean_parsing(self):
        """Test dry_run boolean parsing from environment variables."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("invalid", False),
        ]

        for env_value, expected in test_cases:
            env_vars = {"PROMPT_PIDGEON_DRY_RUN": env_value}
            with patch.dict("os.environ", env_vars, clear=True):
                settings = EnvironmentSettings()
                assert settings.dry_run == expected, f"Failed for value: {env_value}"


class TestConfigManager:
    """Test cases for the ConfigManager class."""

    def test_config_manager_creation(self):
        """Test creating a config manager."""
        manager = ConfigManager()

        assert manager.config_path == Path("prompt-pidgeon.yml")
        assert isinstance(manager.env_settings, EnvironmentSettings)

    def test_config_manager_custom_path(self):
        """Test creating config manager with custom path."""
        custom_path = Path("/home/user/custom-config.yml")
        manager = ConfigManager(custom_path)

        assert manager.config_path == custom_path

    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        manager = ConfigManager(Path("nonexistent.yml"))

        with pytest.raises(FileNotFoundError):
            manager.load_config()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
version: "1"
sources:
  - name: my-langfuse
    type: langfuse
    batch_size: 50
sinks:
  - name: my-openwebui
    type: open-webui
    command_prefix: dev
sync:
  - name: Test sync
    source: my-langfuse
    sink: my-openwebui
log_level: DEBUG
""",
    )
    @patch("pathlib.Path.exists", return_value=True)
    @patch.dict("os.environ", {}, clear=True)  # Clear env vars to avoid override
    def test_load_config_success(self, mock_exists, mock_file):
        """Test successfully loading config from file."""
        manager = ConfigManager()
        config = manager.load_config()

        assert isinstance(config, PidgeonConfig)
        assert config.version == "1"
        assert len(config.sources) == 1
        assert len(config.sinks) == 1
        assert len(config.sync) == 1
        assert config.log_level == "DEBUG"

        # Check sync job
        job = config.sync[0]
        assert job.name == "Test sync"
        assert job.source == "my-langfuse"
        assert job.sink == "my-openwebui"

    def test_validate_config_valid(self):
        """Test validating a valid configuration."""
        source = LangfuseSourceConfig(name="source1")
        sink = OpenWebUISinkConfig(name="sink1")
        job = SyncJobConfig(name="job1", source="source1", sink="sink1")

        config = PidgeonConfig(sources=[source], sinks=[sink], sync=[job])

        manager = ConfigManager()
        errors = manager.validate_config(config)

        assert errors == []

    def test_validate_config_unknown_source(self):
        """Test validating config with unknown source reference."""
        sink = OpenWebUISinkConfig(name="sink1")
        job = SyncJobConfig(name="job1", source="unknown-source", sink="sink1")

        config = PidgeonConfig(sinks=[sink], sync=[job])

        manager = ConfigManager()
        errors = manager.validate_config(config)

        assert len(errors) == 1
        assert "unknown source 'unknown-source'" in errors[0]

    def test_validate_config_unknown_sink(self):
        """Test validating config with unknown sink reference."""
        source = LangfuseSourceConfig(name="source1")
        job = SyncJobConfig(name="job1", source="source1", sink="unknown-sink")

        config = PidgeonConfig(sources=[source], sync=[job])

        manager = ConfigManager()
        errors = manager.validate_config(config)

        assert len(errors) == 1
        assert "unknown sink 'unknown-sink'" in errors[0]
