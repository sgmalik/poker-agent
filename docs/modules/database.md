# Database Module Documentation

The `src/database/` module provides data persistence using SQLite and SQLAlchemy ORM.

---

## Table of Contents
1. [db.py](#dbpy) - Engine setup and session management
2. [models.py](#modelspy) - SQLAlchemy model definitions
3. [service.py](#servicepy) - CRUD operations

---

## db.py

**Purpose:** Database engine configuration and session management.

**Dependencies:**
- `sqlalchemy` - ORM framework
- `config.DATABASE_URL` - Database connection string

### Engine Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,                             # "sqlite:///data/poker_coach.db"
    connect_args={"check_same_thread": False}, # Allow multi-threaded access
    echo=False,                                # Disable SQL logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model declarations
Base = declarative_base()
```

**SQLAlchemy References:**

| Function | Official Docs |
|----------|---------------|
| `create_engine()` | [Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine) |
| `sessionmaker()` | [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker) |
| `declarative_base()` | [Declarative Mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping) |

### Function: get_db

```python
def get_db() -> Generator[Session, None, None]:
    """
    Get a database session as a context manager.

    Yields:
        Database session that auto-closes after use

    Usage:
        with get_db() as db:
            result = db.query(Model).all()
    """
```

### Function: init_db

```python
def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Imports all models to register them with Base.metadata,
    then calls create_all() to create tables.

    Should be called once at application startup.
    """
    from . import models  # Registers models with metadata
    Base.metadata.create_all(bind=engine)
```

### Function: drop_db

```python
def drop_db() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data permanently!
    """
    Base.metadata.drop_all(bind=engine)
```

---

## models.py

**Purpose:** Define SQLAlchemy ORM models for all database tables.

**Dependencies:**
- `sqlalchemy` - Column types and model base
- `datetime` - Timestamp handling

### Column Type Reference (SQLAlchemy)

| Type | SQLAlchemy | Python Type | Usage |
|------|------------|-------------|-------|
| Integer | `Column(Integer)` | `int` | IDs, counts |
| Float | `Column(Float)` | `float` | Money, percentages |
| String | `Column(String(n))` | `str` | Short text (n=max length) |
| Text | `Column(Text)` | `str` | Long text (unlimited) |
| Boolean | `Column(Boolean)` | `bool` | True/False flags |
| DateTime | `Column(DateTime)` | `datetime` | Timestamps |

**Official Docs:** [Column and Data Types](https://docs.sqlalchemy.org/en/20/core/types.html)

---

### Model: PokerSession

Stores poker session records for bankroll tracking.

```python
class PokerSession(Base):
    __tablename__ = "poker_sessions"

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    date = Column(DateTime, nullable=False)
    stake_level = Column(String(20), nullable=False)      # "1/2", "2/5", "NL50"
    buy_in = Column(Float, nullable=False)
    cash_out = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=False)           # Calculated: cash_out - buy_in
    duration_minutes = Column(Integer, nullable=True)
    hands_played = Column(Integer, nullable=True)
    location = Column(String(100), nullable=True)         # "Bellagio", "PokerStars"
    game_type = Column(String(20), default="cash")        # cash, tournament
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Computed Properties
    @property
    def hourly_rate(self) -> float | None:
        """Calculate hourly profit rate: profit_loss / (duration / 60)"""

    @property
    def bb_per_hour(self) -> float | None:
        """Calculate big blinds per hour (parses stake_level)"""
```

**Schema:**
```sql
CREATE TABLE poker_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    date DATETIME NOT NULL,
    stake_level VARCHAR(20) NOT NULL,
    buy_in FLOAT NOT NULL,
    cash_out FLOAT NOT NULL,
    profit_loss FLOAT NOT NULL,
    duration_minutes INTEGER,
    hands_played INTEGER,
    location VARCHAR(100),
    game_type VARCHAR(20) NOT NULL DEFAULT 'cash',
    notes TEXT,
    created_at DATETIME NOT NULL
);
```

---

### Model: QuizAttempt

Stores individual quiz question attempts.

```python
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    question_id = Column(String(50), nullable=False)      # "post_001"
    scenario = Column(Text, nullable=True)
    user_answer = Column(String(100), nullable=False)
    correct_answer = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=True)           # seconds
    difficulty = Column(String(20), nullable=True)
    topic = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

---

### Model: QuizSession

Stores quiz session summaries.

```python
class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    topic = Column(String(50), nullable=True)             # None = all topics
    difficulty = Column(String(20), nullable=True)        # None = all difficulties
    total_questions = Column(Integer, nullable=False)
    questions_attempted = Column(Integer, nullable=True)
    correct_answers = Column(Integer, nullable=False)
    time_total = Column(Integer, nullable=True)           # seconds
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def percentage(self) -> float:
        """Calculate score: (correct / attempted) * 100"""
```

---

### Model: HandHistory

Stores individual hand histories.

```python
class HandHistory(Base):
    __tablename__ = "hand_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    hero_hand = Column(String(10), nullable=False)        # "As Kh"
    board = Column(String(25), nullable=True)             # "Qh Jh 2c 5d 9s"
    position = Column(String(5), nullable=False)          # BTN, CO, etc.
    action_summary = Column(Text, nullable=True)
    result = Column(String(10), nullable=False)           # won, lost, split
    stake_level = Column(String(10), nullable=True)
    pot_size = Column(Float, nullable=True)
    tags = Column(Text, nullable=True)                    # Comma-separated
    notes = Column(Text, nullable=True)
    hand_text = Column(Text, nullable=True)               # Full hand history text
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def tag_list(self) -> list[str]:
        """Return tags as a list (splits comma-separated string)"""

    @property
    def street(self) -> str:
        """Determine street from board card count: preflop/flop/turn/river"""
```

---

## service.py

**Purpose:** Provide CRUD operations as simple functions (service layer pattern).

All functions follow this pattern:
1. Create session with `SessionLocal()`
2. Perform operations
3. Commit changes
4. Close session in `finally` block

---

### Quiz Functions

#### save_quiz_attempt

```python
def save_quiz_attempt(attempt: Dict[str, Any], user_id: int = 1) -> int:
    """
    Save a single quiz attempt.

    Args:
        attempt: Dict with keys:
            - question_id: str
            - user_answer: str
            - correct_answer: str
            - is_correct: bool
            - time_taken: int (optional)
            - difficulty: str (optional)
            - topic: str (optional)
            - scenario: str (optional)
        user_id: User ID (default 1)

    Returns:
        int: ID of created record
    """
```

#### save_quiz_session

```python
def save_quiz_session(
    results: Dict[str, Any],
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    user_id: int = 1,
) -> int:
    """
    Save quiz session summary and all individual attempts.

    Args:
        results: Dict from QuizEngine.get_results() with:
            - total: int
            - score: int
            - answers: List[Dict]
            - time_total: int
        topic: Topic filter used
        difficulty: Difficulty filter used
        user_id: User ID

    Returns:
        int: ID of created session
    """
```

#### get_quiz_stats

```python
def get_quiz_stats(
    user_id: int = 1,
    topic: Optional[str] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Get quiz statistics for analysis.

    Returns:
        Dict with:
            - total_attempts: int
            - correct: int
            - percentage: float
            - by_topic: Dict[str, {total, correct}]
            - by_difficulty: Dict[str, {total, correct}]
    """
```

#### get_quiz_attempt_by_id

```python
def get_quiz_attempt_by_id(
    attempt_id: int,
    user_id: int = 1,
) -> Optional[Dict[str, Any]]:
    """Get single quiz attempt by ID."""
```

#### get_quiz_session_by_id

```python
def get_quiz_session_by_id(
    session_id: int,
    user_id: int = 1,
) -> Optional[Dict[str, Any]]:
    """Get single quiz session by ID."""
```

#### identify_study_leaks

```python
def identify_study_leaks(
    user_id: int = 1,
    min_attempts: int = 5,
    threshold: float = 60.0,
) -> List[Dict[str, Any]]:
    """
    Find weak areas based on quiz performance.

    Args:
        min_attempts: Minimum attempts to consider a topic
        threshold: Percentage below which topic is "weak"

    Returns:
        List of dicts with: topic, attempts, correct, percentage, recommendation
    """
```

---

### Poker Session Functions

#### save_poker_session

```python
def save_poker_session(session_data: Dict[str, Any], user_id: int = 1) -> int:
    """
    Save a poker session.

    Args:
        session_data: Dict with:
            - date: datetime or str
            - stake_level: str (required)
            - buy_in: float (required)
            - cash_out: float (required)
            - duration_minutes: int (optional)
            - hands_played: int (optional)
            - location: str (optional)
            - game_type: str (optional, default "cash")
            - notes: str (optional)

    Returns:
        int: ID of created session
    """
```

#### get_poker_sessions

```python
def get_poker_sessions(
    user_id: int = 1,
    days: int = 0,          # 0 = all time
    stake_level: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Query poker sessions with filters.

    Returns list of dicts with all session fields plus computed properties.
    """
```

#### get_poker_session_by_id

```python
def get_poker_session_by_id(
    session_id: int,
    user_id: int = 1,
) -> Optional[Dict[str, Any]]:
    """Get single poker session by ID."""
```

#### get_session_stats

```python
def get_session_stats(
    user_id: int = 1,
    days: int = 0,
    stake_level: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get aggregated poker session statistics.

    Returns:
        Dict with:
            - total_sessions: int
            - total_profit: float
            - total_hours: float
            - hourly_rate: float
            - win_rate: float (percentage of winning sessions)
            - avg_session_profit: float
            - by_stake: Dict[stake, {sessions, profit, hours}]
            - by_location: Dict[location, {sessions, profit}]
    """
```

#### get_bankroll_data

```python
def get_bankroll_data(
    user_id: int = 1,
    days: int = 0,
) -> Dict[str, Any]:
    """
    Get bankroll progression data for graphing.

    Returns:
        Dict with:
            - data_points: List[{date, profit, cumulative}]
            - total_profit: float
            - peak: float
            - current: float
    """
```

---

### Hand History Functions

#### save_hand_history

```python
def save_hand_history(hand_data: Dict[str, Any], user_id: int = 1) -> int:
    """
    Save a hand history.

    Args:
        hand_data: Dict with:
            - hero_hand: str (required)
            - position: str (required)
            - result: str (required) - "won", "lost", "split"
            - board: str (optional)
            - action_summary: str (optional)
            - stake_level: str (optional)
            - pot_size: float (optional)
            - tags: List[str] (optional) - converted to comma-separated
            - notes: str (optional)
            - hand_text: str (optional)

    Returns:
        int: ID of created hand
    """
```

#### get_hand_histories

```python
def get_hand_histories(
    user_id: int = 1,
    days: int = 0,
    result: Optional[str] = None,
    position: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Query hand histories with filters.

    Returns list of dicts with all hand fields plus computed 'street' property.
    Tags are returned as list.
    """
```

#### get_hand_history_by_id

```python
def get_hand_history_by_id(
    hand_id: int,
    user_id: int = 1,
) -> Optional[Dict[str, Any]]:
    """Get single hand history by ID."""
```

---

### Admin Functions

#### get_admin_stats

```python
def get_admin_stats(user_id: int = 1) -> Dict[str, int]:
    """
    Get record counts for admin dashboard.

    Returns:
        Dict with:
            - quiz_attempts: int
            - quiz_sessions: int
            - poker_sessions: int
            - hand_histories: int
    """
```

#### Delete Functions

```python
def delete_quiz_attempt(attempt_id: int, user_id: int = 1) -> bool:
def delete_quiz_session(session_id: int, user_id: int = 1) -> bool:
def delete_poker_session(session_id: int, user_id: int = 1) -> bool:
def delete_hand_history(hand_id: int, user_id: int = 1) -> bool:
```

All delete functions return `True` on success, `False` if record not found.

---

## SQLAlchemy Query Patterns

### Basic Query

```python
db = SessionLocal()
try:
    # Get all records
    records = db.query(Model).all()

    # Get single record by ID
    record = db.query(Model).filter(Model.id == id).first()

    # Filter by multiple conditions
    records = db.query(Model).filter(
        Model.user_id == user_id,
        Model.date >= cutoff_date,
    ).all()
finally:
    db.close()
```

### Create Record

```python
db = SessionLocal()
try:
    new_record = Model(field1=value1, field2=value2)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)  # Get auto-generated ID
    return new_record.id
finally:
    db.close()
```

### Delete Record

```python
db = SessionLocal()
try:
    record = db.query(Model).filter(Model.id == id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False
finally:
    db.close()
```

**Official SQLAlchemy Documentation:**
- [ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html)

---

## Entity Relationship Diagram

```
┌─────────────────────────┐
│    poker_sessions       │
├─────────────────────────┤
│ PK id                   │
│    user_id              │
│    date                 │
│    stake_level          │
│    buy_in               │
│    cash_out             │
│    profit_loss          │
│    duration_minutes     │
│    hands_played         │
│    location             │
│    game_type            │
│    notes                │
│    created_at           │
└─────────────────────────┘

┌─────────────────────────┐     ┌─────────────────────────┐
│    quiz_sessions        │     │    quiz_attempts        │
├─────────────────────────┤     ├─────────────────────────┤
│ PK id                   │     │ PK id                   │
│    user_id              │     │    user_id              │
│    topic                │     │    question_id          │
│    difficulty           │     │    scenario             │
│    total_questions      │     │    user_answer          │
│    questions_attempted  │     │    correct_answer       │
│    correct_answers      │     │    is_correct           │
│    time_total           │     │    time_taken           │
│    created_at           │     │    difficulty           │
└─────────────────────────┘     │    topic                │
                                │    created_at           │
                                └─────────────────────────┘

┌─────────────────────────┐
│    hand_histories       │
├─────────────────────────┤
│ PK id                   │
│    user_id              │
│    hero_hand            │
│    board                │
│    position             │
│    action_summary       │
│    result               │
│    stake_level          │
│    pot_size             │
│    tags                 │
│    notes                │
│    hand_text            │
│    created_at           │
└─────────────────────────┘
```

Note: Currently no foreign key relationships between tables. Each table is independent with `user_id` for multi-user support.
