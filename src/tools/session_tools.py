"""LangChain tools for poker session tracking and bankroll analysis (Mode 4)."""

from typing import Any, Optional

from langchain_core.tools import tool

from ..database.service import (
    get_poker_sessions,
    get_session_stats,
    get_bankroll_data,
)
from ..core.session_tracker import (
    analyze_bankroll_health,
    calculate_max_drawdown,
    calculate_streak_info,
)


@tool
def get_session_statistics(
    days: int = 30,
    stake_level: Optional[str] = None,
) -> dict[str, Any]:
    """
    Get aggregated statistics for poker sessions.

    Args:
        days: Number of days to look back (0 for all time, default 30)
        stake_level: Filter by specific stake level (optional, e.g., "1/2", "2/5", "NL100")

    Returns:
        Dictionary containing:
        - total_sessions: Number of sessions played
        - total_profit: Total profit/loss in dollars
        - total_hours: Total hours played
        - hourly_rate: Average dollars per hour
        - win_rate: Percentage of winning sessions
        - winning_sessions: Number of winning sessions
        - losing_sessions: Number of losing sessions
        - biggest_win: Largest single session win
        - biggest_loss: Largest single session loss
        - average_session: Average profit per session
        - by_stake: Breakdown by stake level
        - by_location: Breakdown by location

    Example:
        get_session_statistics(days=90) -> {"total_profit": 1500.0, "hourly_rate": 25.0, "win_rate": 65.0, ...}
    """
    try:
        stats = get_session_stats(user_id=1, days=days, stake_level=stake_level)

        return {
            "success": True,
            "period_days": days if days > 0 else "all_time",
            "stake_filter": stake_level,
            "total_sessions": stats["total_sessions"],
            "total_profit": round(stats["total_profit"], 2),
            "total_hours": round(stats["total_hours"], 1),
            "hourly_rate": round(stats["hourly_rate"], 2),
            "win_rate": round(stats["win_rate"], 1),
            "winning_sessions": stats["winning_sessions"],
            "losing_sessions": stats["losing_sessions"],
            "biggest_win": round(stats["biggest_win"], 2),
            "biggest_loss": round(stats["biggest_loss"], 2),
            "average_session": round(stats["average_session"], 2),
            "by_stake": stats["by_stake"],
            "by_location": stats["by_location"],
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting session stats: {str(e)}"}


@tool
def get_bankroll_analysis(
    current_bankroll: float,
    stake_big_blind: float,
) -> dict[str, Any]:
    """
    Analyze bankroll health and get recommendations for stake selection.

    Args:
        current_bankroll: Your current total bankroll in dollars
        stake_big_blind: The big blind of the stake you're playing or considering
            (e.g., 2 for 1/2 game, 5 for 2/5 game, 0.10 for NL10 online)

    Returns:
        Dictionary containing:
        - buyins_available: Number of 100bb buyins in your bankroll
        - risk_of_ruin: Estimated risk of going broke percentage
        - recommended_stakes: List of stakes your bankroll can support
        - health_status: Overall health (excellent, good, caution, critical)
        - win_rate: Historical win rate percentage (if data available)
        - variance: Session-to-session variance
        - std_deviation: Standard deviation of results
        - recommendations: List of actionable recommendations

    Example:
        get_bankroll_analysis(5000, 2) -> {"buyins_available": 25, "health_status": "good", "recommendations": [...]}
    """
    try:
        # Get recent sessions for analysis
        sessions = get_poker_sessions(user_id=1, days=90)

        health = analyze_bankroll_health(
            current_bankroll=current_bankroll,
            stake_big_blind=stake_big_blind,
            sessions=sessions,
        )

        return {
            "success": True,
            "current_bankroll": current_bankroll,
            "stake_big_blind": stake_big_blind,
            "buyins_available": round(health["buyins_available"], 1),
            "risk_of_ruin": round(health["risk_of_ruin"], 1),
            "recommended_stakes": health["recommended_stakes"],
            "health_status": health["health_status"],
            "win_rate": health.get("win_rate"),
            "variance": round(health.get("variance", 0), 2),
            "std_deviation": round(health.get("std_deviation", 0), 2),
            "recommendations": health["recommendations"],
        }
    except Exception as e:
        return {"success": False, "error": f"Error analyzing bankroll: {str(e)}"}


@tool
def get_session_history(
    days: int = 30,
    stake_level: Optional[str] = None,
    game_type: Optional[str] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Get recent poker session history.

    Args:
        days: Number of days to look back (0 for all time, default 30)
        stake_level: Filter by stake level (optional, e.g., "1/2", "2/5")
        game_type: Filter by game type (optional, "cash" or "tournament")
        limit: Maximum number of sessions to return (default 20)

    Returns:
        Dictionary containing:
        - sessions: List of sessions, each with:
            - date: Session date
            - stake_level: Stakes played
            - buy_in: Total buy-in amount
            - cash_out: Total cash-out amount
            - profit_loss: Net result
            - duration_minutes: Session length
            - hourly_rate: Dollars per hour
            - location: Where played
            - notes: Any session notes

    Example:
        get_session_history(days=7, stake_level="1/2") -> {"sessions": [{"date": "2024-01-15", "profit_loss": 250.0, ...}]}
    """
    try:
        sessions = get_poker_sessions(
            user_id=1,
            days=days,
            stake_level=stake_level,
            game_type=game_type,
            limit=limit,
        )

        return {
            "success": True,
            "count": len(sessions),
            "filters": {
                "days": days if days > 0 else "all_time",
                "stake_level": stake_level,
                "game_type": game_type,
            },
            "sessions": sessions,
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting sessions: {str(e)}"}


@tool
def get_bankroll_progression(days: int = 90) -> dict[str, Any]:
    """
    Get bankroll progression data showing profit/loss over time.

    Args:
        days: Number of days to look back (0 for all time, default 90)

    Returns:
        Dictionary containing:
        - data_points: List of data points with date and cumulative profit
        - current_bankroll: Current cumulative profit/loss
        - peak: Highest point reached
        - trough: Lowest point reached
        - max_drawdown: Maximum drawdown from peak
        - max_drawdown_pct: Maximum drawdown as percentage
        - streak_info: Current and longest winning/losing streaks

    Example:
        get_bankroll_progression(days=30) -> {"current_bankroll": 1200.0, "peak": 1500.0, "max_drawdown": 300.0, ...}
    """
    try:
        bankroll_data = get_bankroll_data(user_id=1, days=days)

        if not bankroll_data["data_points"]:
            return {
                "success": True,
                "message": "No session data found for the specified period",
                "data_points": [],
                "current_bankroll": 0,
            }

        # Calculate max drawdown
        cumulative = [dp["cumulative"] for dp in bankroll_data["data_points"]]
        drawdown = calculate_max_drawdown(cumulative)

        # Calculate streaks
        profits = [dp["profit"] for dp in bankroll_data["data_points"]]
        streaks = calculate_streak_info(profits)

        return {
            "success": True,
            "period_days": days if days > 0 else "all_time",
            "num_sessions": len(bankroll_data["data_points"]),
            "current_bankroll": round(bankroll_data["current_bankroll"], 2),
            "peak": round(bankroll_data["peak"], 2),
            "trough": round(bankroll_data["trough"], 2),
            "max_drawdown": round(drawdown["max_drawdown"], 2),
            "max_drawdown_pct": round(drawdown["max_drawdown_pct"], 1),
            "streak_info": streaks,
            "data_points": bankroll_data["data_points"][-10:],  # Last 10 for brevity
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting bankroll data: {str(e)}"}


# Export all tools
SESSION_TOOLS = [
    get_session_statistics,
    get_bankroll_analysis,
    get_session_history,
    get_bankroll_progression,
]
