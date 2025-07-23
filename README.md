# prompt-pidgeon

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Description

`prompt-pidgeon` is a CLI tool for synchronizing LLM prompts between different platforms and formats. It acts as a universal adapter, allowing users to maintain a single source of truth for prompts while ensuring consistency and eliminating tedious manual updates across their entire toolchain.

## Key Features

*   Configure sync jobs declaratively using a simple `prompt-pidgeon.yml` file.
*   Execute all synchronization tasks with a single `prompt-pidgeon sync` command.
*   Pluggable architecture supporting various `sources` (like Langfuse) and `sinks` (like Open WebUI or a local filesystem).
*   Preserve critical metadata and use tags to filter which prompts get synced to specific destinations.

## Installation

1.  Install the package using uvx:

```
uv tool install prompt-pidgeon
```

2.  Create a configuration file in your project root:

```
touch prompt-pidgeon.yml
```

3.  Set the required environment variables for your sources and sinks (e.g., `LANGFUSE_SECRET_KEY`).

## Usage

Define your sources, sinks, and sync jobs in the `prompt-pidgeon.yml` file.

**Example `prompt-pidgeon.yml`:**

```
sources:
  - name: my-langfuse-source
    type: langfuse
    # Reads credentials from LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST env vars

sinks:
  - name: local-prompts-dir
    type: filesystem
    path: ./prompts/dev
  - name: open-webui-instance
    type: open-webui
    # Reads credentials from OPEN_WEBUI_URL env var

sync:
  - name: "Sync technical prompts to local filesystem"
    source: my-langfuse-source
    sink: local-prompts-dir
    filter:
      tags: ["technical", "ide"]

  - name: "Sync general prompts to Open WebUI"
    source: my-langfuse-source
    sink: open-webui-instance
    filter:
      tags: ["general", "chat"]
```

Run the sync command from the same directory as your configuration file:

```
prompt-pidgeon sync
```

## Contributing

Interested in contributing? Great! Here's how to get set up:

1.  Fork the repository.
2.  Clone your fork:

```
git clone https://github.com/your-username/prompt-pidgeon.git
```

3.  Create a virtual environment and install the development dependencies:

```
cd prompt-pidgeon
uv venv
source .venv/bin/activate
uv sync
```

4.  Create a new branch for your feature (`git checkout -b feature/amazing-feature`).
5.  Make your changes and commit them.
6.  Push to your branch and open a Pull Request.

## License

This project is licensed under the MIT License.
