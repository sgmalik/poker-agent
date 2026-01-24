"""Quiz question types, validation, and formatting utilities."""

from typing import Any, Dict, List, Set

# Valid topics for quiz questions
TOPICS: List[str] = [
    "preflop",
    "ranges",
    "pot_odds",
    "hand_strength",
    "position",
    "postflop",
    "game_theory",
    "tournament",
]

# Valid difficulty levels
DIFFICULTIES: List[str] = [
    "beginner",
    "intermediate",
    "advanced",
    "elite",
]

# Valid question types
QUESTION_TYPES: List[str] = [
    "preflop_action",
    "range_check",
    "hand_strength",
    "pot_odds",
    "position_open",
    "postflop_action",
    "board_texture_analysis",
    "blocker_logic",
    "sizing_strategy",
    "icm_logic",
    "range_interaction",
    "4bet_theory",
    "equity_realization",
    "mixed_strategies",
    "node_locking",
    "geometric_sizing",
    "uncapped_ranges",
    "protection_betting",
    "indifference_principle",
    "multiway_dynamics",
    "range_merging",
    "solver_logic",
    "postflop_theory",
    "advanced_icm",
    "range_construction",
]

# Required fields for a valid question
REQUIRED_FIELDS: Set[str] = {
    "id",
    "type",
    "difficulty",
    "topic",
    "question",
    "options",
    "answer",
    "explanation",
}


def validate_question(question: Dict[str, Any]) -> bool:
    """
    Validate that a question has all required fields and valid values.

    Args:
        question: Question dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    # Check all required fields exist
    if not all(field in question for field in REQUIRED_FIELDS):
        return False

    # Validate topic
    if question.get("topic") not in TOPICS:
        return False

    # Validate difficulty
    if question.get("difficulty") not in DIFFICULTIES:
        return False

    # Validate type
    if question.get("type") not in QUESTION_TYPES:
        return False

    # Validate options is a non-empty list
    options = question.get("options", [])
    if not isinstance(options, list) or len(options) < 2:
        return False

    # Validate answer is in options
    answer = question.get("answer", "")
    if answer not in options:
        return False

    # Validate id is a non-empty string
    if not question.get("id") or not isinstance(question.get("id"), str):
        return False

    return True


def check_answer(question: Dict[str, Any], user_answer: str) -> bool:
    """
    Check if the user's answer is correct.

    Args:
        question: Question dictionary
        user_answer: User's submitted answer

    Returns:
        True if answer is correct, False otherwise
    """
    correct = question.get("answer", "")
    return user_answer.strip().lower() == correct.strip().lower()


def format_question_display(question: Dict[str, Any]) -> str:
    """
    Format a question for TUI display with rich markup.

    Args:
        question: Question dictionary

    Returns:
        Formatted string with rich markup
    """
    # Convert card notation for display
    q_text = _format_cards(question.get("question", ""))

    lines = [
        f"[bold]{q_text}[/bold]",
        "",
    ]

    # Add scenario details if present
    scenario = question.get("scenario", {})
    if scenario:
        hero_hand = scenario.get("hero_hand")
        if hero_hand:
            lines.append(f"Hand: [cyan]{_format_cards(hero_hand)}[/cyan]")

        position = scenario.get("position")
        if position:
            lines.append(f"Position: [yellow]{position}[/yellow]")

        board = scenario.get("board")
        if board:
            lines.append(f"Board: [green]{_format_cards(board)}[/green]")

        lines.append("")

    return "\n".join(lines)


def format_options(options: List[str]) -> List[str]:
    """
    Format options for display with letter labels.

    Args:
        options: List of option strings

    Returns:
        List of formatted option strings (e.g., ["A) Fold", "B) Call"])
    """
    labels = "ABCDEFGHIJ"
    return [f"{labels[i]}) {opt}" for i, opt in enumerate(options)]


def get_option_from_label(options: List[str], label: str) -> str:
    """
    Get the option text from a label (A, B, C, etc.).

    Args:
        options: List of option strings
        label: Single character label (A-J)

    Returns:
        Option text or empty string if invalid label
    """
    labels = "ABCDEFGHIJ"
    label = label.upper()
    if label in labels:
        idx = labels.index(label)
        if idx < len(options):
            return options[idx]
    return ""


def _format_cards(text: str) -> str:
    """
    Convert card notation to Unicode suits.

    Args:
        text: Text containing card notation (e.g., "As Kh")

    Returns:
        Text with Unicode suit symbols
    """
    import re

    # Replace suit letters with symbols
    replacements = [
        ("s", "\u2660"),  # Spades
        ("h", "\u2665"),  # Hearts
        ("d", "\u2666"),  # Diamonds
        ("c", "\u2663"),  # Clubs
    ]

    result = text
    for letter, symbol in replacements:
        # Match rank followed by suit letter, requiring space/boundary before rank
        # This prevents "with" -> "wit♥" and "76s" -> "76♠"
        result = re.sub(
            rf"(?<![a-zA-Z0-9])([AKQJT2-9])({letter})\b",
            rf"\1{symbol}",
            result,
            flags=re.IGNORECASE,
        )

    return result


def get_topics() -> List[str]:
    """Get list of available quiz topics."""
    return TOPICS.copy()


def get_difficulties() -> List[str]:
    """Get list of available difficulty levels."""
    return DIFFICULTIES.copy()


def filter_questions(
    questions: List[Dict[str, Any]],
    topic: str | None = None,
    difficulty: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Filter questions by topic and/or difficulty.

    Args:
        questions: List of question dictionaries
        topic: Topic to filter by (None for all)
        difficulty: Difficulty to filter by (None for all)

    Returns:
        Filtered list of questions
    """
    result = questions

    if topic and topic.lower() != "all":
        result = [q for q in result if q.get("topic") == topic]

    if difficulty and difficulty.lower() != "all":
        result = [q for q in result if q.get("difficulty") == difficulty]

    return result
