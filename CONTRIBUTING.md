# Contributing to jsspacynlp

Thank you for your interest in contributing to jsspacynlp! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 14 or higher
- Docker and Docker Compose (for testing)
- Git

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/j3k0/jsspacynlp.git
cd jsspacynlp

# Install Python dependencies
cd server
pip install -r requirements-dev.txt
cd ..

# Install Node.js dependencies
cd client
npm install
cd ..

# Install a test spaCy model
python -m spacy download en_core_web_sm
```

## Project Structure

```
jsspacynlp/
├── server/         # Python FastAPI server
├── client/         # TypeScript client library
├── models/         # Model configuration
├── tests/          # Integration tests
└── docs/           # Additional documentation
```

## Development Workflow

### Making Changes

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes in the appropriate directory:
   - Server changes: `server/app/`
   - Client changes: `client/src/`
   - Documentation: `*.md` files

3. Follow the coding standards (see below)

4. Add tests for new features

5. Run tests to ensure everything works

### Coding Standards

#### Python (Server)

- Follow PEP 8 style guide
- Use type hints for function signatures
- Format code with Black:
  ```bash
  cd server
  black app/ tests/
  ```
- Lint with Ruff:
  ```bash
  ruff check app/ tests/
  ```
- Maximum line length: 100 characters
- Docstrings for all public functions/classes

#### TypeScript (Client)

- Follow the existing code style
- Use TypeScript strict mode
- Format code with Prettier:
  ```bash
  cd client
  npm run format
  ```
- Lint with ESLint:
  ```bash
  npm run lint
  ```
- Add JSDoc comments for public APIs
- Export all public types

### Testing

#### Server Tests

```bash
cd server

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::test_lemmatize_success
```

#### Client Tests

```bash
cd client

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- client.test.ts
```

#### Integration Tests

```bash
# Start server
docker-compose up -d

# Run integration tests
cd server
pytest tests/test_integration.py

# Stop server
docker-compose down
```

### Test Coverage

- Maintain >80% test coverage for new code
- All public APIs must have tests
- Test both success and error cases
- Include edge cases in tests

## Submitting Changes

### Pull Request Process

1. Update documentation for any new features

2. Add tests for new functionality

3. Ensure all tests pass:
   ```bash
   # Server tests
   cd server && pytest
   
   # Client tests
   cd client && npm test
   ```

4. Update CHANGELOG.md with your changes

5. Commit your changes with a clear message:
   ```bash
   git commit -m "feat: add support for custom tokenizers"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request on GitHub

### Commit Message Guidelines

Use conventional commit format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for custom spaCy pipeline components
fix: handle timeout errors in batch processor
docs: update installation instructions
test: add tests for error handling
```

### Pull Request Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventions
- [ ] No unnecessary dependencies added

## Reporting Issues

### Bug Reports

Include the following information:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**:
  - OS and version
  - Python version
  - Node.js version
  - spaCy version
  - jsspacynlp version
- **Error Messages**: Full error messages and stack traces
- **Code Examples**: Minimal reproducible example

### Feature Requests

Include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions you've considered
- **Examples**: Code examples of how it would be used

## Code Review Process

1. Maintainers will review your pull request
2. Address any requested changes
3. Once approved, a maintainer will merge your PR
4. Your contribution will be included in the next release

## Documentation

- Update README.md for user-facing changes
- Update API documentation for new endpoints/methods
- Add code comments for complex logic
- Include examples for new features

## Questions?

If you have questions:

- Check existing issues on GitHub
- Read the documentation
- Ask in a new GitHub issue

## License

By contributing to jsspacynlp, you agree that your contributions will be licensed under the MIT License.

