"""SQLAlchemy database models."""

from datetime import datetime, timezone
from typing import cast

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .db import Base


class QuizAttempt(Base):
    """Model for storing individual quiz question attempts."""

    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    question_id = Column(String(50), nullable=False)
    scenario = Column(Text, nullable=True)
    user_answer = Column(String(100), nullable=False)
    correct_answer = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=True)  # seconds
    difficulty = Column(String(20), nullable=True)
    topic = Column(String(50), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, question_id='{self.question_id}', is_correct={self.is_correct})>"


class QuizSession(Base):
    """Model for storing quiz session summaries."""

    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    topic = Column(String(50), nullable=True)  # None = all topics
    difficulty = Column(String(20), nullable=True)  # None = all difficulties
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    time_total = Column(Integer, nullable=True)  # seconds
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    @property
    def percentage(self) -> float:
        """Calculate score percentage."""
        total = cast(int, self.total_questions) if self.total_questions else 0
        correct = cast(int, self.correct_answers) if self.correct_answers else 0
        if total == 0:
            return 0.0
        return (correct / total) * 100

    def __repr__(self) -> str:
        return f"<QuizSession(id={self.id}, score={self.correct_answers}/{self.total_questions})>"
