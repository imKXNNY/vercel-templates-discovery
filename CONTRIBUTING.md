# Contributing to Vercel Templates Discovery

Thank you for your interest in contributing.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Code quality

```bash
# Formatting and linting
ruff check .
ruff format .

# Type checking
mypy vercel_templates

# Tests
pytest
```

## Pull request process

1. Open an issue first for significant changes.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Ensure tests and linting pass.
4. Add or update tests for new behavior.
5. Keep commits focused and write clear commit messages.

## Reporting bugs

Please include:
- The command you ran
- Expected vs actual output
- Python version and OS
- The output of `vercel-templates stats`
