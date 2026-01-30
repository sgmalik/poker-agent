"""Database service layer for CRUD operations."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

import csv
import io
import json

from .db import SessionLocal
from .models import HandHistory, PokerSession, QuizAttempt, QuizSession


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


def get_poker_session_by_id(session_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single poker session by ID.

    Args:
        session_id: Session ID

    Returns:
        Session record as dict, or None if not found
    """
    db = SessionLocal()
    try:
        s = db.query(PokerSession).filter(PokerSession.id == session_id).first()
        if not s:
            return None

        return {
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


# ============================================================================
# Hand History Functions
# ============================================================================


def save_hand_history(hand_data: Dict[str, Any], user_id: int = 1) -> int:
    """
    Save a hand history to the database.

    Args:
        hand_data: Dict with hero_hand, board, position, action_summary,
                  result, stake_level, pot_size, tags, notes, hand_text
        user_id: User ID (default 1 for single-user mode)

    Returns:
        ID of created hand history record
    """
    db = SessionLocal()
    try:
        # Handle tags - convert list to comma-separated string
        tags = hand_data.get("tags")
        if isinstance(tags, list):
            tags = ", ".join(tags)

        db_hand = HandHistory(
            user_id=user_id,
            hero_hand=hand_data.get("hero_hand", ""),
            board=hand_data.get("board"),
            position=hand_data.get("position", ""),
            action_summary=hand_data.get("action_summary"),
            result=hand_data.get("result", ""),
            stake_level=hand_data.get("stake_level"),
            pot_size=hand_data.get("pot_size"),
            tags=tags,
            notes=hand_data.get("notes"),
            hand_text=hand_data.get("hand_text"),
        )
        db.add(db_hand)
        db.commit()
        db.refresh(db_hand)
        return cast(int, db_hand.id)
    finally:
        db.close()


def get_hand_histories(
    user_id: int = 1,
    days: int = 0,
    tags: Optional[List[str]] = None,
    result: Optional[str] = None,
    position: Optional[str] = None,
    stake_level: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get hand histories for a user with optional filters.

    Args:
        user_id: User ID
        days: Number of days to look back (0 for all time)
        tags: Filter by tags (any match)
        result: Filter by result (won, lost, split)
        position: Filter by position
        stake_level: Filter by stake level
        limit: Maximum records to return

    Returns:
        List of hand history records as dicts
    """
    db = SessionLocal()
    try:
        query = db.query(HandHistory).filter(HandHistory.user_id == user_id)

        if days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(HandHistory.created_at >= cutoff)

        if result:
            query = query.filter(HandHistory.result == result)

        if position:
            query = query.filter(HandHistory.position == position)

        if stake_level:
            query = query.filter(HandHistory.stake_level == stake_level)

        hands = query.order_by(HandHistory.created_at.desc()).limit(limit).all()

        # Filter by tags in Python (SQLite doesn't have good array support)
        if tags:
            filtered_hands = []
            for h in hands:
                hand_tags = h.tag_list
                if any(t in hand_tags for t in tags):
                    filtered_hands.append(h)
            hands = filtered_hands

        return [
            {
                "id": h.id,
                "hero_hand": h.hero_hand,
                "board": h.board,
                "position": h.position,
                "action_summary": h.action_summary,
                "result": h.result,
                "stake_level": h.stake_level,
                "pot_size": h.pot_size,
                "tags": h.tag_list,
                "notes": h.notes,
                "hand_text": h.hand_text,
                "street": h.street,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in hands
        ]
    finally:
        db.close()


def get_hand_history_by_id(
    hand_id: int,
    user_id: int = 1,
) -> Optional[Dict[str, Any]]:
    """
    Get a single hand history by ID.

    Args:
        hand_id: Hand history ID
        user_id: User ID (for verification)

    Returns:
        Hand history as dict, or None if not found
    """
    db = SessionLocal()
    try:
        hand = (
            db.query(HandHistory)
            .filter(
                HandHistory.id == hand_id,
                HandHistory.user_id == user_id,
            )
            .first()
        )

        if not hand:
            return None

        return {
            "id": hand.id,
            "hero_hand": hand.hero_hand,
            "board": hand.board,
            "position": hand.position,
            "action_summary": hand.action_summary,
            "result": hand.result,
            "stake_level": hand.stake_level,
            "pot_size": hand.pot_size,
            "tags": hand.tag_list,
            "notes": hand.notes,
            "hand_text": hand.hand_text,
            "street": hand.street,
            "created_at": hand.created_at.isoformat() if hand.created_at else None,
        }
    finally:
        db.close()


def update_hand_history(
    hand_id: int,
    updates: Dict[str, Any],
    user_id: int = 1,
) -> bool:
    """
    Update a hand history.

    Args:
        hand_id: ID of the hand to update
        updates: Dict with fields to update
        user_id: User ID (for verification)

    Returns:
        True if updated, False if not found
    """
    db = SessionLocal()
    try:
        hand = (
            db.query(HandHistory)
            .filter(
                HandHistory.id == hand_id,
                HandHistory.user_id == user_id,
            )
            .first()
        )

        if not hand:
            return False

        allowed_fields = {
            "hero_hand",
            "board",
            "position",
            "action_summary",
            "result",
            "stake_level",
            "pot_size",
            "tags",
            "notes",
            "hand_text",
        }

        for field, value in updates.items():
            if field in allowed_fields:
                # Convert tag list to comma-separated string
                if field == "tags" and isinstance(value, list):
                    value = ", ".join(value)
                setattr(hand, field, value)

        db.commit()
        return True
    finally:
        db.close()


def delete_hand_history(hand_id: int, user_id: int = 1) -> bool:
    """
    Delete a hand history.

    Args:
        hand_id: ID of the hand to delete
        user_id: User ID (for verification)

    Returns:
        True if deleted, False if not found
    """
    db = SessionLocal()
    try:
        hand = (
            db.query(HandHistory)
            .filter(
                HandHistory.id == hand_id,
                HandHistory.user_id == user_id,
            )
            .first()
        )

        if not hand:
            return False

        db.delete(hand)
        db.commit()
        return True
    finally:
        db.close()


def get_hand_history_stats(
    user_id: int = 1,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Get aggregated hand history statistics.

    Args:
        user_id: User ID
        days: Number of days to look back (0 for all time)

    Returns:
        Dict with total_hands, wins, losses, splits, win_rate,
        by_position, by_tag, common_tags
    """
    db = SessionLocal()
    try:
        query = db.query(HandHistory).filter(HandHistory.user_id == user_id)

        if days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(HandHistory.created_at >= cutoff)

        hands = query.all()

        if not hands:
            return {
                "total_hands": 0,
                "wins": 0,
                "losses": 0,
                "splits": 0,
                "win_rate": 0.0,
                "by_position": {},
                "by_tag": {},
                "common_tags": [],
            }

        total = len(hands)
        wins = sum(1 for h in hands if h.result == "won")
        losses = sum(1 for h in hands if h.result == "lost")
        splits = sum(1 for h in hands if h.result == "split")

        # By position
        by_position: Dict[str, Dict[str, int]] = {}
        for h in hands:
            pos = cast(str, h.position) if h.position else "Unknown"
            if pos not in by_position:
                by_position[pos] = {"total": 0, "won": 0, "lost": 0}
            by_position[pos]["total"] += 1
            if h.result == "won":
                by_position[pos]["won"] += 1
            elif h.result == "lost":
                by_position[pos]["lost"] += 1

        # By tag
        by_tag: Dict[str, Dict[str, int]] = {}
        tag_counts: Dict[str, int] = {}
        for h in hands:
            for tag in h.tag_list:
                if tag not in by_tag:
                    by_tag[tag] = {"total": 0, "won": 0, "lost": 0}
                by_tag[tag]["total"] += 1
                if h.result == "won":
                    by_tag[tag]["won"] += 1
                elif h.result == "lost":
                    by_tag[tag]["lost"] += 1
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Common tags (sorted by frequency)
        common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        common_tags = [tag for tag, _ in common_tags]

        return {
            "total_hands": total,
            "wins": wins,
            "losses": losses,
            "splits": splits,
            "win_rate": (wins / total * 100) if total > 0 else 0.0,
            "by_position": by_position,
            "by_tag": by_tag,
            "common_tags": common_tags,
        }
    finally:
        db.close()


def get_all_tags(user_id: int = 1) -> List[str]:
    """
    Get all unique tags used by a user.

    Args:
        user_id: User ID

    Returns:
        List of unique tags
    """
    db = SessionLocal()
    try:
        hands = db.query(HandHistory).filter(HandHistory.user_id == user_id).all()

        all_tags: set[str] = set()
        for h in hands:
            all_tags.update(h.tag_list)

        return sorted(all_tags)
    finally:
        db.close()


def export_hand_histories(
    user_id: int = 1,
    days: int = 0,
    format: str = "json",
) -> str:
    """
    Export hand histories to JSON or CSV format.

    Args:
        user_id: User ID
        days: Number of days to look back (0 for all time)
        format: Export format ("json" or "csv")

    Returns:
        Exported data as string
    """
    hands = get_hand_histories(user_id=user_id, days=days, limit=10000)

    if format == "csv":
        output = io.StringIO()
        if hands:
            # Use all keys from first hand as headers
            fieldnames = list(hands[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for h in hands:
                # Convert tags list to comma-separated for CSV
                row = h.copy()
                row["tags"] = ", ".join(row.get("tags", []))
                writer.writerow(row)
        return output.getvalue()
    else:
        return json.dumps(hands, indent=2)


def import_hand_histories(
    data: str,
    format: str = "json",
    user_id: int = 1,
) -> int:
    """
    Import hand histories from JSON or CSV format.

    Args:
        data: Import data as string
        format: Import format ("json" or "csv")
        user_id: User ID

    Returns:
        Number of hands imported
    """
    imported = 0

    if format == "csv":
        reader = csv.DictReader(io.StringIO(data))
        for row in reader:
            # Parse tags from comma-separated string
            tags_str = row.get("tags", "")
            if tags_str:
                row["tags"] = [t.strip() for t in tags_str.split(",")]
            else:
                row["tags"] = []

            # Convert pot_size to float if present
            if row.get("pot_size"):
                try:
                    row["pot_size"] = float(row["pot_size"])
                except ValueError:
                    row["pot_size"] = None

            save_hand_history(row, user_id=user_id)
            imported += 1
    else:
        hands = json.loads(data)
        for hand in hands:
            save_hand_history(hand, user_id=user_id)
            imported += 1

    return imported
