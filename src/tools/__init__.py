"""LangChain tools for the Poker Coach AI Agent.

This module exports all available tools that the AI agent can use to help users
with poker analysis, range queries, quiz statistics, session tracking, and
hand history analysis.
"""

from .hand_eval_tools import (
    evaluate_hand,
    calculate_equity,
    analyze_spot,
    HAND_EVAL_TOOLS,
)
from .range_tools import (
    get_gto_range,
    list_available_ranges,
    parse_range,
    check_hand_in_range,
    RANGE_TOOLS,
)
from .quiz_tools import (
    get_quiz_performance,
    find_study_leaks,
    get_recent_quiz_sessions,
    QUIZ_TOOLS,
)
from .session_tools import (
    get_session_statistics,
    get_bankroll_analysis,
    get_session_history,
    get_bankroll_progression,
    SESSION_TOOLS,
)
from .history_tools import (
    search_hands,
    get_hand_statistics,
    analyze_patterns,
    list_available_tags,
    HISTORY_TOOLS,
)

# All tools combined for the agent
ALL_TOOLS = HAND_EVAL_TOOLS + RANGE_TOOLS + QUIZ_TOOLS + SESSION_TOOLS + HISTORY_TOOLS

__all__ = [
    # Hand evaluation tools
    "evaluate_hand",
    "calculate_equity",
    "analyze_spot",
    "HAND_EVAL_TOOLS",
    # Range tools
    "get_gto_range",
    "list_available_ranges",
    "parse_range",
    "check_hand_in_range",
    "RANGE_TOOLS",
    # Quiz tools
    "get_quiz_performance",
    "find_study_leaks",
    "get_recent_quiz_sessions",
    "QUIZ_TOOLS",
    # Session tools
    "get_session_statistics",
    "get_bankroll_analysis",
    "get_session_history",
    "get_bankroll_progression",
    "SESSION_TOOLS",
    # History tools
    "search_hands",
    "get_hand_statistics",
    "analyze_patterns",
    "list_available_tags",
    "HISTORY_TOOLS",
    # All tools
    "ALL_TOOLS",
]
