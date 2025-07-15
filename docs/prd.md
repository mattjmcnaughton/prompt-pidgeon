# Lightweight PRD: prompt-pidgeon

*Your prompts, everywhere.*

### 1. Tool Summary
`prompt-pidgeon` is a CLI tool for synchronizing LLM prompts between different platforms and formats. It acts as a universal adapter, allowing users to maintain a single source of truth for prompts while ensuring consistency and eliminating tedious manual updates across their entire toolchain.

### 2. Goals & Objectives
*   **Efficiency:** Automate the distribution of prompts to downstream systems, eliminating error-prone copy-pasting and saving user time.
*   **Consistency:** Ensure all personal AI applications and development environments use the correct, version-controlled prompts from a central, authoritative source.

### 3. Users & Use Cases
*   **Target Audience:** AI-savvy users (developers, researchers, power-users) who actively build with or iterate on LLMs and use a diverse set of AI-powered tools.

*   **Primary Use Case (Personalized Tooling Sync):** "As an AI-savvy user, I want to sync my curated set of prompts, identified by specific tags in a central library like Langfuse, to all my end-user AI tools. This allows me to use my preferred technical prompts as custom commands in my IDE (e.g., Cursor) and my favorite general-purpose prompts in my chat UI (e.g., Open WebUI), ensuring my personalized toolkit is always up-to-date everywhere."

*   **Secondary Use Case (Coding Assistant Integration):** "As a developer, I want to sync my specialized coding prompts tagged with 'agentic-coding' from Langfuse to my coding assistants (Claude Code, Cursor) so I can use them as slash commands like `/create-code-review` directly in my development environment."

### 4. Core Functionality & Features
*   **Declarative Sync Configuration:** The core of the tool is a `pidgeon.yml` file where the user defines `sources`, `sinks`, and `sync` jobs. This provides a clear, version-controllable definition of the entire workflow.
*   **Simple CLI Interface:** The primary interaction is a single command: `prompt-pidgeon sync`. This command reads the configuration file from the current directory and executes all defined sync operations.
*   **Pluggable Architecture:** The tool is built around two concepts:
    *   **Sources:** Where prompts originate (e.g., Langfuse, Filesystem).
    *   **Sinks:** Where prompts are sent (e.g., Open WebUI, Filesystem, Coding Assistants).
*   **Metadata Preservation & Tagging:**
    *   When syncing from a structured source like Langfuse to a filesystem, the tool persists metadata (e.g., `langfuse_id`, `version`, `tags`) as YAML frontmatter within the prompt's text file. This is critical for preventing data loss and enabling bidirectional sync.
    *   When filtering, the tool can use tags from the source platform to select specific prompts for a given sink.

### 5. Technical Considerations
*   **Tech Stack/Frameworks:** Python, `uvx`, `httpx`, `langfuse`, `Pydantic`, `Typer`.
*   **Configuration:** `pidgeon.yml` for defining sync jobs. Environment variables for secrets (`LANGFUSE_SECRET_KEY`, etc.).
*   **Integrations (v1):**
    *   **Sources:** Langfuse
    *   **Sinks:** Filesystem/Git, Open WebUI, Coding Assistants
        *   **Coding Assistant Platforms (v1):** Claude Code, Cursor
        *   **Coding Assistant Platforms (planned):** Gemini CLI, OpenAI Codex

### 6. Constraints & Limitations
*   **MVP Scope:** v1 focuses on one-way sync *from* Langfuse *to* Filesystem/Git, Open WebUI, and supported coding assistants.
*   **Authentication:** Assumes API key authentication for all services. No OAuth support in v1.
*   **Data Format:** Supports text-only prompts. No support for multi-modal prompts (images, etc.) in v1.
*   **Coding Assistant Support:** v1 includes full support for Claude Code (`.md` files in `~/.claude/commands/` or `./.claude/commands/`) and Cursor (`.mdc` files with YAML frontmatter in `./.cursor/rules/`). Gemini CLI and OpenAI Codex are configuration options but will hard-fail with clear error messages directing users to future releases.
*   **Roadmap Note (v1.1):** The immediate next priority after launch is to support **bidirectional sync**, specifically enabling Filesystem/Git as a source and Langfuse as a sink. The frontmatter metadata design is the explicit foundation for this feature.

### 7. Success Criteria
*   **Functional:** The `prompt-pidgeon sync` command successfully and accurately completes the sync operations defined in the primary use case (e.g., Langfuse -> Filesystem, Langfuse -> Open WebUI, Langfuse -> Coding Assistants) using a `pidgeon.yml` configuration and tag-based filtering.
*   **Coding Assistant Integration:** Tagged prompts from Langfuse successfully sync to Claude Code and Cursor in their respective formats and directory structures, enabling immediate use as slash commands.
