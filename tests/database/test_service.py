"""Tests for database service layer."""

import pytest
import tempfile
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.db import Base
from src.database import service


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create temp file for test DB
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create engine and tables
    test_engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(bind=test_engine)

    # Patch the service module to use test DB
    original_session = service.SessionLocal
    service.SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    yield test_engine

    # Cleanup
    service.SessionLocal = original_session
    os.unlink(path)


class TestSaveQuizAttempt:
    """Tests for save_quiz_attempt function."""

    def test_saves_attempt(self, test_db):
        """Should save an attempt to database."""
        attempt = {
            "question_id": "test_001",
            "user_answer": "Raise",
            "correct_answer": "Raise",
            "is_correct": True,
            "time_taken": 10,
            "difficulty": "beginner",
            "topic": "preflop",
        }

        attempt_id = service.save_quiz_attempt(attempt)
        assert attempt_id > 0

    def test_saves_with_user_id(self, test_db):
        """Should save with specified user ID."""
        attempt = {
            "question_id": "test_002",
            "user_answer": "Fold",
            "correct_answer": "Raise",
            "is_correct": False,
            "topic": "ranges",
        }

        attempt_id = service.save_quiz_attempt(attempt, user_id=42)
        assert attempt_id > 0


class TestSaveQuizSession:
    """Tests for save_quiz_session function."""

    def test_saves_session(self, test_db):
        """Should save a session to database."""
        results = {
            "score": 8,
            "total": 10,
            "time_total": 120,
            "answers": [],
        }

        session_id = service.save_quiz_session(
            results, topic="preflop", difficulty="beginner"
        )
        assert session_id > 0

    def test_saves_with_answers(self, test_db):
        """Should save session with answer records."""
        results = {
            "score": 1,
            "total": 2,
            "time_total": 30,
            "answers": [
                {
                    "question_id": "q1",
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": True,
                    "topic": "preflop",
                },
                {
                    "question_id": "q2",
                    "user_answer": "B",
                    "correct_answer": "C",
                    "is_correct": False,
                    "topic": "ranges",
                },
            ],
        }

        session_id = service.save_quiz_session(results)
        assert session_id > 0


class TestGetQuizStats:
    """Tests for get_quiz_stats function."""

    def test_returns_empty_stats(self, test_db):
        """Should return empty stats when no data."""
        stats = service.get_quiz_stats(user_id=999)
        assert stats["total_attempts"] == 0
        assert stats["correct"] == 0
        assert stats["percentage"] == 0.0

    def test_calculates_stats(self, test_db):
        """Should calculate stats correctly."""
        # Add some attempts
        attempts = [
            {
                "question_id": "q1",
                "user_answer": "A",
                "correct_answer": "A",
                "is_correct": True,
                "topic": "preflop",
            },
            {
                "question_id": "q2",
                "user_answer": "B",
                "correct_answer": "A",
                "is_correct": False,
                "topic": "preflop",
            },
            {
                "question_id": "q3",
                "user_answer": "C",
                "correct_answer": "C",
                "is_correct": True,
                "topic": "ranges",
            },
        ]

        for a in attempts:
            service.save_quiz_attempt(a)

        stats = service.get_quiz_stats()
        assert stats["total_attempts"] == 3
        assert stats["correct"] == 2
        assert abs(stats["percentage"] - 66.67) < 1


class TestIdentifyStudyLeaks:
    """Tests for identify_study_leaks function."""

    def test_returns_empty_with_no_data(self, test_db):
        """Should return empty list with no data."""
        leaks = service.identify_study_leaks(user_id=999)
        assert leaks == []

    def test_identifies_weak_topic(self, test_db):
        """Should identify topics below threshold."""
        # Add attempts with poor preflop performance
        for i in range(6):
            service.save_quiz_attempt(
                {
                    "question_id": f"pf_{i}",
                    "user_answer": "A",
                    "correct_answer": "B" if i < 4 else "A",  # 2/6 correct = 33%
                    "is_correct": i >= 4,
                    "topic": "preflop",
                }
            )

        leaks = service.identify_study_leaks(threshold=60.0, min_attempts=5)
        assert len(leaks) >= 1
        assert any(leak["topic"] == "preflop" for leak in leaks)


class TestGetRecentSessions:
    """Tests for get_recent_sessions function."""

    def test_returns_empty_with_no_sessions(self, test_db):
        """Should return empty list with no sessions."""
        sessions = service.get_recent_sessions(user_id=999)
        assert sessions == []

    def test_returns_recent_sessions(self, test_db):
        """Should return sessions in reverse chronological order."""
        # Add sessions
        for i in range(3):
            results = {"score": i + 1, "total": 5, "time_total": 60, "answers": []}
            service.save_quiz_session(results)

        sessions = service.get_recent_sessions(limit=10)
        assert len(sessions) == 3
        # Most recent first
        assert sessions[0]["score"] == 3


class TestGetQuestionPerformance:
    """Tests for get_question_performance function."""

    def test_returns_empty_with_no_data(self, test_db):
        """Should return empty dict with no data."""
        perf = service.get_question_performance(user_id=999)
        assert perf == {}

    def test_tracks_question_performance(self, test_db):
        """Should track performance by question."""
        # Answer same question multiple times
        for _ in range(3):
            service.save_quiz_attempt(
                {
                    "question_id": "q1",
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": True,
                    "topic": "preflop",
                }
            )

        service.save_quiz_attempt(
            {
                "question_id": "q1",
                "user_answer": "B",
                "correct_answer": "A",
                "is_correct": False,
                "topic": "preflop",
            }
        )

        perf = service.get_question_performance()
        assert "q1" in perf
        assert perf["q1"]["attempts"] == 4
        assert perf["q1"]["correct"] == 3
        assert perf["q1"]["percentage"] == 75.0
