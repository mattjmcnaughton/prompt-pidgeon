# Project Initialization Plan

## Progress Tracking

**Completion Method**: ✅ = Complete, 🔄 = In Progress, ⏳ = Pending

### Completed Steps
- ✅ **Step 1** - Update pyproject.toml (Completed: 2024-12-19)
- ✅ **Step 1.1** - Write a simple proof-of-concept (Completed: 2024-12-19)
- ✅ **Step 2** - Create Justfile (Completed: 2024-12-19)
- ✅ **Step 2.1** - Create `pre-commit` (Completed: 2024-12-19)
- ✅ **Step 2.2** - Create `Dockerfile` for publishing container image (Completed: 2024-12-19)

### Current Status
- **Phase**: 1 - Project Infrastructure Setup
- **Next Step**: Step 3 - Configure CI/CD
- **Currently Working On**: Setting-up GitLab CI

## End State Description

The goal of this plan is to transform the current minimal `prompt-pidgeon` project into a fully-featured, production-ready Python application that adheres to all specified guidelines. The end state will include:

### Project Structure
- **Module Organization**: `prompt_pidgeon/` as the main Python module (top-level, sibling to `README.md`, `pyproject.toml`)
- **CLI Application**: Built with `typer` for command-line interface with primary command `prompt-pidgeon sync`
- **Library Support**: Importable as a Python library
- **Container Ready**: Dockerized for easy deployment

### Core Functionality
- **Prompt Management**: Handle system and user prompts with focus on most recent versions only
- **Platform Integration**: Extensible adapter pattern supporting:
  - **Sources**: Langfuse
  - **Sinks**: Filesystem/Git, Open-WebUI, Coding Assistants (Claude Code, Cursor)
- **Configuration**: `pidgeon.yml` for defining sync jobs with environment variable support for credentials
- **Tag-Based Filtering**: Support for filtering prompts by tags (e.g., `agentic-coding` for coding assistants)
- **Manual Sync**: Support for manual sync operations (no automated scheduling)

### Coding Assistant Integration
- **Claude Code**: Sync to `.md` files in `~/.claude/commands/` (global) or `./.claude/commands/` (project)
- **Cursor**: Sync to `.mdc` files with YAML frontmatter in `./.cursor/rules/` (project scope)
- **Planned Platforms**: Gemini CLI and OpenAI Codex (hard-fail with clear error messages in v1)
- **Scope Handling**: Support for global vs project-specific command placement

### Technical Standards
- **Code Quality**: Type annotations with `mypy`, formatting with `ruff`, minimal purposeful comments
- **Testing**: Three-tier testing structure (unit, integration, e2e) using `pytest` with class-based organization
- **Task Management**: `Justfile` with `lint`, `test`, `typecheck` targets
- **Logging**: `structlog` with trace IDs and structured logging
- **Dependencies**: Managed via `uv` with proper version constraints

### Development Infrastructure
- **Type Checking**: Complete `mypy` configuration with strict settings
- **Code Formatting**: `ruff` configuration for consistent code style
- **Testing Framework**: `pytest` with proper test discovery and organization
- **CI/CD Ready**: All tools configured for continuous integration

## Step-by-Step Implementation Plan

### Phase 1: Project Infrastructure Setup

#### ✅ Step 1: Update pyproject.toml
- ✅ Add complete project metadata and dependencies
- ✅ Configure all development tools (ruff, mypy, pytest)
- ✅ Set up project entry points for CLI and library usage
- ✅ Add proper dependency specifications

#### ✅ Step 1.1: Write a simple proof-of-concept
- ✅ In the `scripts` directory, create a `langfuse-poc.py`, an `open-webui-poc.py` and then a `e2e-poc.py`.
- ✅ Each PoC should be fully self-contained within a single file.

#### ✅ Step 2: Create Justfile
- ✅ Implement `lint`, `test`, `typecheck`, `fix` targets
- ✅ Add convenience targets for development workflow
- ✅ Ensure consistent task execution across environments

#### ✅ Step 2.1: Create `pre-commit`
- ✅ Use `pre-commit` to run `ruff`, `mypy`, etc... on commit.

#### ✅ Step 2.2: Create `Dockerfile` for publishing container image
- ✅ Use the base python image.
- ✅ Add Justfile commands.

#### Step 3: Configure CI/CD
- Set-up github actions for testing, linting, etc... on all MRs.
- Set-up github actions for publishing images on merge to `main`.

#### Step 4: Create Project Module Structure
- Create `prompt_pidgeon/` main module directory
- Set up proper `__init__.py` files
- Create subdirectories for core components:
  - `prompt_pidgeon/cli/` - CLI interface
  - `prompt_pidgeon/core/` - Core business logic
  - `prompt_pidgeon/adapters/` - Platform adapters (sources and sinks)
  - `prompt_pidgeon/config/` - Configuration management
  - `prompt_pidgeon/models/` - Data models

### Phase 2: Core Data Models and Configuration

#### Step 5: Create Data Models
- Define `Prompt` model using `pydantic` for type safety with metadata support
- Create platform-specific models for all supported platforms:
  - **Langfuse**: Source prompt models with tag support
  - **Open-WebUI**: Prompt and model destination formats
  - **Claude Code**: `.md` file format with metadata preservation
  - **Cursor**: `.mdc` format with YAML frontmatter structure
- Implement configuration models using `pydantic-settings` for `pidgeon.yml`
- Add tag filtering and scope resolution models
- Add proper type annotations throughout

#### Step 6: Configuration Management
- Create `pidgeon.yml` schema definition for declarative sync configuration
- Implement environment variable support for credentials:
  - Langfuse: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_URL`
  - Open-WebUI: `OPEN_WEBUI_API_KEY`, `OPEN_WEBUI_URL`
- Add configuration for sync routing with tag-based filtering:
  - Sources, sinks, and sync job definitions
  - Tag-based prompt filtering (e.g., `tag_filter: agentic-coding`)
  - Scope-based path resolution for coding assistants
- Add configuration validation and error handling
- Create example `pidgeon.yml` files for common use cases

#### Step 7: Logging Infrastructure
- Set up `structlog` configuration
- Implement trace ID generation for CLI and web contexts
- Create structured logging patterns with `snake_case` format
- Add proper log levels and formatting

### Phase 3: Platform Adapters

#### Step 8: Adapter Pattern Implementation
- Create base `PlatformAdapter` abstract classes for sources and sinks
- Define standard interface for platform operations (read/write)
- Implement error handling and retry logic
- Add adapter registration system for extensibility

#### Step 9: Langfuse Adapter (Source)
- Implement Langfuse adapter using the official `langfuse` Python library
- Create methods for fetching prompts with tag filtering support
- Add authentication using `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_URL` environment variables
- Implement prompt transformation logic from Langfuse format to internal format
- Support metadata preservation for bidirectional sync preparation

#### Step 10: Open-WebUI Adapter (Sink)
- Implement Open-WebUI API client using `httpx` for HTTP API calls
- Follow API specification documented in `.ai/resources/open-webui-api-spec.md`
- Create methods for both prompts and models based on source directory:
  - **User Prompts**: Langfuse prompts → Open-WebUI `/api/v1/prompts` endpoints
  - **System Prompts**: Langfuse prompts → Open-WebUI `/api/v1/models` endpoints (using prompt as system_prompt)
- Add Bearer Token authentication using `OPEN_WEBUI_API_KEY` and `OPEN_WEBUI_URL` environment variables
- Handle owner-based access control and proper HTTP status codes

#### Step 11: Coding Assistant Adapters (Sinks)
- **Claude Code Adapter**:
  - Support both global (`~/.claude/commands/`) and project (`./.claude/commands/`) scopes
  - Generate `.md` files with proper content formatting
  - Handle filename generation from prompt names/slugs
- **Cursor Adapter**:
  - Target `./.cursor/rules/` directory (project scope only)
  - Generate `.mdc` files with YAML frontmatter structure
  - Include proper frontmatter fields (description, globs, alwaysApply)
- **Unsupported Platform Handling**:
  - Implement graceful hard-fail for Gemini CLI and OpenAI Codex
  - Provide clear error messages directing users to future releases
  - Validate platform configuration at startup

#### Step 12: Filesystem Adapter (Sink)
- Implement filesystem adapter for local file output
- Support metadata preservation as YAML frontmatter
- Handle directory structure creation and file management
- Enable Git integration for version control

### Phase 4: Core Business Logic

#### Step 13: Sync Engine
- Create core sync orchestration logic with multi-sink support
- Implement tag-based filtering and routing logic
- Add comparison and update detection for different sink types
- Create sync result reporting with metrics per sink type
- Handle scope resolution for coding assistants (global vs project)

#### Step 14: CLI Interface
- Implement `typer`-based CLI application with `prompt-pidgeon sync` as primary command
- Create commands for listing, syncing, and configuring
- Add support for `pidgeon.yml` configuration file discovery
- Add proper help text and error messages for all platforms
- Implement structured output with separate reporting for each sink type

#### Step 15: Library Interface
- Create public API for library usage
- Implement proper error handling and exceptions
- Add comprehensive docstrings
- Create usage examples for both Open-WebUI and coding assistant scenarios

### Phase 5: Testing Infrastructure

#### Step 16: Unit Test Structure
- Create `tests/unit/` directory with proper organization
- Implement tests for all core models and utilities
- Create mock objects for external dependencies
- Test tag filtering, scope resolution, and file format generation
- Ensure 100% coverage of business logic

#### Step 17: Integration Tests
- Create `tests/integration/` directory
- Implement tests for adapter interactions
- Create test fixtures for realistic scenarios including coding assistants
- Add database and API mocking where appropriate
- Test `pidgeon.yml` configuration parsing and validation

#### Step 18: End-to-End Tests
- Create `tests/e2e/` directory
- Implement full workflow testing for all sink types
- Create test configurations and environments
- Test actual file creation for coding assistants
- Add performance and reliability tests

### Phase 6: Documentation and Deployment

#### Step 19: Documentation
- Update README.md with comprehensive usage instructions
- Create `pidgeon.yml` configuration examples for common use cases
- Add platform-specific setup guides (Claude Code, Cursor, Open-WebUI)
- Document tag-based filtering and scope configuration
- Create troubleshooting section with platform-specific issues

#### Step 20: Docker Configuration
- Create Dockerfile for CLI application
- Set up docker-compose for development
- Configure environment variable handling
- Add health checks and proper logging

#### Step 21: Final Quality Assurance
- Run complete test suite and ensure all tests pass
- Verify type checking with `mypy` strict mode
- Confirm code formatting with `ruff`
- Perform end-to-end testing with real APIs and file system
- Test coding assistant integration with actual command creation

#### Step 22: Commit and Tag
- Create comprehensive commit with conventional commit format
- Add proper commit message describing the complete initialization
- Tag the release as `v0.1.0`
- Push to repository with proper branch protection

## Success Criteria

At completion, the project will:
- ✅ Pass all linting, type checking, and formatting checks
- ✅ Have comprehensive test coverage across all three test categories
- ✅ Successfully sync prompts between Langfuse and all supported sinks (Open-WebUI, Claude Code, Cursor, Filesystem)
- ✅ Support tag-based filtering and scope-based routing
- ✅ Generate proper file formats for coding assistants (.md for Claude Code, .mdc for Cursor)
- ✅ Handle unsupported platforms gracefully with clear error messages
- ✅ Support both CLI and library usage patterns
- ✅ Be deployable as a container
- ✅ Follow all specified coding standards and conventions
- ✅ Have proper error handling and logging throughout
- ✅ Use `pidgeon.yml` for declarative configuration
- ✅ Be ready for production use and further development

## Risk Mitigation

- **API Changes**: Implement robust error handling and version detection
- **Authentication**: Secure credential management with environment variables
- **File System Access**: Proper error handling for directory creation and file permissions
- **Platform Differences**: Isolated adapters for each coding assistant platform
- **Configuration Complexity**: Comprehensive validation of `pidgeon.yml` structure
- **Performance**: Implement proper connection pooling and rate limiting
- **Maintainability**: Follow established patterns and maintain comprehensive tests
- **Extensibility**: Design adapter pattern to support future platform additions (Gemini CLI, OpenAI Codex)
