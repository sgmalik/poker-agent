# SQLAlchemy Library Reference

## Overview

**SQLAlchemy** is a Python SQL toolkit and Object-Relational Mapping (ORM) library. The Poker Coach Agent uses SQLAlchemy 2.0+ with its modern ORM style.

**Official Documentation:** https://docs.sqlalchemy.org/en/20/

**Installation:**
```bash
pip install sqlalchemy
```

---

## Core Components

### Engine & Connection

The engine is the starting point for SQLAlchemy, managing the database connection pool.

**Documentation:** https://docs.sqlalchemy.org/en/20/core/engines.html

#### Function: `create_engine(url)`

Creates a database engine.

```python
from sqlalchemy import create_engine

engine = create_engine(url: str, **kwargs)
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | `str` | Database connection URL |
| `echo` | `bool` | Log SQL statements (default: False) |
| `pool_pre_ping` | `bool` | Test connections before use |

**URL Formats:**
```python
# SQLite (file-based)
"sqlite:///./data/poker_coach.db"

# SQLite (in-memory)
"sqlite:///:memory:"

# PostgreSQL
"postgresql://user:password@host:port/database"
```

**Usage in Poker Coach:**
```python
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./data/poker_coach.db"
engine = create_engine(DATABASE_URL, echo=False)
```

---

### Declarative Base

The base class for all ORM models.

**Documentation:** https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

All model classes inherit from this base:

```python
class User(Base):
    __tablename__ = "users"
    # ... columns
```

---

### Column Types

**Documentation:** https://docs.sqlalchemy.org/en/20/core/types.html

```python
from sqlalchemy import (
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
```

#### Common Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `Integer` | `int` | Whole numbers |
| `String(n)` | `str` | Variable-length string up to n |
| `Text` | `str` | Unlimited text |
| `Float` | `float` | Floating-point numbers |
| `Boolean` | `bool` | True/False |
| `DateTime` | `datetime` | Date and time |
| `JSON` | `dict/list` | JSON data (SQLite 3.9+) |

---

### Model Definition

**Documentation:** https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html

#### Modern Style (SQLAlchemy 2.0+)

```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class PokerSession(Base):
    __tablename__ = "poker_sessions"

    # Primary key (auto-increment)
    id: Mapped[int] = mapped_column(primary_key=True)

    # Required fields
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    date: Mapped[str] = mapped_column(String(10))
    stake_level: Mapped[str] = mapped_column(String(20))
    buy_in: Mapped[float] = mapped_column(Float)
    cash_out: Mapped[float] = mapped_column(Float)
    profit_loss: Mapped[float] = mapped_column(Float)

    # Optional fields
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # JSON field
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Timestamp with default
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
```

#### Column Options

| Option | Description |
|--------|-------------|
| `primary_key=True` | Mark as primary key |
| `nullable=True` | Allow NULL values |
| `default=value` | Default value |
| `unique=True` | Enforce uniqueness |
| `index=True` | Create index |

---

### Session Management

**Documentation:** https://docs.sqlalchemy.org/en/20/orm/session.html

```python
from sqlalchemy.orm import sessionmaker, Session

SessionLocal = sessionmaker(bind=engine)
```

#### Context Manager Pattern

```python
def get_db():
    """Get database session as context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage
with SessionLocal() as session:
    # ... database operations
    session.commit()
```

---

### CRUD Operations

#### Create (Insert)

```python
def save_poker_session(
    date: str,
    stake_level: str,
    buy_in: float,
    cash_out: float,
    **kwargs
) -> int:
    """Create a new poker session."""
    with SessionLocal() as session:
        new_session = PokerSession(
            date=date,
            stake_level=stake_level,
            buy_in=buy_in,
            cash_out=cash_out,
            profit_loss=cash_out - buy_in,
            **kwargs
        )
        session.add(new_session)
        session.commit()
        session.refresh(new_session)
        return new_session.id
```

---

#### Read (Query)

**Documentation:** https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html

```python
from sqlalchemy import select

def get_poker_sessions(
    user_id: int = 1,
    days: int = 0,
    limit: int = 100
) -> List[Dict]:
    """Get poker sessions with optional filters."""
    with SessionLocal() as session:
        # Build query
        query = select(PokerSession).where(
            PokerSession.user_id == user_id
        )

        # Add date filter
        if days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            query = query.where(PokerSession.created_at >= cutoff)

        # Order and limit
        query = query.order_by(PokerSession.created_at.desc())
        query = query.limit(limit)

        # Execute
        result = session.execute(query)
        rows = result.scalars().all()

        # Convert to dicts
        return [row_to_dict(row) for row in rows]
```

#### Query Methods

| Method | Description |
|--------|-------------|
| `select(Model)` | Start a SELECT query |
| `.where(condition)` | Add WHERE clause |
| `.filter(condition)` | Alias for where |
| `.order_by(column)` | Add ORDER BY |
| `.limit(n)` | Limit results |
| `.offset(n)` | Skip first n results |
| `.scalars()` | Get scalar results |
| `.all()` | Get all results |
| `.first()` | Get first result |
| `.one()` | Get exactly one result |
| `.one_or_none()` | Get one or None |

#### Filter Operators

```python
# Equality
.where(Model.field == value)

# Inequality
.where(Model.field != value)

# Comparison
.where(Model.field > value)
.where(Model.field >= value)
.where(Model.field < value)
.where(Model.field <= value)

# NULL check
.where(Model.field.is_(None))
.where(Model.field.is_not(None))

# LIKE
.where(Model.field.like("%pattern%"))
.where(Model.field.ilike("%pattern%"))  # Case-insensitive

# IN
.where(Model.field.in_([value1, value2]))

# AND (multiple where clauses)
.where(Model.field1 == value1).where(Model.field2 == value2)

# OR
from sqlalchemy import or_
.where(or_(Model.field1 == value1, Model.field2 == value2))
```

---

#### Update

```python
def update_poker_session(session_id: int, **updates) -> bool:
    """Update a poker session."""
    with SessionLocal() as session:
        # Fetch the record
        query = select(PokerSession).where(PokerSession.id == session_id)
        result = session.execute(query)
        record = result.scalar_one_or_none()

        if not record:
            return False

        # Update fields
        for key, value in updates.items():
            if hasattr(record, key):
                setattr(record, key, value)

        session.commit()
        return True
```

---

#### Delete

```python
def delete_poker_session(session_id: int) -> bool:
    """Delete a poker session."""
    with SessionLocal() as session:
        query = select(PokerSession).where(PokerSession.id == session_id)
        result = session.execute(query)
        record = result.scalar_one_or_none()

        if not record:
            return False

        session.delete(record)
        session.commit()
        return True
```

---

### Aggregation Functions

**Documentation:** https://docs.sqlalchemy.org/en/20/core/functions.html

```python
from sqlalchemy import func, select

def get_session_stats(user_id: int = 1, days: int = 30) -> Dict:
    """Get aggregated session statistics."""
    with SessionLocal() as session:
        # Build base query
        query = select(
            func.count(PokerSession.id).label("total"),
            func.sum(PokerSession.profit_loss).label("total_profit"),
            func.avg(PokerSession.profit_loss).label("avg_profit"),
            func.max(PokerSession.profit_loss).label("biggest_win"),
            func.min(PokerSession.profit_loss).label("biggest_loss"),
        ).where(
            PokerSession.user_id == user_id
        )

        # Add date filter
        if days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            query = query.where(PokerSession.created_at >= cutoff)

        result = session.execute(query)
        row = result.one()

        return {
            "total_sessions": row.total or 0,
            "total_profit": row.total_profit or 0.0,
            "average_profit": row.avg_profit or 0.0,
            "biggest_win": row.biggest_win or 0.0,
            "biggest_loss": row.biggest_loss or 0.0,
        }
```

#### Common Functions

| Function | Description |
|----------|-------------|
| `func.count(col)` | Count rows |
| `func.sum(col)` | Sum values |
| `func.avg(col)` | Average value |
| `func.max(col)` | Maximum value |
| `func.min(col)` | Minimum value |
| `func.coalesce(col, default)` | Replace NULL |

---

### Table Creation

```python
from sqlalchemy import create_engine
from .models import Base

engine = create_engine("sqlite:///./data/poker_coach.db")

def init_database():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
```

---

## Usage in Poker Coach Agent

### Database Configuration (db.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./data/poker_coach.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def init_database():
    """Initialize database and create tables."""
    from .models import Base
    Base.metadata.create_all(bind=engine)
```

### Model Definitions (models.py)

```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class PokerSession(Base):
    __tablename__ = "poker_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    date: Mapped[str] = mapped_column(String(10))
    stake_level: Mapped[str] = mapped_column(String(20))
    buy_in: Mapped[float] = mapped_column(Float)
    cash_out: Mapped[float] = mapped_column(Float)
    profit_loss: Mapped[float] = mapped_column(Float)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hands_played: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    game_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HandHistory(Base):
    __tablename__ = "hand_histories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    hero_hand: Mapped[str] = mapped_column(String(10))
    board: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    position: Mapped[str] = mapped_column(String(5))
    action_summary: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    result: Mapped[str] = mapped_column(String(10))
    stake_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pot_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hand_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    topic: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer)
    questions_attempted: Mapped[int] = mapped_column(Integer)
    correct_answers: Mapped[int] = mapped_column(Integer)
    time_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    question_id: Mapped[str] = mapped_column(String(50))
    scenario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_answer: Mapped[str] = mapped_column(String(100))
    correct_answer: Mapped[str] = mapped_column(String(100))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    time_taken: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### Service Functions (service.py)

```python
from sqlalchemy import select, func
from .db import SessionLocal
from .models import PokerSession, HandHistory, QuizSession, QuizAttempt

def get_poker_sessions(user_id: int = 1, days: int = 0, limit: int = 100) -> List[Dict]:
    """Get poker sessions."""
    with SessionLocal() as session:
        query = select(PokerSession).where(PokerSession.user_id == user_id)

        if days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            query = query.where(PokerSession.created_at >= cutoff)

        query = query.order_by(PokerSession.created_at.desc()).limit(limit)
        result = session.execute(query)

        return [_to_dict(row) for row in result.scalars().all()]

def _to_dict(model: Base) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary."""
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }
```

---

## Common Patterns

### Row to Dictionary Conversion

```python
def row_to_dict(row) -> dict:
    """Convert SQLAlchemy row to dictionary."""
    result = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        # Handle datetime serialization
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result
```

### Bulk Operations

```python
def save_quiz_attempts(attempts: List[Dict]) -> None:
    """Save multiple quiz attempts."""
    with SessionLocal() as session:
        for attempt_data in attempts:
            attempt = QuizAttempt(**attempt_data)
            session.add(attempt)
        session.commit()
```

### Error Handling

```python
from sqlalchemy.exc import SQLAlchemyError

def safe_save(data: Dict) -> bool:
    """Save with error handling."""
    try:
        with SessionLocal() as session:
            record = MyModel(**data)
            session.add(record)
            session.commit()
            return True
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False
```
