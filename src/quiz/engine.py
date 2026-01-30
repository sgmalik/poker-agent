"""Interactive poker quiz engine."""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .questions import (
    check_answer,
    filter_questions,
    validate_question,
)
from ..config import QUIZ_BANK_FILE


class QuizEngine:
    """
    Interactive poker quiz engine.

    Manages quiz sessions including question loading, filtering,
    answer submission, progress tracking, and results.
    """

    def __init__(self, bank_file: Optional[Path] = None) -> None:
        """
        Initialize the quiz engine.

        Args:
            bank_file: Path to quiz bank JSON file (uses default if None)
        """
        self._bank_file = bank_file or QUIZ_BANK_FILE
        self._all_questions: List[Dict[str, Any]] = []
        self._questions: List[Dict[str, Any]] = []
        self._current_idx: int = 0
        self._answers: List[Dict[str, Any]] = []
        self._start_time: Optional[datetime] = None
        self._question_start_time: Optional[datetime] = None

        # Load question bank
        self._load_bank()

    def _load_bank(self) -> None:
        """Load questions from the question bank file."""
        if not self._bank_file.exists():
            raise FileNotFoundError(f"Quiz bank not found: {self._bank_file}")

        with open(self._bank_file, "r") as f:
            data = json.load(f)

        # Validate and store questions
        questions = data.get("questions", [])
        self._all_questions = [q for q in questions if validate_question(q)]

    def load_questions(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10,
        shuffle: bool = True,
    ) -> int:
        """
        Load and filter questions for a quiz session.

        Args:
            topic: Topic to filter by (None or "all" for all topics)
            difficulty: Difficulty to filter by (None or "all" for all)
            limit: Maximum number of questions
            shuffle: Whether to randomize question order

        Returns:
            Number of questions loaded
        """
        # Reset state
        self._current_idx = 0
        self._answers = []
        self._start_time = datetime.now()
        self._question_start_time = datetime.now()

        # Filter questions
        filtered = filter_questions(
            self._all_questions,
            topic=topic,
            difficulty=difficulty,
        )

        # Shuffle if requested
        if shuffle:
            filtered = filtered.copy()
            random.shuffle(filtered)

        # Apply limit
        self._questions = filtered[:limit]

        return len(self._questions)

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the current question.

        Returns:
            Current question dict or None if quiz is complete/not started
        """
        if not self._questions or self._current_idx >= len(self._questions):
            return None
        return self._questions[self._current_idx]

    def submit_answer(self, answer: str) -> Dict[str, Any]:
        """
        Submit an answer for the current question.

        Args:
            answer: User's answer string

        Returns:
            Dict with:
                - is_correct: bool
                - correct_answer: str
                - explanation: str
                - time_taken: int (seconds)
        """
        question = self.get_current_question()
        if not question:
            return {
                "is_correct": False,
                "correct_answer": "",
                "explanation": "No current question",
                "time_taken": 0,
            }

        # Calculate time taken
        time_taken = 0
        if self._question_start_time:
            delta = datetime.now() - self._question_start_time
            time_taken = int(delta.total_seconds())

        # Check answer
        is_correct = check_answer(question, answer)

        # Record answer
        answer_record = {
            "question_id": question.get("id", ""),
            "question_text": question.get("question", ""),
            "topic": question.get("topic", ""),
            "difficulty": question.get("difficulty", ""),
            "user_answer": answer,
            "correct_answer": question.get("answer", ""),
            "is_correct": is_correct,
            "time_taken": time_taken,
            "explanation": question.get("explanation", ""),
        }
        self._answers.append(answer_record)

        return {
            "is_correct": is_correct,
            "correct_answer": question.get("answer", ""),
            "explanation": question.get("explanation", ""),
            "time_taken": time_taken,
        }

    def next_question(self) -> Optional[Dict[str, Any]]:
        """
        Advance to the next question.

        Returns:
            Next question dict or None if quiz is complete
        """
        self._current_idx += 1
        self._question_start_time = datetime.now()
        return self.get_current_question()

    def get_progress(self) -> Dict[str, Any]:
        """
        Get current quiz progress and statistics.

        Returns:
            Dict with:
                - current: int (1-indexed question number)
                - total: int (total questions)
                - correct: int (correct answers so far)
                - incorrect: int (incorrect answers so far)
                - percentage: float (score percentage)
                - by_topic: dict (breakdown by topic)
        """
        total = len(self._questions)
        answered = len(self._answers)
        correct = sum(1 for a in self._answers if a.get("is_correct"))
        incorrect = answered - correct

        # Calculate by topic
        by_topic: Dict[str, Dict[str, int]] = {}
        for answer in self._answers:
            topic = answer.get("topic", "unknown")
            if topic not in by_topic:
                by_topic[topic] = {"correct": 0, "total": 0}
            by_topic[topic]["total"] += 1
            if answer.get("is_correct"):
                by_topic[topic]["correct"] += 1

        return {
            "current": self._current_idx + 1,
            "total": total,
            "answered": answered,
            "correct": correct,
            "incorrect": incorrect,
            "percentage": (correct / answered * 100) if answered > 0 else 0.0,
            "by_topic": by_topic,
        }

    def is_complete(self) -> bool:
        """
        Check if the quiz is finished.

        Returns:
            True if all questions have been answered
        """
        return len(self._answers) >= len(self._questions) and len(self._questions) > 0

    def get_results(self) -> Dict[str, Any]:
        """
        Get final quiz results.

        Returns:
            Dict with:
                - score: int (correct count)
                - total: int (total questions)
                - percentage: float
                - time_total: int (total seconds)
                - by_topic: dict (breakdown by topic)
                - by_difficulty: dict (breakdown by difficulty)
                - incorrect_questions: list (questions answered incorrectly)
        """
        total = len(self._questions)
        correct = sum(1 for a in self._answers if a.get("is_correct"))

        # Total time
        time_total = 0
        if self._start_time:
            delta = datetime.now() - self._start_time
            time_total = int(delta.total_seconds())

        # By topic
        by_topic: Dict[str, Dict[str, int]] = {}
        for answer in self._answers:
            topic = answer.get("topic", "unknown")
            if topic not in by_topic:
                by_topic[topic] = {"correct": 0, "total": 0}
            by_topic[topic]["total"] += 1
            if answer.get("is_correct"):
                by_topic[topic]["correct"] += 1

        # By difficulty
        by_difficulty: Dict[str, Dict[str, int]] = {}
        for answer in self._answers:
            diff = answer.get("difficulty", "unknown")
            if diff not in by_difficulty:
                by_difficulty[diff] = {"correct": 0, "total": 0}
            by_difficulty[diff]["total"] += 1
            if answer.get("is_correct"):
                by_difficulty[diff]["correct"] += 1

        # Incorrect questions
        incorrect_questions = [
            {
                "question": a.get("question_text", ""),
                "your_answer": a.get("user_answer", ""),
                "correct_answer": a.get("correct_answer", ""),
                "explanation": a.get("explanation", ""),
                "topic": a.get("topic", ""),
            }
            for a in self._answers
            if not a.get("is_correct")
        ]

        return {
            "score": correct,
            "total": total,
            "percentage": (correct / total * 100) if total > 0 else 0.0,
            "time_total": time_total,
            "by_topic": by_topic,
            "by_difficulty": by_difficulty,
            "incorrect_questions": incorrect_questions,
            "answers": self._answers,
        }

    def get_available_topics(self) -> List[str]:
        """
        Get topics that have questions in the bank.

        Returns:
            List of topic names
        """
        topics = set()
        for q in self._all_questions:
            topic = q.get("topic")
            if topic:
                topics.add(topic)
        return sorted(list(topics))

    def get_available_difficulties(self) -> List[str]:
        """
        Get difficulties that have questions in the bank.

        Returns:
            List of difficulty names
        """
        difficulties = set()
        for q in self._all_questions:
            diff = q.get("difficulty")
            if diff:
                difficulties.add(diff)
        return sorted(list(difficulties))

    def get_question_count(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> int:
        """
        Get count of questions matching filters.

        Args:
            topic: Topic filter
            difficulty: Difficulty filter

        Returns:
            Number of matching questions
        """
        filtered = filter_questions(
            self._all_questions,
            topic=topic,
            difficulty=difficulty,
        )
        return len(filtered)
