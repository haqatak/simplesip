# Contributing to SimpleSIP

Thank you for your interest in contributing to SimpleSIP! This document provides guidelines and instructions for contributing to the project.

## 🎯 How Can You Contribute?

### 🐛 Bug Reports
- Report bugs through [GitHub Issues](https://github.com/Awaiskhan404/simplesip/issues)
- Use the bug report template
- Include detailed steps to reproduce
- Provide system information and error messages

### 💡 Feature Requests
- Suggest new features via [GitHub Issues](https://github.com/Awaiskhan404/simplesip/issues)
- Use the feature request template
- Explain the use case and benefits
- Discuss implementation approach if possible

### 🔧 Code Contributions
- Fix bugs and implement features
- Improve documentation
- Add tests and examples
- Optimize performance

### 📚 Documentation
- Improve API documentation
- Add examples and tutorials
- Fix typos and clarify explanations
- Translate documentation

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/simplesip.git
cd simplesip

# Add upstream remote
git remote add upstream https://github.com/Awaiskhan404/simplesip.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### 3. Development Dependencies

The `[dev]` extra installs:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `isort` - Import sorting

### 4. Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Check code quality
black --check simplesip/
flake8 simplesip/
mypy simplesip/
```

## 📋 Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, readable code
- Follow existing code style
- Add docstrings for new functions/classes
- Include type hints where appropriate

### 3. Add Tests

```bash
# Create test file in tests/ directory
# tests/test_your_feature.py

import pytest
from simplesip import SimpleSIPClient

def test_your_feature():
    # Test implementation
    assert True
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=simplesip --cov-report=html

# Run specific test file
pytest tests/test_your_feature.py

# Run tests for specific function
pytest -k "test_your_feature"
```

### 5. Code Quality Checks

```bash
# Format code
black simplesip/ tests/

# Sort imports
isort simplesip/ tests/

# Check linting
flake8 simplesip/ tests/

# Type checking
mypy simplesip/
```

### 6. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of changes

- Detailed explanation of what was added
- Any breaking changes
- Related issue numbers"
```

### 7. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Use the PR template and provide detailed description
```

## 📝 Code Style Guidelines

### General Principles
- Follow PEP 8 style guide
- Use descriptive variable and function names
- Keep functions small and focused
- Write self-documenting code

### Code Formatting
We use `black` for code formatting with these settings:
- Line length: 88 characters
- Target Python version: 3.8+

### Docstrings
Use Google-style docstrings:

```python
def make_call(self, destination: str) -> bool:
    """Initiate a call to the specified destination.
    
    Args:
        destination: The phone number or SIP URI to call
        
    Returns:
        True if call initiation was successful, False otherwise
        
    Raises:
        ConnectionError: If not connected to SIP server
        ValueError: If destination is invalid
        
    Example:
        >>> client = SimpleSIPClient("user", "pass", "server")
        >>> client.connect()
        >>> success = client.make_call("1001")
        >>> if success:
        ...     print("Call initiated")
    """
    # Implementation
```

### Type Hints
Use type hints for function parameters and return values:

```python
from typing import Optional, Dict, List, Callable

def process_audio(
    self, 
    audio_data: bytes, 
    callback: Optional[Callable[[bytes, str], None]] = None
) -> Dict[str, int]:
    # Implementation
```

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log appropriate information

```python
import logging

logger = logging.getLogger(__name__)

def connect(self) -> bool:
    try:
        # Connection logic
        return True
    except socket.error as e:
        logger.error(f"Failed to connect to SIP server: {e}")
        raise ConnectionError(f"Unable to connect to {self.server}:{self.port}")
```

## 🧪 Testing Guidelines

### Test Structure
- Place tests in the `tests/` directory
- Mirror the package structure in test files
- Use descriptive test function names

### Test Categories
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Test Example

```python
import pytest
from unittest.mock import Mock, patch
from simplesip import SimpleSIPClient

class TestSimpleSIPClient:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = SimpleSIPClient("user", "pass", "server")
    
    def test_init(self):
        """Test client initialization."""
        assert self.client.username == "user"
        assert self.client.server == "server"
        assert self.client.port == 5060
    
    @patch('socket.socket')
    def test_connect_success(self, mock_socket):
        """Test successful connection."""
        mock_socket.return_value.connect.return_value = None
        
        result = self.client.connect()
        
        assert result is True
        mock_socket.return_value.connect.assert_called_once()
    
    def test_make_call_without_connection(self):
        """Test making call without connection raises error."""
        with pytest.raises(ConnectionError):
            self.client.make_call("1001")
```

### Mocking External Dependencies
- Mock network connections
- Mock audio interfaces
- Mock system calls

```python
@patch('simplesip.client.socket.socket')
@patch('pyaudio.PyAudio')
def test_audio_streaming(self, mock_audio, mock_socket):
    # Test implementation
    pass
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Changelog is updated (if applicable)
- [ ] PR description is complete

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] New tests added for new functionality
- [ ] All existing tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code performed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation has been updated
- [ ] No new warnings introduced

## Related Issues
Fixes #123
Relates to #456
```

### Code Review Process
1. Automated checks must pass (CI/CD)
2. At least one maintainer review required
3. Address review feedback promptly
4. Squash commits if requested
5. Maintain clean commit history

## 🏗️ Project Structure

```
simplesip/
├── simplesip/              # Main package
│   ├── __init__.py        # Package initialization
│   ├── client.py          # Main SIP client
│   └── examples/          # Example scripts
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_client.py     # Client tests
│   └── test_integration.py
├── docs/                  # Documentation
├── README.md              # Project README
├── CONTRIBUTING.md        # This file
├── LICENSE                # License file
├── pyproject.toml         # Project configuration
├── setup.py               # Setup script
└── .github/               # GitHub workflows
```

## 🔄 Release Process

### Version Numbers
We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Steps (Maintainers)
1. Update version in `simplesip/__init__.py`
2. Update `CHANGELOG.md`
3. Create release branch: `release/v1.2.3`
4. Final testing and review
5. Merge to main
6. Create GitHub release with tag
7. Automated PyPI publication

## 📊 Issue Labels

We use these labels to categorize issues:

### Type
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `question` - Further information requested

### Priority
- `priority: high` - Critical issues
- `priority: medium` - Important issues
- `priority: low` - Nice-to-have improvements

### Status
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `wontfix` - This will not be worked on
- `duplicate` - This issue already exists

### Area
- `area: audio` - Audio processing related
- `area: networking` - Network/SIP protocol
- `area: testing` - Testing infrastructure
- `area: docs` - Documentation

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other community members

### Communication
- Use clear, concise language
- Provide context for issues and PRs
- Ask questions if something is unclear
- Be patient with response times

### Getting Help
- Check existing issues and documentation first
- Use GitHub Discussions for questions
- Provide minimal reproducible examples
- Include relevant system information

## 🏆 Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes for significant contributions
- Social media acknowledgments

## 📞 Contact

- **GitHub Issues**: Technical discussions and bug reports
- **GitHub Discussions**: General questions and community chat
- **Email**: [contact@awaiskhan.com.pk](mailto:contact@awaiskhan.com.pk) for private inquiries

---

Thank you for contributing to SimpleSIP! Every contribution, no matter how small, helps make the project better for everyone. 🎉