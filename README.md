# prompt-pidgeon

Sync AI prompts between multiple platforms (Langfuse, Open-WebUI, etc.)

## Installation

```bash
pip install prompt-pidgeon
```

## Usage

### CLI
```bash
# Sync prompts from Langfuse to Open-WebUI
prompt-pidgeon sync --config config.yaml

# List available prompts
prompt-pidgeon list --platform langfuse
```

### Library
```python
from prompt_pidgeon import sync_prompts

sync_prompts(source="langfuse", destination="open-webui")
```

## Configuration

Create `config.yaml`:
```yaml
langfuse:
  url: https://cloud.langfuse.com
  # Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY env vars

open_webui:
  url: http://localhost:3000
  # Set OPEN_WEBUI_API_KEY env var
```

## Development

```bash
# Setup
uv sync --extra dev

# Tasks
just lint      # Format and lint code
just test      # Run tests
just typecheck # Type checking
```

## License

MIT
