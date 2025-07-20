# CI/CD Workflows

This document outlines the Continuous Integration (CI) and Continuous Deployment (CD) workflows for the `prompt-pidgeon` project. Our automation is built using GitHub Actions.

## CI Workflows

CI workflows are designed to maintain code quality and correctness. They run automatically on every pull request that targets the `main` branch.

### 1. Testing (`.github/workflows/test.yml`)

-   **Trigger**: Pull request to `main`
-   **Purpose**: To ensure that all existing functionality remains correct and that new features meet their requirements.
-   **Jobs**:
    -   `test`: Installs dependencies and runs the full test suite using the `just test` command.

### 2. Static Analysis (`.github/workflows/static-analysis.yml`)

-   **Trigger**: Pull request to `main`
-   **Purpose**: To enforce code style, identify potential bugs, and ensure type safety before code is merged.
-   **Jobs**:
    -   `static-analysis`: Installs dependencies and runs the following checks:
        -   `just lint`: Lints the codebase using `ruff`.
        -   `just typecheck`: Performs static type checking using `mypy`.

## CD Workflows

CD workflows are designed to automate the release and distribution of the application.

### 1. Publish Container Image (`.github/workflows/publish-container.yml`)

-   **Trigger**: Push to `main` branch
-   **Purpose**: To build and publish the application as a Docker container for easy deployment and distribution.
-   **Jobs**:
    -   `publish`:
        1.  Logs into the GitHub Container Registry (GHCR).
        2.  Builds the `Dockerfile` in the root of the repository.
        3.  Pushes the resulting image to GHCR, tagged as `ghcr.io/<owner>/prompt-pidgeon:latest`.

### 2. Publish PyPi Image

We _may_ decide to explore publishing to PyPi image via https://til.simonwillison.net/pypi/pypi-releases-from-github, but am not ready to set up yet.
