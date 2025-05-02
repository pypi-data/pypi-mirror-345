# Contributing to Preswald

Thank you for your interest in contributing to **Preswald**! This document outlines the project structure, how to set up your development environment, and the guidelines for contributing. Whether you’re fixing bugs, adding new features, or improving documentation, we appreciate your time and effort.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Setup Guide](#setup-guide)
3. [Development Workflow](#development-workflow)
4. [Working with Forks & Keeping Your Branches in Sync](#working-with-forks--keeping-your-branches-in-sync)
5. [Style Guide](#style-guide)
6. [Code Quality](#code-quality)
7. [Claiming an Issue](#claiming-an-issue)
8. [Pull Request Guidelines](#pull-request-guidelines)
9. [Issue Reporting Guidelines](#issue-reporting-guidelines)
10. [Community Support](#community-support)
11. [Acknowledgments](#acknowledgments)

## Project Structure

```
preswald/
├── preswald/       # SDK + Python FastAPI backend
├── frontend/       # React + Vite frontend
├── examples/       # Sample apps to showcase Preswald's capabilities
├── tutorial/       # Tutorial for getting started with Preswald
├── tests/          # Unit and integration tests
├── pyproject.toml  # Python package configuration
└── README.md       # Project overview
```

## Setup Guide

### 1. Fork and Clone the Repository

1. **Fork the repository** on GitHub.
2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/StructuredLabs/preswald.git
   cd preswald
   ```

### 2. Set Up a Python Environment

We recommend using Conda to manage dependencies:

1. [OPTIONAL] Install uv (this makes things so much faster):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Create and activate a Conda environment:
   ```bash
   conda create -n preswald python=3.10 -y
   conda activate preswald
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"

   or

   uv pip install -e ".[dev]" # if you installed uv
   ```
4. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

### 3. Build the Frontend

Build the frontend once
```bash
python -m preswald.build frontend
```

Or use watch mode to monitor changes and auto-rebuild
```bash
python -m preswald.build watch
```

### 4. Run the Example App

Verify your setup by running the sample app:

```bash
cd examples/iris && preswald run
```

## Development Workflow

Here’s a quick summary of the contributing workflow:

1. **Fork and clone the repository.**
2. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and follow the [Style Guide](#style-guide).
4. **Test your changes** thoroughly.
5. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** on the main repository.

## Working with Forks & Keeping Your Branches in Sync

When your forked repo gets out of sync with upstream (StructuredLabs/preswald), you’ll want to rebase your feature branch onto the latest upstream main to keep your commit history clean and linear. This avoids unnecessary merge commits that can clutter PR reviews. (If you haven’t already, add the upstream remote:
`git remote add upstream git@github.com:StructuredLabs/preswald.git`)

Here’s a great guide on syncing forks:
https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork

And here’s a solid intro to Git rebase:
https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase

## Style Guide

Follow these style guidelines to maintain consistency:

- **Python**: Use [PEP 8](https://peps.python.org/pep-0008/).
- **React**: Follow [React Best Practices](https://react.dev/learn).
- **Formatting/Linting**:
  These are set up in the pre-commit hook - will run upon `git commit` on staged files. You don't have to run anything explicitly for formatting/linting
  - Python: we use `ruff`
    ```bash
    ruff format
    ruff check --fix
    ```
  - JavaScript: we use `ESLint` with the provided configuration.
    ```bash
    npm run lint
    ```

## Code Quality

If you're using Preswald in your project, you might want to adopt similar standards. You can use our configuration files as a starting point:

- `.pre-commit-config.yaml` for pre-commit configuration
- `pyproject.toml` for tool settings

These configurations ensure your code remains consistent with our standards when contributing back to the project.

## Testing

1. Create and activate another Conda environment for testing:
   ```bash
   conda deactivate # if inside an existing conda env
   conda create -n preswald-test python=3.10 -y
   conda activate preswald-test
   ```
2. Clear old builds:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```
3. Build frontend and backend:
   ```bash
   python -m preswald.build frontend
   python -m build
   ```
4. Install the pip package
   ```bash
   uv pip install dist/preswald-0.xx.xx.tar.gz
   ```
5. Run a test app
   ```
   cd examples/earthquakes && preswald run
   ```
   Make sure to do step 5 for **all** directories in `examples`, not just `earthquakes`

## Claiming an Issue

Issues are assigned and reviewed on a first come first serve basis. When you begin work on an issue, ensure you leave a comment acknowledging that you have done so such that other users who may be interested in the issue are aware of your work.

## Pull Request Guidelines

When submitting a PR:

1. Use a descriptive branch name (e.g., `feature/add-widget` or `fix/typo-readme`).
2. Write a clear and concise PR title and description.
   - **Title**: Start with a type prefix, such as `feat`, `fix`, or `docs`.
   - **Description**: Include context, screenshots (if applicable), and links to relevant issues.
3. Ensure your PR includes:
   - Relevant tests for your changes.
   - Updates to the documentation if applicable.

Example PR description:

```
feat: add new user authentication system

This PR adds user authentication via JWT tokens. Includes:
- Backend API endpoints for login and signup.
- React context integration for frontend.
- Unit tests for new functionality.

Fixes #42
```

## Issue Reporting Guidelines

When reporting an issue:

1. Use a clear and concise title.
2. Provide relevant details, such as:
   - Steps to reproduce the issue.
   - Expected vs. actual behavior.
   - Environment details (OS, Python version, browser).
   - Screenshots or logs, if applicable.

Example issue template:

```
**Describe the bug**
A clear and concise description of the issue.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain the issue.

**Environment**
- OS: [e.g., Windows, macOS, Linux]
- Python version: [e.g., 3.9]
- Browser: [e.g., Chrome, Firefox]
```

## Community Support

If you have questions or need help:

- Email us at **[founders@structuredlabs.com](mailto:founders@structuredlabs.com)**.
- Join the **Structured Users Slack** for discussions and support:
  [Structured Users Slack Invite](https://structured-users.slack.com/join/shared_invite/zt-265ong01f-UHP6BP3FzvOmMQDIKty_JQ#/shared-invite/email).

## Acknowledgments

We’re deeply grateful for your contributions! Every bug report, feature suggestion, and PR helps us build a better **Preswald**. Let’s create something amazing together! 🚀
