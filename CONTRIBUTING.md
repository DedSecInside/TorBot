# Contributing to TorBot

Thank you for your interest in contributing to TorBot! This document provides guidelines for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix/Mac)
5. Install dependencies: `pip install -r requirements.txt`

## Making Changes

1. Create a new branch for your feature/fix
2. Make your changes
3. Test your changes thoroughly
4. Update documentation if necessary
5. Update CHANGELOG.md with your changes

## Testing

Run the test suite before submitting:
```bash
python -m pytest tests/
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Ensure all new code has appropriate error handling

## Security Considerations

- Never commit sensitive information (API keys, passwords, etc.)
- Validate all user inputs
- Use secure coding practices
- Test with various edge cases

## Submitting Changes

1. Push your branch to your fork
2. Create a pull request with:
   - Clear description of changes
   - Reference to any related issues
   - Testing evidence/screenshots if applicable

## Review Process

- All PRs require review before merging
- Address feedback promptly
- Ensure CI checks pass

Thank you for contributing to TorBot!