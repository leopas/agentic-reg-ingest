<!-- SPDX-License-Identifier: MIT | (c) 2025 Leopoldo Carvalho Correia de Lima -->

# Contributing to agentic-reg-ingest

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/agentic-reg-ingest.git
   cd agentic-reg-ingest
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   make deps
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow existing code style
   - Add docstrings to functions/classes
   - Update tests as needed

3. **Run linters**
   ```bash
   make lint
   ```

4. **Run tests**
   ```bash
   make test
   ```

5. **Run type checker**
   ```bash
   make typecheck
   ```

## Code Style

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking
- Use type hints where possible
- Write descriptive variable names
- Keep functions focused and single-purpose

## Testing Guidelines

- Write tests for new features
- Maintain or improve test coverage
- Use pytest fixtures for setup/teardown
- Mock external dependencies (APIs, databases)
- Test edge cases and error conditions

## Commit Messages

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Example:
```
feat: add support for Excel file ingestion

- Add Excel parser using openpyxl
- Update router to handle .xlsx files
- Add tests for Excel ingestion

Closes #123
```

## Pull Request Process

1. Update documentation (README, docstrings) if needed
2. Ensure all tests pass
3. Update CHANGELOG.md with your changes
4. Submit PR with clear description of changes
5. Link related issues
6. Wait for review and address feedback

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

Thank you for contributing! 🎉

