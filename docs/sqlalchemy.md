# SQLAlchemy Reference

SQLAlchemy is a Python SQL toolkit and ORM. This covers SQLAlchemy 2.0 patterns.

## Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite (file)
DATABASE_URL = "sqlite:///data/app.db"

# SQLite (memory, for testing)
DATABASE_URL = "sqlite:///:memory:"

# PostgreSQL
DATABASE_URL = "postgresql://user:pass@localhost/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite only
    echo=True,  # Log SQL statements (debug)
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
```

## Defining Models

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    posts = relationship("Post", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    views = Column(Integer, default=0)
    score = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="posts")
```

### Column Types

| SQLAlchemy | Python | Notes |
|------------|--------|-------|
| `Integer` | `int` | |
| `String(n)` | `str` | Max length n |
| `Text` | `str` | Unlimited length |
| `Boolean` | `bool` | |
| `Float` | `float` | |
| `DateTime` | `datetime` | |
| `Date` | `date` | |
| `JSON` | `dict/list` | Native JSON support |

### Column Options

```python
Column(Integer, primary_key=True)
Column(String, nullable=False)           # NOT NULL
Column(String, unique=True)              # UNIQUE constraint
Column(String, index=True)               # Create index
Column(Integer, default=0)               # Default value
Column(DateTime, default=datetime.now)   # Callable default
Column(Integer, ForeignKey("table.id"))  # Foreign key
```

## Creating Tables

```python
# Create all tables
Base.metadata.create_all(bind=engine)

# Drop all tables (careful!)
Base.metadata.drop_all(bind=engine)
```

## Session Management

```python
# Get session
db = SessionLocal()

try:
    # ... do work ...
    db.commit()
except:
    db.rollback()
    raise
finally:
    db.close()

# Or use context manager pattern
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## CRUD Operations

### Create

```python
# Single record
user = User(email="test@example.com", name="Test")
db.add(user)
db.commit()
db.refresh(user)  # Reload to get generated ID
print(user.id)  # Now has ID

# Multiple records
users = [User(email="a@b.com"), User(email="c@d.com")]
db.add_all(users)
db.commit()
```

### Read

```python
# Get by primary key
user = db.get(User, 1)  # Returns User or None

# Query all
users = db.query(User).all()

# First result
user = db.query(User).first()

# Filter (WHERE)
user = db.query(User).filter(User.email == "test@example.com").first()

# Multiple conditions
users = db.query(User).filter(
    User.is_active == True,
    User.name != None
).all()

# Filter with OR
from sqlalchemy import or_
users = db.query(User).filter(
    or_(User.name == "Alice", User.name == "Bob")
).all()

# LIKE
users = db.query(User).filter(User.email.like("%@gmail.com")).all()

# IN
users = db.query(User).filter(User.id.in_([1, 2, 3])).all()

# Order by
users = db.query(User).order_by(User.created_at.desc()).all()

# Limit/offset
users = db.query(User).limit(10).offset(20).all()

# Count
count = db.query(User).filter(User.is_active == True).count()
```

### Update

```python
# Fetch then update
user = db.query(User).filter(User.id == 1).first()
user.name = "New Name"
db.commit()

# Bulk update
db.query(User).filter(User.is_active == False).update({"is_active": True})
db.commit()
```

### Delete

```python
# Fetch then delete
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()

# Bulk delete
db.query(User).filter(User.is_active == False).delete()
db.commit()
```

## Relationships

### One-to-Many

```python
class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")

# Usage
author = Author()
book = Book(author=author)
# or
author.books.append(book)
```

### Querying Relationships

```python
# Access related objects (lazy load)
author = db.query(Author).first()
for book in author.books:
    print(book.title)

# Eager load (avoid N+1)
from sqlalchemy.orm import joinedload
authors = db.query(Author).options(joinedload(Author.books)).all()

# Filter by relationship
books = db.query(Book).join(Author).filter(Author.name == "Alice").all()
```

## Aggregations

```python
from sqlalchemy import func

# Count
total = db.query(func.count(User.id)).scalar()

# Sum
total_views = db.query(func.sum(Post.views)).scalar()

# Average
avg_score = db.query(func.avg(Post.score)).scalar()

# Group by
results = db.query(
    Post.user_id,
    func.count(Post.id).label("post_count")
).group_by(Post.user_id).all()

for user_id, count in results:
    print(f"User {user_id}: {count} posts")
```

## Raw SQL

```python
from sqlalchemy import text

# Execute raw SQL
result = db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
rows = result.fetchall()

# With ORM mapping
users = db.query(User).from_statement(
    text("SELECT * FROM users WHERE email LIKE :pattern")
).params(pattern="%@gmail.com").all()
```

## Transactions

```python
# Auto-commit on success
try:
    user = User(email="test@example.com")
    db.add(user)
    post = Post(title="Hello", user_id=user.id)
    db.add(post)
    db.commit()  # Commits both
except Exception:
    db.rollback()  # Rolls back everything
    raise
```

## Common Patterns

### Service Layer

```python
def create_user(email: str, name: str = None) -> int:
    db = SessionLocal()
    try:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
    finally:
        db.close()

def get_user_by_email(email: str) -> User | None:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()
```

### Pagination

```python
def get_users_paginated(page: int = 1, per_page: int = 20):
    db = SessionLocal()
    try:
        offset = (page - 1) * per_page
        users = db.query(User).offset(offset).limit(per_page).all()
        total = db.query(func.count(User.id)).scalar()
        return {
            "items": users,
            "total": total,
            "page": page,
            "pages": (total + per_page - 1) // per_page
        }
    finally:
        db.close()
```

### Upsert (Insert or Update)

```python
from sqlalchemy.dialects.sqlite import insert

stmt = insert(User).values(email="test@example.com", name="Test")
stmt = stmt.on_conflict_do_update(
    index_elements=["email"],
    set_={"name": stmt.excluded.name}
)
db.execute(stmt)
db.commit()
```

## Tips

- Always close sessions (use try/finally or context manager)
- Use `db.refresh(obj)` after commit to get generated values
- Use `index=True` on frequently queried columns
- Use `joinedload` for relationships you'll access (avoid N+1)
- `nullable=False` is safer than allowing NULL
- Keep session scope small - don't hold open for long
