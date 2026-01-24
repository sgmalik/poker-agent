"""Database module for quiz persistence and statistics."""

from .db import Base, SessionLocal, engine, get_db, init_db
from .models import QuizAttempt, QuizSession
from .service import (
    get_question_performance,
    get_quiz_stats,
    get_recent_sessions,
    identify_study_leaks,
    save_quiz_attempt,
    save_quiz_session,
)

__all__ = [
    # Database setup
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    # Models
    "QuizAttempt",
    "QuizSession",
    # Service functions
    "save_quiz_attempt",
    "save_quiz_session",
    "get_quiz_stats",
    "identify_study_leaks",
    "get_recent_sessions",
    "get_question_performance",
]
