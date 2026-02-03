# Tools Module Documentation

## Overview

The tools module (`src/tools/`) provides LangChain-compatible tools that enable the AI agent to interact with all application features. These tools wrap core logic and database services to provide a clean API for the AI coaching agent.

---

## Module Structure

```
src/tools/
├── __init__.py           # Module exports & ALL_TOOLS aggregation
├── hand_eval_tools.py    # Hand evaluation tools (Mode 1)
├── range_tools.py        # GTO range tools (Mode 2)
├── quiz_tools.py         # Quiz statistics tools (Mode 3)
├── session_tools.py      # Session tracking tools (Mode 4)
└── history_tools.py      # Hand history tools (Mode 5)
```

---

## LangChain Tool Architecture

All tools use the `@tool` decorator from LangChain to expose functions to the AI agent.

### Library Reference: LangChain Tools

**Documentation:** https://python.langchain.com/docs/concepts/tools

**Import:**
```python
from langchain_core.tools import tool
```

**Decorator Usage:**
```python
@tool
def my_tool(param: str) -> dict[str, Any]:
    """
    Tool description shown to the AI agent.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    # Implementation
    return {"result": "value"}
```

**Key Concepts:**
- The docstring becomes the tool's description for the AI
- Parameter types and descriptions inform the AI how to call the tool
- Return values should include a `success` field for error handling
- All tools return dictionaries (JSON-serializable)

---

## File: hand_eval_tools.py

### Purpose
Provides tools for hand strength evaluation, equity calculation, and comprehensive spot analysis.

### Dependencies
- `langchain_core.tools` - Tool decorator
- `..core.hand_evaluator` - HandEvaluator, EquityCalculator
- `..core.spot_analyzer` - SpotAnalyzer

---

### Tool: `evaluate_hand`

Evaluates the strength of a poker hand on a given board.

```python
@tool
def evaluate_hand(hero_hand: str, board: str) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hero_hand` | `str` | Two hole cards (e.g., "As Kh") |
| `board` | `str` | 3-5 community cards (e.g., "Qh Jh 2c") |

**Returns:**
```python
{
    "success": bool,
    "hand_class": str,      # e.g., "Flush", "Two Pair"
    "rank": int,            # Numeric rank (lower = better)
    "description": str,     # Human-readable description
}
# On error:
{
    "success": False,
    "error": str,
}
```

**Example AI Usage:**
```
User: "What hand do I have with Ac Kc on Qc Jc Tc?"
Agent calls: evaluate_hand("Ac Kc", "Qc Jc Tc")
Result: {"success": True, "hand_class": "Straight Flush", ...}
```

---

### Tool: `calculate_equity`

Calculates equity between two hands using Monte Carlo simulation.

```python
@tool
def calculate_equity(
    hero_hand: str,
    villain_hand: str,
    board: str = "",
    iterations: int = 10000,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hero_hand` | `str` | - | Your two hole cards |
| `villain_hand` | `str` | - | Opponent's two hole cards |
| `board` | `str` | `""` | Community cards (empty for preflop) |
| `iterations` | `int` | `10000` | Monte Carlo iterations |

**Returns:**
```python
{
    "success": bool,
    "hero_equity": float,      # Win probability (0-100)
    "villain_equity": float,
    "hero_wins": int,
    "villain_wins": int,
    "ties": int,
    "iterations": int,
}
```

**Example AI Usage:**
```
User: "What are my odds with pocket aces vs pocket kings preflop?"
Agent calls: calculate_equity("As Ad", "Kh Kd", "")
Result: {"hero_equity": 81.5, "villain_equity": 18.5, ...}
```

---

### Tool: `analyze_spot`

Performs comprehensive spot analysis including hand strength, equity, outs, pot odds, and recommendations.

```python
@tool
def analyze_spot(
    hero_hand: str,
    board: str,
    pot_size: Optional[float] = None,
    bet_to_call: Optional[float] = None,
    effective_stack: Optional[float] = None,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hero_hand` | `str` | - | Your two hole cards |
| `board` | `str` | - | Community cards (3-5) |
| `pot_size` | `Optional[float]` | `None` | Current pot size |
| `bet_to_call` | `Optional[float]` | `None` | Amount to call |
| `effective_stack` | `Optional[float]` | `None` | Remaining stack |

**Returns:**
```python
{
    "success": bool,
    "hand_strength": dict,     # Hand type and description
    "equity": float,           # Estimated win probability
    "equity_method": str,      # "outs_estimation" or "simulation"
    "out_count": int,          # Number of outs
    "outs": dict,              # Breakdown of outs by type
    "pot_odds": float | None,  # Required equity to call
    "implied_odds": float | None,
    "spr": float | None,       # Stack-to-pot ratio
    "spr_category": str | None,
    "ev": float | None,        # Expected value
    "recommendation": dict,    # Action and reasoning
}
```

**Recommendation Structure:**
```python
{
    "action": str,        # "CALL", "FOLD", or "ANALYZE"
    "reasoning": List[str],  # List of reasons
}
```

**Example AI Usage:**
```
User: "I have Ah Kh on Qh Jh 2c. Pot is $100, facing $50 bet. What should I do?"
Agent calls: analyze_spot("Ah Kh", "Qh Jh 2c", pot_size=100, bet_to_call=50)
Result: {"recommendation": {"action": "CALL", "reasoning": ["Flush draw with 9 outs", ...]}}
```

---

### Tool Exports

```python
HAND_EVAL_TOOLS = [evaluate_hand, calculate_equity, analyze_spot]
```

---

## File: range_tools.py

### Purpose
Provides tools for GTO preflop range lookup, range parsing, and hand-in-range checking.

### Dependencies
- `langchain_core.tools` - Tool decorator
- `..core.gto_charts` - GTOCharts
- `..core.range_parser` - RangeParser

---

### Tool: `get_gto_range`

Gets the GTO preflop range for a position and action.

```python
@tool
def get_gto_range(position: str, action: str = "open") -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `position` | `str` | - | Table position (UTG, MP, CO, BTN, SB, BB, etc.) |
| `action` | `str` | `"open"` | Action type (open, call_vs_BTN, 3bet_vs_BTN) |

**Returns:**
```python
{
    "success": bool,
    "position": str,
    "action": str,
    "hands": List[str],        # e.g., ["AA", "KK", "AKs", ...]
    "notation": str,           # Compact notation
    "total_combos": int,
    "percentage": float,       # Percentage of all hands
}
```

**Example AI Usage:**
```
User: "What hands should I open from the button?"
Agent calls: get_gto_range("BTN", "open")
Result: {"hands": ["AA", "KK", ...], "percentage": 40.0, ...}
```

---

### Tool: `list_available_ranges`

Lists all available GTO range positions and their actions.

```python
@tool
def list_available_ranges() -> dict[str, Any]:
```

**Returns:**
```python
{
    "success": bool,
    "positions": {
        "UTG": ["open"],
        "BTN": ["open"],
        "BB": ["call_vs_BTN", "3bet_vs_BTN"],
        # ...
    }
}
```

---

### Tool: `parse_range`

Parses poker range notation into individual hands and statistics.

```python
@tool
def parse_range(range_notation: str) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `range_notation` | `str` | Range string (e.g., "QQ+, AKs, ATs+") |

**Notation Syntax:**
- Single hands: `AA`, `AKs`, `AKo`
- Plus notation: `QQ+` (QQ and better), `ATs+` (ATs through AKs)
- Range notation: `QQ-88`, `A5s-A2s`
- Combinations: `"QQ+, AKs, ATs+, 98s"`

**Returns:**
```python
{
    "success": bool,
    "input_notation": str,
    "hands": List[str],        # Individual hands
    "combos": dict,            # By type (pairs, suited, offsuit)
    "total_combos": int,
    "percentage": float,       # Percentage of 1326 hands
}
```

**Example AI Usage:**
```
User: "How many combos is QQ+ and AK?"
Agent calls: parse_range("QQ+, AKs, AKo")
Result: {"total_combos": 34, "percentage": 2.6, ...}
```

---

### Tool: `check_hand_in_range`

Checks if a specific hand is in a GTO range.

```python
@tool
def check_hand_in_range(
    hand: str, position: str, action: str = "open"
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hand` | `str` | - | Hand to check (e.g., "AKs", "QQ") |
| `position` | `str` | - | Table position |
| `action` | `str` | `"open"` | Action type |

**Returns:**
```python
{
    "success": bool,
    "hand": str,
    "position": str,
    "action": str,
    "in_range": bool,          # Whether hand is in range
    "range_percentage": float,  # Total range percentage
}
```

**Example AI Usage:**
```
User: "Should I open A5s from UTG?"
Agent calls: check_hand_in_range("A5s", "UTG", "open")
Result: {"in_range": False, "range_percentage": 15.2, ...}
```

---

### Tool Exports

```python
RANGE_TOOLS = [get_gto_range, list_available_ranges, parse_range, check_hand_in_range]
```

---

## File: quiz_tools.py

### Purpose
Provides tools for quiz performance tracking, study leak identification, and question bank management.

### Dependencies
- `langchain_core.tools` - Tool decorator
- `..config` - QUIZ_BANK_FILE
- `..database.service` - Quiz database functions
- `..quiz.questions` - Question validation constants

---

### Tool: `get_quiz_performance`

Gets quiz performance statistics for the user.

```python
@tool
def get_quiz_performance(
    topic: Optional[str] = None,
    days: int = 30,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | `Optional[str]` | `None` | Filter by topic |
| `days` | `int` | `30` | Days to look back |

**Valid Topics:**
- `preflop`, `ranges`, `pot_odds`, `hand_strength`
- `position`, `postflop`, `game_theory`, `tournament`

**Returns:**
```python
{
    "success": bool,
    "period_days": int,
    "filtered_topic": str | None,
    "total_attempts": int,
    "correct": int,
    "percentage": float,
    "by_topic": dict,          # {topic: {attempts, correct, percentage}}
    "by_difficulty": dict,      # {difficulty: {attempts, correct, percentage}}
}
```

---

### Tool: `find_study_leaks`

Identifies weak areas based on quiz history.

```python
@tool
def find_study_leaks(
    min_attempts: int = 5,
    threshold: float = 60.0,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_attempts` | `int` | `5` | Minimum attempts to identify leak |
| `threshold` | `float` | `60.0` | Percentage below which is "weak" |

**Returns:**
```python
{
    "success": bool,
    "leaks": [
        {
            "topic": str,
            "attempts": int,
            "correct": int,
            "percentage": float,
            "recommendation": str,
        }
    ],
    "message": str,
}
```

**Example AI Usage:**
```
User: "What areas should I study?"
Agent calls: find_study_leaks()
Result: {"leaks": [{"topic": "pot_odds", "percentage": 45.0, ...}], ...}
```

---

### Tool: `get_recent_quiz_sessions`

Gets recent quiz session history.

```python
@tool
def get_recent_quiz_sessions(limit: int = 10) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `10` | Maximum sessions to return |

**Returns:**
```python
{
    "success": bool,
    "sessions": [
        {
            "topic": str,
            "difficulty": str,
            "score": int,
            "total": int,
            "percentage": float,
            "created_at": str,
        }
    ],
    "count": int,
}
```

---

### Tool: `add_quiz_question`

Adds a new question to the quiz bank.

```python
@tool
def add_quiz_question(
    topic: str,
    difficulty: str,
    question_type: str,
    question_text: str,
    options: list[str],
    answer: str,
    explanation: str,
    hero_hand: Optional[str] = None,
    position: Optional[str] = None,
    board: Optional[str] = None,
    action_to_hero: Optional[str] = None,
    stack_depth: Optional[str] = None,
    pot_size: Optional[str] = None,
    villain_action: Optional[str] = None,
) -> dict[str, Any]:
```

**Required Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | `str` | Question topic (see TOPICS) |
| `difficulty` | `str` | beginner/intermediate/advanced/elite |
| `question_type` | `str` | Question type (see QUESTION_TYPES) |
| `question_text` | `str` | The question text |
| `options` | `list[str]` | 2-4 answer options |
| `answer` | `str` | Correct answer (must be in options) |
| `explanation` | `str` | Why the answer is correct |

**Optional Scenario Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hero_hand` | `str` | Hero's hole cards |
| `position` | `str` | Hero's position |
| `board` | `str` | Board cards |
| `action_to_hero` | `str` | Action facing hero |
| `stack_depth` | `str` | Effective stack |
| `pot_size` | `str` | Current pot |
| `villain_action` | `str` | Villain's action |

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "question_id": str,
    "topic": str,
    "difficulty": str,
    "total_questions": int,
}
```

---

### Tool: `get_quiz_bank_stats`

Gets statistics about the quiz bank.

```python
@tool
def get_quiz_bank_stats() -> dict[str, Any]:
```

**Returns:**
```python
{
    "success": bool,
    "total_questions": int,
    "by_topic": dict,          # {topic: count}
    "by_difficulty": dict,      # {difficulty: count}
    "by_type": dict,            # {question_type: count}
    "coverage_gaps": List[str], # Areas with few questions
}
```

---

### Helper Functions (Internal)

```python
def _load_quiz_bank() -> dict[str, Any]:
    """Load quiz bank from JSON file."""

def _save_quiz_bank(data: dict[str, Any]) -> bool:
    """Save quiz bank to JSON file."""

def _generate_question_id(topic: str, questions: list) -> str:
    """Generate unique question ID (e.g., 'pf_001')."""
```

---

### Tool Exports

```python
QUIZ_TOOLS = [
    get_quiz_performance,
    find_study_leaks,
    get_recent_quiz_sessions,
    add_quiz_question,
    get_quiz_bank_stats,
]
```

---

## File: session_tools.py

### Purpose
Provides tools for poker session statistics, bankroll analysis, and session history.

### Dependencies
- `langchain_core.tools` - Tool decorator
- `..database.service` - Session database functions
- `..core.session_tracker` - Bankroll analysis functions

---

### Tool: `get_session_statistics`

Gets aggregated poker session statistics.

```python
@tool
def get_session_statistics(
    days: int = 30,
    stake_level: Optional[str] = None,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | `int` | `30` | Days to look back (0 = all time) |
| `stake_level` | `Optional[str]` | `None` | Filter by stake (e.g., "1/2") |

**Returns:**
```python
{
    "success": bool,
    "period_days": int | str,
    "stake_filter": str | None,
    "total_sessions": int,
    "total_profit": float,
    "total_hours": float,
    "hourly_rate": float,
    "win_rate": float,           # Percentage of winning sessions
    "winning_sessions": int,
    "losing_sessions": int,
    "biggest_win": float,
    "biggest_loss": float,
    "average_session": float,
    "by_stake": dict,
    "by_location": dict,
}
```

**Example AI Usage:**
```
User: "How am I doing this month at 1/2?"
Agent calls: get_session_statistics(days=30, stake_level="1/2")
Result: {"total_profit": 1500.0, "hourly_rate": 25.0, ...}
```

---

### Tool: `get_bankroll_analysis`

Analyzes bankroll health and provides stake recommendations.

```python
@tool
def get_bankroll_analysis(
    current_bankroll: float,
    stake_big_blind: float,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `current_bankroll` | `float` | Current bankroll in dollars |
| `stake_big_blind` | `float` | Big blind of stake (e.g., 2 for 1/2) |

**Returns:**
```python
{
    "success": bool,
    "current_bankroll": float,
    "stake_big_blind": float,
    "buyins_available": float,       # Number of 100bb buyins
    "risk_of_ruin": float,           # Percentage
    "recommended_stakes": List[str],
    "health_status": str,            # excellent/good/caution/critical
    "win_rate": float | None,
    "variance": float,
    "std_deviation": float,
    "recommendations": List[str],
}
```

**Example AI Usage:**
```
User: "I have $5000. Should I play 2/5?"
Agent calls: get_bankroll_analysis(5000, 5)
Result: {"buyins_available": 10, "health_status": "caution", ...}
```

---

### Tool: `get_session_history`

Gets recent poker session history.

```python
@tool
def get_session_history(
    days: int = 30,
    stake_level: Optional[str] = None,
    game_type: Optional[str] = None,
    limit: int = 20,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | `int` | `30` | Days to look back |
| `stake_level` | `Optional[str]` | `None` | Filter by stake |
| `game_type` | `Optional[str]` | `None` | "cash" or "tournament" |
| `limit` | `int` | `20` | Maximum sessions |

**Returns:**
```python
{
    "success": bool,
    "count": int,
    "filters": dict,
    "sessions": [
        {
            "date": str,
            "stake_level": str,
            "buy_in": float,
            "cash_out": float,
            "profit_loss": float,
            "duration_minutes": int,
            "hourly_rate": float,
            "location": str,
            "notes": str,
        }
    ],
}
```

---

### Tool: `get_bankroll_progression`

Gets bankroll progression data over time.

```python
@tool
def get_bankroll_progression(days: int = 90) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | `int` | `90` | Days to look back |

**Returns:**
```python
{
    "success": bool,
    "period_days": int | str,
    "num_sessions": int,
    "current_bankroll": float,
    "peak": float,
    "trough": float,
    "max_drawdown": float,
    "max_drawdown_pct": float,
    "streak_info": {
        "current_streak": int,      # Positive = winning, negative = losing
        "longest_win_streak": int,
        "longest_lose_streak": int,
    },
    "data_points": List[dict],      # Last 10 data points
}
```

---

### Tool Exports

```python
SESSION_TOOLS = [
    get_session_statistics,
    get_bankroll_analysis,
    get_session_history,
    get_bankroll_progression,
]
```

---

## File: history_tools.py

### Purpose
Provides tools for hand history search, statistics, and pattern analysis.

### Dependencies
- `langchain_core.tools` - Tool decorator
- `..database.service` - Hand history database functions
- `..core.hand_history` - Pattern analysis functions

---

### Tool: `search_hands`

Searches saved hand histories with filters.

```python
@tool
def search_hands(
    tags: Optional[List[str]] = None,
    days_back: int = 0,
    position: Optional[str] = None,
    result: Optional[str] = None,
    limit: int = 20,
) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tags` | `Optional[List[str]]` | `None` | Filter by tags |
| `days_back` | `int` | `0` | Days to look back (0 = all) |
| `position` | `Optional[str]` | `None` | Filter by position |
| `result` | `Optional[str]` | `None` | "won", "lost", or "split" |
| `limit` | `int` | `20` | Maximum hands |

**Common Tags:**
- `bluff`, `value`, `mistake`, `hero_call`
- `3bet`, `4bet`, `c-bet`, `check-raise`
- `slow_play`, `squeeze`, `float`, `overbet`
- `cooler`, `bad_beat`, `river_bluff`

**Returns:**
```python
{
    "success": bool,
    "count": int,
    "filters": dict,
    "hands": [
        {
            "hero_hand": str,
            "board": str,
            "position": str,
            "action_summary": str,
            "result": str,
            "tags": List[str],
            "notes": str,
            "pot_size": float,
            "created_at": str,
        }
    ],
}
```

---

### Tool: `get_hand_statistics`

Gets aggregated hand history statistics.

```python
@tool
def get_hand_statistics(days: int = 30) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | `int` | `30` | Days to look back (0 = all) |

**Returns:**
```python
{
    "success": bool,
    "period_days": int | str,
    "total_hands": int,
    "wins": int,
    "losses": int,
    "splits": int,
    "win_rate": float,
    "by_position": dict,       # {position: {total, won}}
    "by_tag": dict,            # {tag: {total, won}}
    "common_tags": List[str],
}
```

---

### Tool: `analyze_patterns`

Analyzes patterns and identifies leaks in hand history.

```python
@tool
def analyze_patterns(days: int = 30) -> dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | `int` | `30` | Days to look back |

**Returns:**
```python
{
    "success": bool,
    "period_days": int | str,
    "total_hands": int,
    "overall_win_rate": float,
    "position_win_rates": dict,    # {position: win_rate}
    "tag_win_rates": dict,         # {tag: win_rate}
    "bluff_success_rate": float,
    "value_bet_win_rate": float,
    "street_distribution": dict,   # {street: percentage}
    "insights": List[str],         # Actionable recommendations
}
```

**Example Insights:**
```python
[
    "Best position: BTN (65% win rate)",
    "Low bluff success (35%). Consider tightening.",
    "Strong in 3bet pots (72% win rate)",
]
```

---

### Tool: `list_available_tags`

Lists available tags for categorizing hands.

```python
@tool
def list_available_tags() -> dict[str, Any]:
```

**Returns:**
```python
{
    "success": bool,
    "common_tags": List[str],
    "positions": List[str],
    "tag_descriptions": {
        "bluff": "Made a bluff (bet/raise without best hand)",
        "value": "Made a value bet for thin value",
        "mistake": "Hand you played incorrectly",
        # ...
    },
}
```

---

### Tool Exports

```python
HISTORY_TOOLS = [
    search_hands,
    get_hand_statistics,
    analyze_patterns,
    list_available_tags,
]
```

---

## File: __init__.py

### Purpose
Module initialization that aggregates all tools into a single `ALL_TOOLS` list.

### Exports

```python
# All tools combined for the agent
ALL_TOOLS = HAND_EVAL_TOOLS + RANGE_TOOLS + QUIZ_TOOLS + SESSION_TOOLS + HISTORY_TOOLS

__all__ = [
    # Hand evaluation tools (3)
    "evaluate_hand",
    "calculate_equity",
    "analyze_spot",
    "HAND_EVAL_TOOLS",

    # Range tools (4)
    "get_gto_range",
    "list_available_ranges",
    "parse_range",
    "check_hand_in_range",
    "RANGE_TOOLS",

    # Quiz tools (5)
    "get_quiz_performance",
    "find_study_leaks",
    "get_recent_quiz_sessions",
    "add_quiz_question",
    "get_quiz_bank_stats",
    "QUIZ_TOOLS",

    # Session tools (4)
    "get_session_statistics",
    "get_bankroll_analysis",
    "get_session_history",
    "get_bankroll_progression",
    "SESSION_TOOLS",

    # History tools (4)
    "search_hands",
    "get_hand_statistics",
    "analyze_patterns",
    "list_available_tags",
    "HISTORY_TOOLS",

    # All tools
    "ALL_TOOLS",  # 17 tools total
]
```

### Usage

```python
# Import all tools for agent
from src.tools import ALL_TOOLS

# Import specific tool groups
from src.tools import HAND_EVAL_TOOLS, RANGE_TOOLS

# Import individual tools
from src.tools import evaluate_hand, calculate_equity
```

---

## Tool Count Summary

| Category | Tools | Purpose |
|----------|-------|---------|
| Hand Eval | 3 | Hand strength, equity, spot analysis |
| Range | 4 | GTO ranges, parsing, hand checking |
| Quiz | 5 | Performance, leaks, question bank |
| Session | 4 | Statistics, bankroll, history |
| History | 4 | Search, stats, pattern analysis |
| **Total** | **17** | All agent capabilities |

---

## Error Handling Pattern

All tools follow a consistent error handling pattern:

```python
@tool
def example_tool(param: str) -> dict[str, Any]:
    try:
        # ... implementation ...
        return {
            "success": True,
            # ... result data ...
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

The AI agent should check the `success` field before using results.

---

## Integration with Agent

Tools are bound to the agent in `src/agent/coach.py`:

```python
from src.tools import ALL_TOOLS

# Create agent with tools
agent = create_react_agent(llm, ALL_TOOLS)
```

The agent can then call any tool based on user queries, with the docstrings providing context for when and how to use each tool.
