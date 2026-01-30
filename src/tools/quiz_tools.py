"""LangChain tools for quiz statistics and study analysis (Mode 3)."""

import json
from typing import Any, Optional

from langchain_core.tools import tool

from ..config import QUIZ_BANK_FILE
from ..database.service import get_quiz_stats, identify_study_leaks, get_recent_sessions
from ..quiz.questions import (
    TOPICS,
    DIFFICULTIES,
    QUESTION_TYPES,
    validate_question,
)


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


def _load_quiz_bank() -> dict[str, Any]:
    """Load the quiz bank from JSON file."""
    if QUIZ_BANK_FILE.exists():
        with open(QUIZ_BANK_FILE, "r") as f:
            return json.load(f)
    return {
        "version": "1.0",
        "description": "Poker quiz question bank",
        "questions": [],
    }


def _save_quiz_bank(data: dict[str, Any]) -> bool:
    """Save the quiz bank to JSON file."""
    try:
        with open(QUIZ_BANK_FILE, "w") as f:
            json.dump(data, f, indent="\t")
        return True
    except Exception:
        return False


def _generate_question_id(topic: str, questions: list) -> str:
    """Generate a unique question ID based on topic."""
    prefix_map = {
        "preflop": "pf",
        "ranges": "rng",
        "pot_odds": "po",
        "hand_strength": "hs",
        "position": "pos",
        "postflop": "post",
        "game_theory": "gt",
        "tournament": "trn",
    }
    prefix = prefix_map.get(topic, "q")

    # Find highest existing number for this prefix
    existing_nums = []
    for q in questions:
        qid = q.get("id", "")
        if qid.startswith(prefix + "_"):
            try:
                num = int(qid.split("_")[1])
                existing_nums.append(num)
            except (IndexError, ValueError):
                pass

    next_num = max(existing_nums, default=0) + 1
    return f"{prefix}_{next_num:03d}"


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
    """
    Add a new quiz question to the question bank.

    Use this tool to create new quiz questions to expand the quiz bank.
    Questions should be educational, have clear correct answers, and include
    helpful explanations.

    Args:
        topic: Question topic. Must be one of:
            - preflop: Preflop decision making
            - ranges: Range understanding and construction
            - pot_odds: Pot odds and implied odds calculations
            - hand_strength: Hand strength evaluation
            - position: Positional play concepts
            - postflop: Postflop strategy
            - game_theory: GTO and game theory concepts
            - tournament: Tournament-specific concepts (ICM, bubble, etc.)

        difficulty: Question difficulty. Must be one of:
            - beginner: Basic concepts, straightforward decisions
            - intermediate: More nuanced situations
            - advanced: Complex scenarios requiring deep understanding
            - elite: Expert-level solver concepts

        question_type: Type of question. Common types include:
            - preflop_action: What action to take preflop
            - range_check: Is a hand in a certain range
            - hand_strength: Evaluate hand strength
            - pot_odds: Calculate pot odds
            - position_open: Opening range decisions
            - postflop_action: Postflop betting decisions
            - board_texture_analysis: Analyzing board textures
            - blocker_logic: Blocker-based decisions
            - sizing_strategy: Bet sizing decisions
            - icm_logic: ICM considerations
            - equity_realization: Equity realization concepts

        question_text: The question to ask the user

        options: List of 2-4 answer options (one must be the correct answer)

        answer: The correct answer (must exactly match one of the options)

        explanation: Detailed explanation of why the answer is correct.
            Should be educational and help users understand the concept.

        hero_hand: Hero's hand in card notation (e.g., "As Kh")
        position: Hero's position (e.g., "BTN", "UTG", "BB")
        board: Board cards if applicable (e.g., "Ah Kd 7c")
        action_to_hero: Action facing hero (e.g., "raise_3bb", "check")
        stack_depth: Effective stack depth (e.g., "100bb", "25bb")
        pot_size: Current pot size (e.g., "10bb", "$50")
        villain_action: Villain's action description

    Returns:
        Dictionary with success status and the new question ID if successful

    Example:
        add_quiz_question(
            topic="pot_odds",
            difficulty="beginner",
            question_type="pot_odds",
            question_text="The pot is $100 and you need to call $25. What are your pot odds?",
            options=["3:1", "4:1", "5:1", "2:1"],
            answer="4:1",
            explanation="Pot odds = pot / call amount = $100 / $25 = 4:1. You need 20% equity to break even."
        )
    """
    try:
        # Validate topic
        if topic not in TOPICS:
            return {
                "success": False,
                "error": f"Invalid topic '{topic}'. Must be one of: {', '.join(TOPICS)}",
            }

        # Validate difficulty
        if difficulty not in DIFFICULTIES:
            return {
                "success": False,
                "error": f"Invalid difficulty '{difficulty}'. Must be one of: {', '.join(DIFFICULTIES)}",
            }

        # Validate question type
        if question_type not in QUESTION_TYPES:
            return {
                "success": False,
                "error": f"Invalid question_type '{question_type}'. Must be one of: {', '.join(QUESTION_TYPES)}",
            }

        # Validate options
        if not isinstance(options, list) or len(options) < 2 or len(options) > 4:
            return {
                "success": False,
                "error": "Options must be a list of 2-4 choices",
            }

        # Validate answer is in options
        if answer not in options:
            return {
                "success": False,
                "error": f"Answer '{answer}' must be one of the options: {options}",
            }

        # Load existing quiz bank
        quiz_bank = _load_quiz_bank()
        questions = quiz_bank.get("questions", [])

        # Generate unique ID
        question_id = _generate_question_id(topic, questions)

        # Build scenario dict if any scenario fields provided
        scenario = {}
        if hero_hand:
            scenario["hero_hand"] = hero_hand
        if position:
            scenario["position"] = position
        if board:
            scenario["board"] = board
        if action_to_hero:
            scenario["action_to_hero"] = action_to_hero
        if stack_depth:
            scenario["stack_depth"] = stack_depth
        if pot_size:
            scenario["pot_size"] = pot_size
        if villain_action:
            scenario["villain_action"] = villain_action

        # Create the question
        new_question: dict[str, Any] = {
            "id": question_id,
            "type": question_type,
            "difficulty": difficulty,
            "topic": topic,
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": explanation,
        }

        if scenario:
            new_question["scenario"] = scenario

        # Validate the question
        if not validate_question(new_question):
            return {
                "success": False,
                "error": "Question validation failed. Check all required fields.",
            }

        # Add to quiz bank
        questions.append(new_question)
        quiz_bank["questions"] = questions

        # Save
        if _save_quiz_bank(quiz_bank):
            return {
                "success": True,
                "message": "Question added successfully",
                "question_id": question_id,
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": len(questions),
            }
        else:
            return {
                "success": False,
                "error": "Failed to save quiz bank file",
            }

    except Exception as e:
        return {"success": False, "error": f"Error adding question: {str(e)}"}


@tool
def get_quiz_bank_stats() -> dict[str, Any]:
    """
    Get statistics about the current quiz bank.

    Use this to understand the current coverage of questions across
    topics and difficulty levels before adding new questions.

    Returns:
        Dictionary containing:
        - total_questions: Total number of questions
        - by_topic: Count of questions per topic
        - by_difficulty: Count of questions per difficulty
        - by_type: Count of questions per question type
        - coverage_gaps: Topics/difficulties with fewer questions

    Example:
        get_quiz_bank_stats() -> {"total_questions": 80, "by_topic": {"preflop": 15, ...}, ...}
    """
    try:
        quiz_bank = _load_quiz_bank()
        questions = quiz_bank.get("questions", [])

        # Count by topic
        by_topic = {t: 0 for t in TOPICS}
        for q in questions:
            topic = q.get("topic")
            if topic in by_topic:
                by_topic[topic] += 1

        # Count by difficulty
        by_difficulty = {d: 0 for d in DIFFICULTIES}
        for q in questions:
            diff = q.get("difficulty")
            if diff in by_difficulty:
                by_difficulty[diff] += 1

        # Count by type
        by_type: dict[str, int] = {}
        for q in questions:
            qtype = q.get("type", "unknown")
            by_type[qtype] = by_type.get(qtype, 0) + 1

        # Identify coverage gaps (topics or difficulties with < 5 questions)
        coverage_gaps = []
        for topic, count in by_topic.items():
            if count < 10:
                coverage_gaps.append(f"{topic}: only {count} questions")
        for diff, count in by_difficulty.items():
            if count < 15:
                coverage_gaps.append(f"{diff} difficulty: only {count} questions")

        return {
            "success": True,
            "total_questions": len(questions),
            "by_topic": by_topic,
            "by_difficulty": by_difficulty,
            "by_type": by_type,
            "coverage_gaps": coverage_gaps,
        }

    except Exception as e:
        return {"success": False, "error": f"Error getting stats: {str(e)}"}


# Export all tools
QUIZ_TOOLS = [
    get_quiz_performance,
    find_study_leaks,
    get_recent_quiz_sessions,
    add_quiz_question,
    get_quiz_bank_stats,
]
