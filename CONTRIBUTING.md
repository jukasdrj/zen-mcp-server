# Contributing to PAL MCP Server

Thank you for your interest in contributing to PAL MCP Server!

For comprehensive contribution guidelines, please see our detailed documentation:

**[📖 Full Contributing Guide](docs/contributions.md)**

## Quick Links

- **[Getting Started](docs/contributions.md#getting-started)** - Fork, clone, and setup
- **[Code Quality Standards](docs/contributions.md#development-process)** - Linting, formatting, and testing requirements
- **[Pull Request Process](docs/contributions.md#pull-request-process)** - PR titles, checklist, and workflow
- **[Code Style Guidelines](docs/contributions.md#code-style-guidelines)** - Python standards and examples
- **[Adding New Providers](docs/adding_providers.md)** - Provider contribution guide
- **[Adding New Tools](docs/adding_tools.md)** - Tool contribution guide

## Essential Quick Commands

```bash
# Run all quality checks (required before PR)
./code_quality_checks.sh

# Run quick test suite
python communication_simulator_test.py --quick

# Setup development environment
./run-server.sh
```

## PR Title Format

Your PR title MUST use one of these prefixes:
- `feat:` - New features (MINOR version bump)
- `fix:` - Bug fixes (PATCH version bump)
- `breaking:` - Breaking changes (MAJOR version bump)
- `docs:` - Documentation only (no version bump)
- `chore:` - Maintenance tasks (no version bump)
- `test:` - Test additions/changes (no version bump)

## Core Requirements

✅ All code quality checks must pass 100%
✅ All tests must pass (zero tolerance for failures)
✅ New features require tests
✅ Follow code style guidelines (Black, Ruff, isort)
✅ Add docstrings to all public functions and classes

## Getting Help

- **Questions**: Open a [GitHub issue](https://github.com/your-repo/issues) with "question" label
- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Discussions**: Use [GitHub Discussions](https://github.com/your-repo/discussions)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

---

For complete details, see **[docs/contributions.md](docs/contributions.md)**.
