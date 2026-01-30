"""LangChain tools for quiz statistics and study analysis (Mode 3)."""

from typing import Any, Optional

from langchain_core.tools import tool

from ..database.service import get_quiz_stats, identify_study_leaks, get_recent_sessions


@tool
def get_quiz_performance(
    topic: Optional[str] = None,
    days: int = 30,
) -> dict[str, Any]:
    """
    Get quiz performance statistics for the user.

    Args:
        topic: Filter by specific topic (optional). Valid topics include:
            - preflop: Preflop decision making
            - ranges: Range understanding
            - pot_odds: Pot odds calculations
            - hand_strength: Hand strength evaluation
            - position: Positional play
            - postflop: Postflop strategy
            - game_theory: Game theory concepts
            - tournament: Tournament-specific concepts
        days: Number of days to look back (default 30)

    Returns:
        Dictionary containing:
        - total_attempts: Total number of quiz questions attempted
        - correct: Number of correct answers
        - percentage: Overall accuracy percentage
        - by_topic: Performance breakdown by topic
        - by_difficulty: Performance breakdown by difficulty level

    Example:
        get_quiz_performance(topic="pot_odds", days=7) -> {"total_attempts": 25, "correct": 20, "percentage": 80.0, ...}
    """
    try:
        stats = get_quiz_stats(user_id=1, topic=topic, days=days)

        return {
            "success": True,
            "period_days": days,
            "filtered_topic": topic,
            "total_attempts": stats["total_attempts"],
            "correct": stats["correct"],
            "percentage": round(stats["percentage"], 1),
            "by_topic": stats["by_topic"],
            "by_difficulty": stats["by_difficulty"],
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting quiz stats: {str(e)}"}


@tool
def find_study_leaks(
    min_attempts: int = 5,
    threshold: float = 60.0,
) -> dict[str, Any]:
    """
    Identify weak areas in the user's poker knowledge based on quiz history.

    This analyzes quiz performance to find topics where the user struggles,
    helping them focus their study efforts on areas that need improvement.

    Args:
        min_attempts: Minimum number of attempts needed to identify a leak (default 5)
        threshold: Percentage below which a topic is considered weak (default 60.0)

    Returns:
        Dictionary containing:
        - leaks: List of weak areas, each with:
            - topic: The topic name
            - attempts: Number of questions attempted
            - correct: Number correct
            - percentage: Accuracy percentage
            - recommendation: Study recommendation

    Example:
        find_study_leaks() -> {"leaks": [{"topic": "pot_odds", "percentage": 45.0, "recommendation": "Focus more practice on pot odds questions"}, ...]}
    """
    try:
        leaks = identify_study_leaks(
            user_id=1, min_attempts=min_attempts, threshold=threshold
        )

        if not leaks:
            return {
                "success": True,
                "leaks": [],
                "message": "No significant study leaks found. Keep up the good work!",
            }

        return {
            "success": True,
            "leaks": leaks,
            "message": f"Found {len(leaks)} area(s) needing improvement",
        }
    except Exception as e:
        return {"success": False, "error": f"Error identifying leaks: {str(e)}"}


@tool
def get_recent_quiz_sessions(limit: int = 10) -> dict[str, Any]:
    """
    Get recent quiz session history.

    Args:
        limit: Maximum number of sessions to return (default 10)

    Returns:
        Dictionary containing:
        - sessions: List of recent quiz sessions, each with:
            - topic: Topic studied (or "All")
            - difficulty: Difficulty level (or "All")
            - score: Number of correct answers
            - total: Total questions in session
            - percentage: Accuracy percentage
            - created_at: When the session was completed

    Example:
        get_recent_quiz_sessions(limit=5) -> {"sessions": [{"topic": "preflop", "score": 8, "total": 10, "percentage": 80.0}, ...]}
    """
    try:
        sessions = get_recent_sessions(user_id=1, limit=limit)

        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions),
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting sessions: {str(e)}"}


# Export all tools
QUIZ_TOOLS = [get_quiz_performance, find_study_leaks, get_recent_quiz_sessions]
