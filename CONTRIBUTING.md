# Contributing to SubFluxGPT

Thank you for your interest in contributing to SubFluxGPT! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be constructive in your feedback and welcoming to new contributors.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, use the provided bug report template and include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, API used)
- Error messages/logs

### Suggesting Features

Feature suggestions are welcome! Use the feature request template and describe:

- The feature and its use case
- Why it would be valuable for the bug bounty community
- Any implementation ideas you have

### Pull Requests

#### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/SubFluxGPT.git
   cd SubFluxGPT
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

5. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Making Changes

- Follow the existing code style and patterns
- Add comments for complex logic
- Update documentation as needed
- Test your changes thoroughly

#### Commit Guidelines

- Write clear, descriptive commit messages
- Use conventional commit format:
  - `feat: add new feature`
  - `fix: resolve bug description`
  - `docs: update documentation`
  - `refactor: improve code structure`

Example:
```
feat: add support for custom Netlas dork queries

- Allow users to specify custom dork queries via --netlas-dork
- Update CLI to accept dork parameter
- Add documentation and examples
```

#### Submitting PRs

1. Push your changes to your fork
2. Create a pull request to the main branch
3. Fill out the PR template
4. Wait for review and address any feedback

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and modular
- Add docstrings for public functions and classes

### Testing

- Test your changes with various APIs (Gemini, Claude, etc.)
- Test with different input sizes
- Verify stdout pipeline functionality
- Test integration with external tools (httpx, BBRF)

### Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update docstrings for modified functions
- Add examples for new features

## Project Structure

```
SubFluxGPT/
├── src/subfluxgpt/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── ai_router.py        # Multi-API LLM router
│   ├── netlas_client.py    # Netlas API integration
│   ├── bbrf_client.py      # BBRF integration
│   ├── dns_resolver.py     # DNS resolution
│   ├── http_prober.py      # HTTP probing
│   └── utils.py            # Utilities
├── tests/
├── docs/
└── requirements.txt
```

## API Integration Guidelines

When adding support for new AI APIs:

1. Add the API method to `ai_router.py`
2. Follow the existing pattern (async method returning LLMResponse)
3. Add the API to the available choices in CLI
4. Update requirements.txt with necessary dependencies
5. Document the API in README.md

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Contact maintainers

Thank you for contributing to SubFluxGPT! 🚀
