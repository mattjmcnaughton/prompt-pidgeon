"""Configuration models for prompt-pidgeon.yml and environment variables."""

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from prompt_pidgeon.models.core import TagFilter
from prompt_pidgeon.models.platforms.coding_assistants import CodingAssistantSinkConfig
from prompt_pidgeon.models.platforms.filesystem import FilesystemSinkConfig
from prompt_pidgeon.models.platforms.langfuse import LangfuseSourceConfig
from prompt_pidgeon.models.platforms.openwebui import OpenWebUISinkConfig


class SyncJobConfig(BaseModel):
    """Configuration for a sync job."""

    name: str = Field(..., description="Human-readable name for this sync job")
    source: str = Field(..., description="Name of the source to sync from")
    sink: str = Field(..., description="Name of the sink to sync to")
    enabled: bool = Field(default=True, description="Whether this sync job is enabled")

    # Filtering
    filter: TagFilter | None = Field(None, description="Tag-based filtering for prompts")

    # Scheduling (for future use)
    schedule: str | None = Field(None, description="Cron-like schedule for automatic sync")

    # Sync behavior
    dry_run: bool = Field(default=False, description="Perform a dry run without making changes")
    force_update: bool = Field(default=False, description="Force update even if content hasn't changed")


class PidgeonConfig(BaseModel):
    """Main configuration model for prompt-pidgeon.yml."""

    version: str = Field(default="1", description="Configuration version")

    sources: list[LangfuseSourceConfig | BaseModel] = Field(default_factory=list, description="List of data sources")

    sinks: list[OpenWebUISinkConfig | FilesystemSinkConfig | CodingAssistantSinkConfig | BaseModel] = Field(
        default_factory=list, description="List of data sinks"
    )

    sync: list[SyncJobConfig] = Field(default_factory=list, description="List of sync jobs")

    # Global settings
    log_level: str = Field(default="INFO", description="Logging level")
    max_concurrent_jobs: int = Field(default=5, description="Maximum concurrent sync jobs")
    timeout_seconds: int = Field(default=300, description="Timeout for sync operations")

    def get_source_by_name(self, name: str) -> BaseModel | None:
        """Get a source configuration by name."""
        for source in self.sources:
            if hasattr(source, "name") and source.name == name:
                return source
        return None

    def get_sink_by_name(self, name: str) -> BaseModel | None:
        """Get a sink configuration by name."""
        for sink in self.sinks:
            if hasattr(sink, "name") and sink.name == name:
                return sink
        return None

    def get_enabled_sync_jobs(self) -> list[SyncJobConfig]:
        """Get all enabled sync jobs."""
        return [job for job in self.sync if job.enabled]


class EnvironmentSettings(BaseSettings):
    """Environment variable settings for prompt-pidgeon."""

    model_config = SettingsConfigDict(
        env_prefix="PROMPT_PIDGEON_", case_sensitive=False, env_file=".env", env_file_encoding="utf-8"
    )

    # Langfuse credentials
    langfuse_public_key: str | None = Field(default=None, description="Langfuse public key")
    langfuse_secret_key: str | None = Field(default=None, description="Langfuse secret key")
    langfuse_host: str | None = Field(default=None, description="Langfuse host URL")

    # Open-WebUI credentials
    open_webui_api_key: str | None = Field(default=None, description="Open-WebUI API key")
    open_webui_url: str | None = Field(default=None, description="Open-WebUI base URL")

    # Global settings
    config_file: str = Field(default="prompt-pidgeon.yml", description="Path to configuration file")
    log_level: str = Field(default="INFO", description="Global log level override")
    dry_run: bool = Field(default=False, description="Global dry run mode")


class ConfigManager:
    """Manager for loading and validating configuration."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path("prompt-pidgeon.yml")
        self.env_settings = EnvironmentSettings()

    def load_config(self) -> PidgeonConfig:
        """Load configuration from file and environment variables."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        # Load YAML configuration
        import yaml

        with open(self.config_path) as f:
            config_data = yaml.safe_load(f)

        # Create configuration object
        config = PidgeonConfig(**config_data)

        # Override with environment settings if provided
        if self.env_settings.log_level != "INFO":  # Only override if explicitly set
            config.log_level = self.env_settings.log_level

        return config

    def validate_config(self, config: PidgeonConfig) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Check that all sync jobs reference valid sources and sinks
        source_names = {getattr(source, "name", None) for source in config.sources}
        source_names.discard(None)
        sink_names = {getattr(sink, "name", None) for sink in config.sinks}
        sink_names.discard(None)

        for job in config.sync:
            if job.source not in source_names:
                errors.append(f"Sync job '{job.name}' references unknown source '{job.source}'")

            if job.sink not in sink_names:
                errors.append(f"Sync job '{job.name}' references unknown sink '{job.sink}'")

        # Check for duplicate names
        if len(source_names) != len(config.sources):
            errors.append("Duplicate source names found")

        if len(sink_names) != len(config.sinks):
            errors.append("Duplicate sink names found")

        return errors
