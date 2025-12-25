# Poker Coach Agent - Coding Guidelines

## Code Quality Standards

### Python Code Style

#### Formatting
- **Tool**: black with line length 100
- **Configuration**:
  ```toml
  [tool.black]
  line-length = 100
  target-version = ['py311']
  ```
- **Auto-format**: Always run before committing

#### Linting
- **Tool**: ruff (fast, comprehensive)
- **Rules**: Enable all recommended rules plus:
  - `F` (pyflakes)
  - `E`, `W` (pycodestyle)
  - `I` (isort)
  - `N` (pep8-naming)
  - `UP` (pyupgrade)
  - `B` (flake8-bugbear)
- **Fix automatically**: `ruff check . --fix`

#### Type Checking
- **Tool**: pyrefly (modern, fast type checker)
- **Requirements**:
  - Type hints on all function signatures
  - Type hints on class attributes
  - No `Any` types without explicit justification
  - Generic types properly specified (e.g., `list[str]` not `list`)

### Naming Conventions

#### Variables & Functions
```python
# Good
def calculate_equity(hand: str, board: str) -> float:
    pot_size = 100
    effective_stack = 200
    return equity_value

# Bad
def calcEquity(h: str, b: str):  # camelCase, unclear params
    p = 100  # unclear variable names
    return e
```

#### Classes
```python
# Good
class HandEvaluator:
    pass

class RangeBuilder:
    pass

# Bad
class hand_evaluator:  # snake_case
    pass

class rangebuilder:  # no separation
    pass
```

#### Constants
```python
# Good
MAX_PLAYERS = 9
DEFAULT_STACK_SIZE = 100
SUIT_SYMBOLS = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}

# Bad
max_players = 9  # not uppercase
MaxPlayers = 9  # PascalCase
```

#### Files & Modules
```python
# Good file names
hand_evaluator.py
equity_calculator.py
range_builder.py

# Bad file names
HandEvaluator.py  # PascalCase
hand-evaluator.py  # hyphens
handeval.py  # unclear abbreviation
```

### Documentation

#### Module Docstrings
```python
"""
Hand evaluation module for poker hands.

This module provides functionality to evaluate poker hands (5-card and 7-card),
determine winners, and compare hand strengths.

Example:
    >>> from poker_coach.core import HandEvaluator
    >>> evaluator = HandEvaluator()
    >>> strength = evaluator.evaluate("AsKh", "Ac Kd Qh Js Ts")
    >>> print(strength)
    "Royal Flush"
"""
```

#### Function Docstrings (Google Style)
```python
def calculate_equity(hand: str, villain_range: str, board: str = "", iterations: int = 10000) -> float:
    """
    Calculate equity of a hand against a villain's range.

    Runs Monte Carlo simulations to determine the probability that the given hand
    wins against the specified range of opponent hands.

    Args:
        hand: Hero's hand in format "AsKh" (rank + suit for each card)
        villain_range: Opponent's range in standard notation (e.g., "QQ+, AKs")
        board: Community cards if any, in format "Ac Kd Qh" (default: "")
        iterations: Number of Monte Carlo iterations (default: 10000)

    Returns:
        Equity as a float between 0 and 1 (e.g., 0.653 = 65.3%)

    Raises:
        ValueError: If hand or range format is invalid
        ValueError: If board contains invalid cards

    Example:
        >>> equity = calculate_equity("AsKs", "QQ+, AK", "Ah Kh 7s")
        >>> print(f"Equity: {equity:.1%}")
        Equity: 82.3%
    """
```

#### Class Docstrings
```python
class RangeBuilder:
    """
    Build and manipulate poker hand ranges.

    Provides methods to create ranges from notation, convert to combinations,
    and perform range operations like intersection and union.

    Attributes:
        combos: List of all hand combinations in the range
        notation: String representation of the range

    Example:
        >>> rb = RangeBuilder("AK, QQ+")
        >>> print(len(rb.combos))
        28
        >>> print(rb.notation)
        "AK, QQ+"
    """
```

### Error Handling

#### Custom Exceptions
```python
# Good - specific exceptions
class PokerError(Exception):
    """Base exception for poker-related errors."""
    pass

class InvalidHandError(PokerError):
    """Raised when hand format is invalid."""
    pass

class InvalidRangeError(PokerError):
    """Raised when range notation is invalid."""
    pass

# Usage
def parse_hand(hand_str: str) -> tuple[str, str]:
    if len(hand_str) != 4:
        raise InvalidHandError(f"Hand must be 4 characters, got: {hand_str}")
    # ... parsing logic
```

#### Error Messages
```python
# Good - clear, actionable error messages
raise InvalidHandError(
    f"Invalid card '{card}'. Expected format: rank (2-9, T, J, Q, K, A) "
    f"+ suit (s, h, d, c). Example: 'As' for Ace of spades."
)

# Bad - vague error messages
raise ValueError("Invalid input")
raise Exception("Error")
```

#### Exception Handling
```python
# Good - specific exceptions, proper cleanup
def analyze_hand(hand_history: str) -> HandAnalysis:
    try:
        parsed_hand = parse_hand_history(hand_history)
        analysis = analyze_decisions(parsed_hand)
        return analysis
    except InvalidHandHistoryError as e:
        logger.error(f"Failed to parse hand history: {e}")
        raise
    except LLMAPIError as e:
        logger.warning(f"LLM API failed, using fallback analysis: {e}")
        return fallback_analysis(parsed_hand)
    finally:
        cleanup_temp_data()

# Bad - catching everything
def analyze_hand(hand_history: str):
    try:
        # ... code
        return result
    except Exception:  # Too broad
        return None  # Swallows errors
```

### Testing

#### Test File Structure
```python
# tests/core/test_hand_evaluator.py
import pytest
from poker_coach.core.hand_evaluator import HandEvaluator, InvalidHandError

class TestHandEvaluator:
    """Tests for HandEvaluator class."""

    @pytest.fixture
    def evaluator(self):
        """Create HandEvaluator instance for tests."""
        return HandEvaluator()

    def test_royal_flush_detection(self, evaluator):
        """Should identify royal flush correctly."""
        hand = "AsKs"
        board = "Qs Js Ts"
        result = evaluator.evaluate(hand, board)
        assert result.rank_class == "Royal Flush"
        assert result.strength == 1  # Highest possible

    def test_invalid_hand_raises_error(self, evaluator):
        """Should raise InvalidHandError for malformed hand."""
        with pytest.raises(InvalidHandError, match="Expected format"):
            evaluator.evaluate("XX", "As Ks Qs")

    @pytest.mark.parametrize("hand,board,expected", [
        ("AsKs", "Qs Js Ts", "Royal Flush"),
        ("9s8s", "7s 6s 5s", "Straight Flush"),
        ("AhAd", "Ac As Kh", "Four of a Kind"),
    ])
    def test_hand_rankings(self, evaluator, hand, board, expected):
        """Should correctly rank various hand types."""
        result = evaluator.evaluate(hand, board)
        assert result.rank_class == expected
```

#### Test Naming
```python
# Good - descriptive test names
def test_equity_calculator_handles_empty_board():
    pass

def test_range_builder_raises_error_on_invalid_notation():
    pass

def test_hand_parser_extracts_positions_correctly():
    pass

# Bad - unclear test names
def test_equity():
    pass

def test_range():
    pass

def test_1():
    pass
```

#### Fixtures & Mocks
```python
# Good - reusable fixtures
@pytest.fixture
def sample_hand():
    """Standard hand for testing."""
    return {
        "hand": "AsKh",
        "position": "BTN",
        "action": "raise",
        "amount": 3.5,
        "stack": 100
    }

@pytest.fixture
def mock_llm_client(monkeypatch):
    """Mock LLM API to avoid costs in tests."""
    class MockClient:
        def generate(self, prompt: str) -> str:
            return "This is a good hand to raise from the button."

    client = MockClient()
    monkeypatch.setattr("poker_coach.agent.coach.get_llm_client", lambda: client)
    return client
```

### Database

#### Models
```python
# Good - clear model definitions with relationships
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Hand(Base):
    """Represents a poker hand for analysis."""

    __tablename__ = "hands"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    hand_history = Column(String, nullable=False)
    analysis = Column(String)  # JSON blob

    # Relationships
    user = relationship("User", back_populates="hands")

    # Indexes
    __table_args__ = (
        Index('ix_hands_user_timestamp', 'user_id', 'timestamp'),
    )
```

#### Queries
```python
# Good - use ORM, avoid raw SQL
def get_recent_hands(user_id: int, limit: int = 10) -> list[Hand]:
    """Get user's most recent hands."""
    return (
        session.query(Hand)
        .filter(Hand.user_id == user_id)
        .order_by(Hand.timestamp.desc())
        .limit(limit)
        .all()
    )

# Use transactions for multi-step operations
def save_hand_with_analysis(hand_data: dict, analysis: str) -> Hand:
    """Save hand and analysis atomically."""
    with session.begin():
        hand = Hand(**hand_data)
        hand.analysis = analysis
        session.add(hand)
        session.flush()  # Get ID before commit
        return hand
```

### Performance

#### Optimize Hot Paths
```python
# Good - cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=1024)
def parse_range(range_str: str) -> list[tuple[str, str]]:
    """Parse range notation into combinations (cached)."""
    # Expensive parsing logic
    pass

# Good - use generators for large datasets
def iterate_all_hands(user_id: int) -> Generator[Hand, None, None]:
    """Iterate all hands without loading into memory."""
    offset = 0
    batch_size = 100
    while True:
        batch = (
            session.query(Hand)
            .filter(Hand.user_id == user_id)
            .offset(offset)
            .limit(batch_size)
            .all()
        )
        if not batch:
            break
        yield from batch
        offset += batch_size
```

#### Profile Before Optimizing
```python
# Good - measure performance
import time
from loguru import logger

def calculate_range_equity(range1: str, range2: str) -> float:
    """Calculate equity between two ranges."""
    start = time.perf_counter()

    # Equity calculation logic
    result = monte_carlo_simulation(range1, range2, iterations=10000)

    elapsed = time.perf_counter() - start
    logger.debug(f"Equity calculation took {elapsed:.2f}s")

    return result
```

### Logging

#### Use Structured Logging
```python
from loguru import logger

# Configure logger
logger.add(
    "logs/poker_coach_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

# Good - structured, contextual logging
logger.info(
    "Hand analyzed",
    user_id=user.id,
    hand_id=hand.id,
    processing_time=elapsed,
    mistakes_found=len(mistakes)
)

logger.error(
    "LLM API call failed",
    error=str(e),
    prompt_length=len(prompt),
    retry_count=retry,
    exc_info=True
)

# Bad - unstructured logging
print("Analyzing hand...")  # Use logger, not print
logger.info("Error occurred")  # No context
logger.debug(f"User: {user}")  # Exposing PII in logs
```

### Configuration

#### Environment Variables
```python
# Good - use pydantic for settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings from environment."""

    # API Keys
    anthropic_api_key: str
    openai_api_key: str | None = None

    # Database
    database_url: str = "sqlite:///poker_coach.db"

    # LLM
    llm_model: str = "claude-sonnet-4"
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.7

    # Application
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### Use .env File
```bash
# .env (never commit this!)
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///poker_coach.db
LLM_MODEL=claude-sonnet-4
DEBUG=false
LOG_LEVEL=INFO
```

### Security

#### Input Validation
```python
# Good - validate all inputs
def parse_hand(hand_str: str) -> tuple[str, str]:
    """Parse hand string into two cards."""
    # Validate length
    if len(hand_str) != 4:
        raise InvalidHandError(f"Hand must be 4 characters, got {len(hand_str)}")

    # Validate format
    card1, card2 = hand_str[:2], hand_str[2:]
    for card in [card1, card2]:
        rank, suit = card[0], card[1]
        if rank not in "23456789TJQKA":
            raise InvalidHandError(f"Invalid rank: {rank}")
        if suit not in "shdc":
            raise InvalidHandError(f"Invalid suit: {suit}")

    return card1, card2
```

#### Sanitize User Input
```python
# Good - sanitize before storing/processing
import bleach

def save_hand_notes(hand_id: int, notes: str) -> None:
    """Save user notes for a hand."""
    # Sanitize HTML/XSS
    clean_notes = bleach.clean(notes, tags=[], strip=True)

    # Limit length
    if len(clean_notes) > 1000:
        raise ValueError("Notes too long (max 1000 characters)")

    hand = session.query(Hand).get(hand_id)
    hand.notes = clean_notes
    session.commit()
```

## Git Commit Messages

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```bash
# Good commits
feat(equity): add range vs range equity calculator
fix(parser): handle multi-way pots correctly
docs(readme): add installation instructions
test(core): add tests for hand evaluation edge cases

# Bad commits
"fixed stuff"
"WIP"
"asdf"
"Updated code"
```

## Code Review Checklist

Before submitting code, verify:

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Type checking passes (`pyrefly .`)
- [ ] Test coverage maintained or improved
- [ ] Docstrings added for public functions/classes
- [ ] No hardcoded secrets or API keys
- [ ] Error handling is appropriate
- [ ] Logging added for important operations
- [ ] Performance considerations addressed (if applicable)
- [ ] Security considerations addressed (if applicable)

## Anti-Patterns to Avoid

### Magic Numbers
```python
# Bad
if stack_size > 100:
    play_style = "deep"

# Good
DEEP_STACK_THRESHOLD = 100  # Big blinds
if stack_size > DEEP_STACK_THRESHOLD:
    play_style = "deep"
```

### Mutable Default Arguments
```python
# Bad
def add_hand(hand, hands=[]):
    hands.append(hand)
    return hands

# Good
def add_hand(hand, hands=None):
    if hands is None:
        hands = []
    hands.append(hand)
    return hands
```

### Catching All Exceptions
```python
# Bad
try:
    result = risky_operation()
except:
    pass

# Good
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### God Objects/Functions
```python
# Bad - doing too much
def analyze_everything(hand_history):
    # Parse hand
    # Calculate equity
    # Analyze decisions
    # Generate coaching
    # Save to database
    # Send notification
    # ... 500 lines later
    pass

# Good - single responsibility
def analyze_hand(hand_history: str) -> HandAnalysis:
    parsed = parse_hand_history(hand_history)
    equity = calculate_equity(parsed)
    decisions = analyze_decisions(parsed, equity)
    return HandAnalysis(parsed, equity, decisions)
```

---

**Last Updated**: 2025-12-25
**Status**: Active - follow these guidelines for all code contributions
