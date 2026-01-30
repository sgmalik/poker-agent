"""LangChain tools for hand history search and analysis (Mode 5)."""

from typing import Any, List, Optional

from langchain_core.tools import tool

from ..database.service import (
    get_hand_histories,
    get_hand_history_stats,
)
from ..core.hand_history import (
    analyze_hand_patterns,
    COMMON_TAGS,
    POSITIONS,
)


@tool
def search_hands(
    tags: Optional[List[str]] = None,
    days_back: int = 0,
    position: Optional[str] = None,
    result: Optional[str] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Search saved hand histories with filters.

    Args:
        tags: Filter by tags (optional). Common tags include:
            bluff, value, mistake, hero_call, 3bet, 4bet, c-bet, check-raise,
            slow_play, squeeze, float, overbet, cooler, bad_beat, river_bluff
        days_back: Number of days to look back (0 for all time, default 0)
        position: Filter by position (optional): UTG, MP, CO, BTN, SB, BB, etc.
        result: Filter by result (optional): "won", "lost", or "split"
        limit: Maximum number of hands to return (default 20)

    Returns:
        Dictionary containing:
        - count: Number of hands found
        - hands: List of hand records, each with:
            - hero_hand: Your hole cards
            - board: Community cards
            - position: Your position
            - action_summary: Description of the action
            - result: Won, lost, or split
            - tags: Tags applied to the hand
            - notes: Any notes
            - pot_size: Final pot size
            - created_at: When the hand was recorded

    Example:
        search_hands(tags=["bluff"], result="won") -> {"count": 5, "hands": [...]}
    """
    try:
        hands = get_hand_histories(
            user_id=1,
            days=days_back,
            tags=tags,
            result=result,
            position=position.upper() if position else None,
            limit=limit,
        )

        return {
            "success": True,
            "count": len(hands),
            "filters": {
                "tags": tags,
                "days_back": days_back if days_back > 0 else "all_time",
                "position": position,
                "result": result,
            },
            "hands": hands,
        }
    except Exception as e:
        return {"success": False, "error": f"Error searching hands: {str(e)}"}


@tool
def get_hand_statistics(days: int = 30) -> dict[str, Any]:
    """
    Get aggregated statistics from hand history.

    Args:
        days: Number of days to look back (0 for all time, default 30)

    Returns:
        Dictionary containing:
        - total_hands: Total hands recorded
        - wins: Number of winning hands
        - losses: Number of losing hands
        - splits: Number of split pots
        - win_rate: Overall win percentage
        - by_position: Win rates broken down by position
        - by_tag: Win rates broken down by tag
        - common_tags: Most frequently used tags

    Example:
        get_hand_statistics(days=90) -> {"total_hands": 150, "win_rate": 58.0, "by_position": {"BTN": {"total": 30, "won": 20}}, ...}
    """
    try:
        stats = get_hand_history_stats(user_id=1, days=days)

        return {
            "success": True,
            "period_days": days if days > 0 else "all_time",
            "total_hands": stats["total_hands"],
            "wins": stats["wins"],
            "losses": stats["losses"],
            "splits": stats["splits"],
            "win_rate": round(stats["win_rate"], 1),
            "by_position": stats["by_position"],
            "by_tag": stats["by_tag"],
            "common_tags": stats["common_tags"],
        }
    except Exception as e:
        return {"success": False, "error": f"Error getting hand stats: {str(e)}"}


@tool
def analyze_patterns(days: int = 30) -> dict[str, Any]:
    """
    Analyze patterns and identify leaks in your hand history.

    This tool performs deep analysis on your recorded hands to find:
    - Your strongest and weakest positions
    - Bluff success rates
    - Value betting effectiveness
    - Areas needing improvement

    Args:
        days: Number of days to look back (0 for all time, default 30)

    Returns:
        Dictionary containing:
        - total_hands: Number of hands analyzed
        - overall_win_rate: Overall win percentage
        - position_win_rates: Win rate by position
        - tag_win_rates: Win rate by hand type/tag
        - bluff_success_rate: How often bluffs succeed
        - value_bet_win_rate: How often value bets win
        - street_distribution: Where hands end (flop/turn/river)
        - insights: List of actionable insights and recommendations

    Example:
        analyze_patterns(days=60) -> {"insights": ["Best position: BTN (65% win rate)", "Low bluff success (35%). Consider tightening."], ...}
    """
    try:
        # Get hands for analysis
        hands = get_hand_histories(user_id=1, days=days, limit=1000)

        if not hands:
            return {
                "success": True,
                "message": "No hands found for the specified period. Start logging hands to get pattern analysis!",
                "total_hands": 0,
                "insights": [],
            }

        analysis = analyze_hand_patterns(hands)

        return {
            "success": True,
            "period_days": days if days > 0 else "all_time",
            "total_hands": analysis["total_hands"],
            "overall_win_rate": round(analysis["overall_win_rate"], 1),
            "position_win_rates": {
                k: round(v, 1) for k, v in analysis["position_win_rates"].items()
            },
            "tag_win_rates": {
                k: round(v, 1) for k, v in analysis["tag_win_rates"].items()
            },
            "bluff_success_rate": round(analysis["bluff_success_rate"], 1),
            "value_bet_win_rate": round(analysis["value_bet_win_rate"], 1),
            "street_distribution": {
                k: round(v, 1) for k, v in analysis["street_distribution"].items()
            },
            "insights": analysis["insights"],
        }
    except Exception as e:
        return {"success": False, "error": f"Error analyzing patterns: {str(e)}"}


@tool
def list_available_tags() -> dict[str, Any]:
    """
    List all available tags for categorizing hands.

    Returns:
        Dictionary containing:
        - common_tags: List of predefined common tags
        - positions: List of valid table positions

    Example:
        list_available_tags() -> {"common_tags": ["bluff", "value", "mistake", ...], "positions": ["UTG", "MP", ...]}
    """
    return {
        "success": True,
        "common_tags": COMMON_TAGS,
        "positions": POSITIONS,
        "tag_descriptions": {
            "bluff": "Made a bluff (bet/raise without best hand)",
            "value": "Made a value bet for thin value",
            "mistake": "Hand you played incorrectly",
            "hero_call": "Made a difficult call that required reading opponent",
            "3bet": "Made or faced a 3-bet preflop",
            "4bet": "Made or faced a 4-bet preflop",
            "c-bet": "Made or faced a continuation bet",
            "check-raise": "Made or faced a check-raise",
            "slow_play": "Slow played a strong hand",
            "squeeze": "Made a squeeze play preflop",
            "cooler": "Lost with a very strong hand to a stronger hand",
            "bad_beat": "Lost in an unlikely way statistically",
        },
    }


# Export all tools
HISTORY_TOOLS = [
    search_hands,
    get_hand_statistics,
    analyze_patterns,
    list_available_tags,
]
