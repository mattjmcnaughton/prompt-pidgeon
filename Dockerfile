
# Use a lightweight Python base image
FROM python:3.13-slim-bookworm

RUN apt update && apt install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group with UID/GID 1000
RUN addgroup --gid 1000 appgroup && adduser --uid 1000 --gid 1000 --shell /bin/sh --disabled-password --gecos "" appuser
USER appuser

# Install uv and make accessible to the user
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/appuser/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy dependency management files
COPY --chown=appuser:appgroup pyproject.toml uv.lock README.md ./
COPY --chown=appuser:appgroup prompt_pidgeon ./prompt_pidgeon

RUN uv sync

# Define the entrypoint for the CLI application
ENTRYPOINT ["uv", "run", "prompt-pidgeon"]
