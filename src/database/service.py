"""Database service layer for CRUD operations."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

from .db import SessionLocal
from .models import PokerSession, QuizAttempt, QuizSession


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


# ============================================================================
# Poker Session Functions
# ============================================================================


def save_poker_session(session_data: Dict[str, Any], user_id: int = 1) -> int:
    """
    Save a poker session to the database.

    Args:
        session_data: Dict with date, stake_level, buy_in, cash_out,
                     duration_minutes, hands_played, location, game_type, notes
        user_id: User ID (default 1 for single-user mode)

    Returns:
        ID of created session record
    """
    db = SessionLocal()
    try:
        # Calculate profit/loss
        buy_in = session_data.get("buy_in", 0.0)
        cash_out = session_data.get("cash_out", 0.0)
        profit_loss = cash_out - buy_in

        # Parse date if string
        date = session_data.get("date")
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        elif date is None:
            date = datetime.now(timezone.utc)

        db_session = PokerSession(
            user_id=user_id,
            date=date,
            stake_level=session_data.get("stake_level", ""),
            buy_in=buy_in,
            cash_out=cash_out,
            profit_loss=profit_loss,
            duration_minutes=session_data.get("duration_minutes"),
            hands_played=session_data.get("hands_played"),
            location=session_data.get("location"),
            game_type=session_data.get("game_type", "cash"),
            notes=session_data.get("notes"),
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return cast(int, db_session.id)
    finally:
        db.close()


def get_poker_sessions(
    user_id: int = 1,
    days: int = 30,
    stake_level: Optional[str] = None,
    game_type: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get poker sessions for a user.

    Args:
        user_id: User ID
        days: Number of days to look back (0 for all time)
        stake_level: Filter by stake level
        game_type: Filter by game type (cash, tournament)
        limit: Maximum sessions to return

    Returns:
        List of session records as dicts
    """
    db = SessionLocal()
    try:
        query = db.query(PokerSession).filter(PokerSession.user_id == user_id)

        if days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(PokerSession.date >= cutoff)

        if stake_level:
            query = query.filter(PokerSession.stake_level == stake_level)

        if game_type:
            query = query.filter(PokerSession.game_type == game_type)

        sessions = query.order_by(PokerSession.date.desc()).limit(limit).all()

        return [
            {
                "id": s.id,
                "date": s.date.isoformat() if s.date else None,
                "stake_level": s.stake_level,
                "buy_in": s.buy_in,
                "cash_out": s.cash_out,
                "profit_loss": s.profit_loss,
                "duration_minutes": s.duration_minutes,
                "hands_played": s.hands_played,
                "location": s.location,
                "game_type": s.game_type,
                "notes": s.notes,
                "hourly_rate": s.hourly_rate,
                "bb_per_hour": s.bb_per_hour,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ]
    finally:
        db.close()


def get_session_stats(
    user_id: int = 1,
    days: int = 30,
    stake_level: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get aggregated session statistics.

    Args:
        user_id: User ID
        days: Number of days to look back (0 for all time)
        stake_level: Filter by stake level

    Returns:
        Dict with total_sessions, total_profit, total_hours, hourly_rate,
        win_rate, biggest_win, biggest_loss, by_stake, by_location
    """
    db = SessionLocal()
    try:
        query = db.query(PokerSession).filter(PokerSession.user_id == user_id)

        if days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(PokerSession.date >= cutoff)

        if stake_level:
            query = query.filter(PokerSession.stake_level == stake_level)

        sessions = query.all()

        if not sessions:
            return {
                "total_sessions": 0,
                "total_profit": 0.0,
                "total_hours": 0.0,
                "hourly_rate": 0.0,
                "win_rate": 0.0,
                "winning_sessions": 0,
                "losing_sessions": 0,
                "biggest_win": 0.0,
                "biggest_loss": 0.0,
                "average_session": 0.0,
                "by_stake": {},
                "by_location": {},
            }

        total_profit = sum(
            cast(float, s.profit_loss) for s in sessions if s.profit_loss is not None
        )
        total_minutes = sum(
            cast(int, s.duration_minutes)
            for s in sessions
            if s.duration_minutes is not None
        )
        total_hours = total_minutes / 60 if total_minutes > 0 else 0

        profits = [
            cast(float, s.profit_loss) for s in sessions if s.profit_loss is not None
        ]
        winning = sum(1 for p in profits if p > 0)
        losing = sum(1 for p in profits if p < 0)

        # By stake level
        by_stake: Dict[str, Dict[str, Any]] = {}
        for s in sessions:
            stake = cast(str, s.stake_level) if s.stake_level else "Unknown"
            if stake not in by_stake:
                by_stake[stake] = {"sessions": 0, "profit": 0.0, "hours": 0.0}
            by_stake[stake]["sessions"] += 1
            by_stake[stake]["profit"] += (
                cast(float, s.profit_loss) if s.profit_loss else 0.0
            )
            by_stake[stake]["hours"] += (
                (cast(int, s.duration_minutes) / 60) if s.duration_minutes else 0.0
            )

        # By location
        by_location: Dict[str, Dict[str, Any]] = {}
        for s in sessions:
            loc = cast(str, s.location) if s.location else "Unknown"
            if loc not in by_location:
                by_location[loc] = {"sessions": 0, "profit": 0.0}
            by_location[loc]["sessions"] += 1
            by_location[loc]["profit"] += (
                cast(float, s.profit_loss) if s.profit_loss else 0.0
            )

        return {
            "total_sessions": len(sessions),
            "total_profit": total_profit,
            "total_hours": total_hours,
            "hourly_rate": total_profit / total_hours if total_hours > 0 else 0.0,
            "win_rate": (winning / len(sessions) * 100) if sessions else 0.0,
            "winning_sessions": winning,
            "losing_sessions": losing,
            "biggest_win": max(profits) if profits else 0.0,
            "biggest_loss": min(profits) if profits else 0.0,
            "average_session": total_profit / len(sessions) if sessions else 0.0,
            "by_stake": by_stake,
            "by_location": by_location,
        }
    finally:
        db.close()


def get_bankroll_data(
    user_id: int = 1,
    days: int = 90,
) -> Dict[str, Any]:
    """
    Get bankroll progression data for graphing.

    Args:
        user_id: User ID
        days: Number of days to look back (0 for all time)

    Returns:
        Dict with data_points (date, cumulative_profit), current_bankroll
    """
    db = SessionLocal()
    try:
        query = db.query(PokerSession).filter(PokerSession.user_id == user_id)

        # Only apply date filter if days > 0
        if days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(PokerSession.date >= cutoff)

        sessions = query.order_by(PokerSession.date.asc()).all()

        if not sessions:
            return {
                "data_points": [],
                "current_bankroll": 0.0,
                "starting_bankroll": 0.0,
                "peak": 0.0,
                "trough": 0.0,
            }

        # Build cumulative data points
        data_points = []
        cumulative = 0.0
        peak = 0.0
        trough = 0.0

        for s in sessions:
            profit = cast(float, s.profit_loss) if s.profit_loss else 0.0
            cumulative += profit
            peak = max(peak, cumulative)
            trough = min(trough, cumulative)
            data_points.append(
                {
                    "date": s.date.strftime("%Y-%m-%d") if s.date else "",
                    "profit": profit,
                    "cumulative": cumulative,
                }
            )

        return {
            "data_points": data_points,
            "current_bankroll": cumulative,
            "starting_bankroll": 0.0,
            "peak": peak,
            "trough": trough,
        }
    finally:
        db.close()


def delete_poker_session(session_id: int, user_id: int = 1) -> bool:
    """
    Delete a poker session.

    Args:
        session_id: ID of the session to delete
        user_id: User ID (for verification)

    Returns:
        True if deleted, False if not found
    """
    db = SessionLocal()
    try:
        session = (
            db.query(PokerSession)
            .filter(
                PokerSession.id == session_id,
                PokerSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            return False

        db.delete(session)
        db.commit()
        return True
    finally:
        db.close()


def update_poker_session(
    session_id: int,
    updates: Dict[str, Any],
    user_id: int = 1,
) -> bool:
    """
    Update a poker session.

    Args:
        session_id: ID of the session to update
        updates: Dict with fields to update
        user_id: User ID (for verification)

    Returns:
        True if updated, False if not found
    """
    db = SessionLocal()
    try:
        session = (
            db.query(PokerSession)
            .filter(
                PokerSession.id == session_id,
                PokerSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            return False

        # Update allowed fields
        allowed_fields = {
            "date",
            "stake_level",
            "buy_in",
            "cash_out",
            "duration_minutes",
            "hands_played",
            "location",
            "game_type",
            "notes",
        }

        for field, value in updates.items():
            if field in allowed_fields:
                if field == "date" and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                setattr(session, field, value)

        # Recalculate profit/loss if buy_in or cash_out changed
        if "buy_in" in updates or "cash_out" in updates:
            profit = cast(float, session.cash_out) - cast(float, session.buy_in)
            session.profit_loss = profit  # type: ignore[assignment]

        db.commit()
        return True
    finally:
        db.close()
