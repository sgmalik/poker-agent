# Contributing to Poker Coach Agent

Thank you for your interest in contributing to the Poker Coach Agent! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Quality Standards](#code-quality-standards)
- [Testing Guidelines](#testing-guidelines)
- [Poker Logic Contributions](#poker-logic-contributions)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Poker discussions should be educational and strategic
- No spam, self-promotion, or off-topic content

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Familiarity with poker (especially Texas Hold'em)
- Basic understanding of GTO poker principles (for poker logic contributions)

### First Contributions

Good first issues are labeled with `good-first-issue`. These are typically:
- Documentation improvements
- Small bug fixes
- Test additions
- Code cleanup

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/poker-agent.git
   cd poker-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Verify Setup**
   ```bash
   pytest
   black . --check
   ruff check .
   pyrefly .
   ```

## Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make Your Changes**
   - Write code following our style guidelines
   - Add/update tests
   - Update documentation

3. **Run Quality Checks**
   ```bash
   # Format code
   black .

   # Lint
   ruff check . --fix

   # Type check
   pyrefly .

   # Run tests
   pytest --cov
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   **Commit Message Format**:
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

   **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

   **Examples**:
   - `feat(equity): add range vs range calculator`
   - `fix(parser): handle multi-way pots correctly`
   - `docs(readme): update installation instructions`

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Then create a Pull Request on GitHub
   ```

## Code Quality Standards

### Python Style

- **Formatting**: black (line length: 100)
- **Linting**: ruff with recommended rules
- **Type Checking**: pyrefly in strict mode
- **Docstrings**: Google-style docstrings

### Code Organization

```python
# Good example
def calculate_equity(hand: str, villain_range: str, board: str = "") -> float:
    """
    Calculate equity of a hand against a villain's range.

    Args:
        hand: Hero's hand in format "AsKh"
        villain_range: Opponent's range in notation (e.g., "QQ+, AKs")
        board: Community cards if any (default: "")

    Returns:
        Equity as a float between 0 and 1

    Raises:
        ValueError: If hand or range format is invalid
    """
    # Implementation
    pass
```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private**: `_leading_underscore`

## Testing Guidelines

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Aim for >80% code coverage
- Poker logic must have 100% test coverage

### Test Structure

```python
# tests/core/test_hand_evaluator.py
import pytest
from poker_coach.core.hand_evaluator import HandEvaluator

class TestHandEvaluator:
    """Tests for HandEvaluator class."""

    @pytest.fixture
    def evaluator(self):
        return HandEvaluator()

    def test_royal_flush_detection(self, evaluator):
        """Should identify royal flush correctly."""
        result = evaluator.evaluate("AsKs", "Qs Js Ts")
        assert result.rank_class == "Royal Flush"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/core/test_hand_evaluator.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/core/test_hand_evaluator.py::TestHandEvaluator::test_royal_flush_detection
```

## Poker Logic Contributions

### Validation Required

All poker logic changes must be validated against established tools:

- **Hand Evaluation**: Verify against standard poker hand rankings
- **Equity Calculations**: Compare with PokerStove, Equilab, or similar
- **GTO Advice**: Reference GTO Wizard, PioSolver, or GTO+
- **Range Notation**: Follow standard poker range notation

### Documentation

Include in your PR:
- What poker concept is being implemented
- How you validated correctness
- References (books, solvers, calculators)
- Edge cases considered

### Example

```python
def test_equity_calculation_validated():
    """
    Verify equity calculation matches PokerStove.

    Test case from PokerStove:
    AsKs vs QQ on Ah Kh 7s = 82.3% equity
    """
    equity = calculate_equity("AsKs", "QQ", "Ah Kh 7s")
    assert abs(equity - 0.823) < 0.01  # Within 1% tolerance
```

## Submitting Changes

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Linting passes (ruff)
- [ ] Type checking passes (pyrefly)
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Poker logic validated (if applicable)
- [ ] No hardcoded secrets
- [ ] Commit messages follow convention

### PR Description

Use the PR template and include:
- Clear description of changes
- Motivation and context
- Testing performed
- Screenshots (if UI changes)
- Breaking changes (if any)

## Review Process

### What to Expect

1. **Automated Checks**: CI/CD runs tests, linting, type checking
2. **Code Review**: Maintainer reviews code quality and logic
3. **Poker Validation**: For poker logic, validation is verified
4. **Feedback**: You may receive comments or change requests
5. **Approval**: Once approved, PR will be merged

### Review Criteria

- Code quality and maintainability
- Test coverage and quality
- Documentation completeness
- Poker logic correctness (if applicable)
- Performance considerations
- Security implications

### Response Time

- Initial review: Within 3-5 days
- Follow-up: Within 1-2 days
- Note: This is a side project, so please be patient!

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a Bug Report issue
- **Features**: Create a Feature Request issue
- **Poker Logic**: Use the Poker Logic Issue template

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Appreciated in the community!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to Poker Coach Agent! Your help in building a better poker study tool is greatly appreciated.
