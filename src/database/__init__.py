"""Database module for quiz persistence and statistics."""

from .db import Base, SessionLocal, engine, get_db, init_db
from .models import HandHistory, PokerSession, QuizAttempt, QuizSession
from .service import (
    # Hand history functions
    delete_hand_history,
    export_hand_histories,
    get_all_tags,
    get_hand_histories,
    get_hand_history_by_id,
    get_hand_history_stats,
    import_hand_histories,
    save_hand_history,
    update_hand_history,
    # Quiz functions
    get_question_performance,
    get_quiz_stats,
    get_recent_sessions,
    identify_study_leaks,
    save_quiz_attempt,
    save_quiz_session,
    # Poker session functions
    delete_poker_session,
    get_bankroll_data,
    get_poker_sessions,
    get_session_stats,
    save_poker_session,
    update_poker_session,
)

__all__ = [
    # Database setup
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    # Models
    "HandHistory",
    "PokerSession",
    "QuizAttempt",
    "QuizSession",
    # Quiz service functions
    "save_quiz_attempt",
    "save_quiz_session",
    "get_quiz_stats",
    "identify_study_leaks",
    "get_recent_sessions",
    "get_question_performance",
    # Poker session service functions
    "save_poker_session",
    "get_poker_sessions",
    "get_session_stats",
    "get_bankroll_data",
    "delete_poker_session",
    "update_poker_session",
    # Hand history service functions
    "save_hand_history",
    "get_hand_histories",
    "get_hand_history_by_id",
    "update_hand_history",
    "delete_hand_history",
    "get_hand_history_stats",
    "get_all_tags",
    "export_hand_histories",
    "import_hand_histories",
]
