"""Database service layer for CRUD operations."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

from .db import SessionLocal
from .models import QuizAttempt, QuizSession


def save_quiz_attempt(attempt: Dict[str, Any], user_id: int = 1) -> int:
    """
    Save a single quiz attempt to the database.

    Args:
        attempt: Dict with question_id, user_answer, correct_answer,
                is_correct, time_taken, difficulty, topic
        user_id: User ID (default 1 for single-user mode)

    Returns:
        ID of created attempt record
    """
    db = SessionLocal()
    try:
        db_attempt = QuizAttempt(
            user_id=user_id,
            question_id=attempt.get("question_id", ""),
            scenario=attempt.get("scenario"),
            user_answer=attempt.get("user_answer", ""),
            correct_answer=attempt.get("correct_answer", ""),
            is_correct=attempt.get("is_correct", False),
            time_taken=attempt.get("time_taken"),
            difficulty=attempt.get("difficulty"),
            topic=attempt.get("topic"),
        )
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        return cast(int, db_attempt.id)
    finally:
        db.close()


def save_quiz_session(
    results: Dict[str, Any],
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    user_id: int = 1,
) -> int:
    """
    Save a quiz session summary to the database.

    Args:
        results: Quiz results dict from QuizEngine
        topic: Topic filter used (None for all)
        difficulty: Difficulty filter used (None for all)
        user_id: User ID (default 1)

    Returns:
        ID of created session record
    """
    db = SessionLocal()
    try:
        session = QuizSession(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            total_questions=results.get("total", 0),
            correct_answers=results.get("score", 0),
            time_total=results.get("time_total"),
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Also save individual attempts
        for answer in results.get("answers", []):
            save_quiz_attempt(answer, user_id=user_id)

        return cast(int, session.id)
    finally:
        db.close()


def get_quiz_stats(
    user_id: int = 1,
    topic: Optional[str] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Get quiz statistics for a user.

    Args:
        user_id: User ID
        topic: Filter by topic (None for all)
        days: Number of days to look back

    Returns:
        Dict with total_attempts, correct, percentage, by_topic, by_difficulty
    """
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        query = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.created_at >= cutoff,
        )

        if topic:
            query = query.filter(QuizAttempt.topic == topic)

        attempts = query.all()

        if not attempts:
            return {
                "total_attempts": 0,
                "correct": 0,
                "percentage": 0.0,
                "by_topic": {},
                "by_difficulty": {},
            }

        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)

        # By topic
        by_topic: Dict[str, Dict[str, int]] = {}
        for a in attempts:
            t = cast(str, a.topic) if a.topic else "unknown"
            if t not in by_topic:
                by_topic[t] = {"total": 0, "correct": 0}
            by_topic[t]["total"] += 1
            if a.is_correct:
                by_topic[t]["correct"] += 1

        # By difficulty
        by_difficulty: Dict[str, Dict[str, int]] = {}
        for a in attempts:
            d = cast(str, a.difficulty) if a.difficulty else "unknown"
            if d not in by_difficulty:
                by_difficulty[d] = {"total": 0, "correct": 0}
            by_difficulty[d]["total"] += 1
            if a.is_correct:
                by_difficulty[d]["correct"] += 1

        return {
            "total_attempts": total,
            "correct": correct,
            "percentage": (correct / total * 100) if total > 0 else 0.0,
            "by_topic": by_topic,
            "by_difficulty": by_difficulty,
        }
    finally:
        db.close()


def identify_study_leaks(
    user_id: int = 1,
    min_attempts: int = 5,
    threshold: float = 60.0,
) -> List[Dict[str, Any]]:
    """
    Find weak areas based on quiz history.

    Args:
        user_id: User ID
        min_attempts: Minimum attempts needed to identify a leak
        threshold: Percentage below which topic is considered weak

    Returns:
        List of weak areas with topic, percentage, and recommendation
    """
    stats = get_quiz_stats(user_id=user_id)
    leaks = []

    for topic, data in stats.get("by_topic", {}).items():
        total = data.get("total", 0)
        correct = data.get("correct", 0)

        if total < min_attempts:
            continue

        pct = (correct / total * 100) if total > 0 else 0

        if pct < threshold:
            leaks.append(
                {
                    "topic": topic,
                    "attempts": total,
                    "correct": correct,
                    "percentage": pct,
                    "recommendation": f"Focus more practice on {topic.replace('_', ' ')} questions",
                }
            )

    # Sort by percentage (worst first)
    leaks.sort(key=lambda x: x["percentage"])

    return leaks


def get_recent_sessions(
    user_id: int = 1,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Get recent quiz sessions.

    Args:
        user_id: User ID
        limit: Maximum sessions to return

    Returns:
        List of session summaries
    """
    db = SessionLocal()
    try:
        sessions = (
            db.query(QuizSession)
            .filter(QuizSession.user_id == user_id)
            .order_by(QuizSession.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": s.id,
                "topic": s.topic or "All",
                "difficulty": s.difficulty or "All",
                "score": s.correct_answers,
                "total": s.total_questions,
                "percentage": s.percentage,
                "time_total": s.time_total,
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
    finally:
        db.close()


def get_question_performance(
    user_id: int = 1,
    question_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get performance on specific questions.

    Args:
        user_id: User ID
        question_id: Specific question ID (None for all)

    Returns:
        Dict mapping question_id to performance stats
    """
    db = SessionLocal()
    try:
        query = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)

        if question_id:
            query = query.filter(QuizAttempt.question_id == question_id)

        attempts = query.all()

        # Group by question
        by_question: Dict[str, Dict[str, Any]] = {}
        for a in attempts:
            qid = cast(str, a.question_id)
            if qid not in by_question:
                by_question[qid] = {
                    "attempts": 0,
                    "correct": 0,
                    "topic": cast(str, a.topic) if a.topic else None,
                    "difficulty": cast(str, a.difficulty) if a.difficulty else None,
                }
            by_question[qid]["attempts"] += 1
            if a.is_correct:
                by_question[qid]["correct"] += 1

        # Calculate percentages
        for qid, data in by_question.items():
            data["percentage"] = (
                (data["correct"] / data["attempts"] * 100)
                if data["attempts"] > 0
                else 0.0
            )

        return by_question
    finally:
        db.close()
