"""Tests for quiz questions module."""

import pytest
from src.quiz.questions import (
    DIFFICULTIES,
    QUESTION_TYPES,
    TOPICS,
    check_answer,
    filter_questions,
    format_options,
    format_question_display,
    get_difficulties,
    get_option_from_label,
    get_topics,
    validate_question,
)


class TestConstants:
    """Tests for module constants."""

    def test_topics_list(self):
        """Should have expected topics."""
        assert "preflop" in TOPICS
        assert "ranges" in TOPICS
        assert "pot_odds" in TOPICS
        assert "hand_strength" in TOPICS
        assert "position" in TOPICS

    def test_difficulties_list(self):
        """Should have expected difficulties."""
        assert "beginner" in DIFFICULTIES
        assert "intermediate" in DIFFICULTIES
        assert "advanced" in DIFFICULTIES

    def test_question_types_list(self):
        """Should have expected question types."""
        assert "preflop_action" in QUESTION_TYPES
        assert "range_check" in QUESTION_TYPES
        assert "hand_strength" in QUESTION_TYPES
        assert "pot_odds" in QUESTION_TYPES
        assert "position_open" in QUESTION_TYPES


class TestValidateQuestion:
    """Tests for validate_question function."""

    @pytest.fixture
    def valid_question(self):
        """Return a valid question dict."""
        return {
            "id": "test_001",
            "type": "preflop_action",
            "difficulty": "beginner",
            "topic": "preflop",
            "question": "What should you do with AA?",
            "options": ["Fold", "Call", "Raise"],
            "answer": "Raise",
            "explanation": "AA is the best hand.",
        }

    def test_valid_question_passes(self, valid_question):
        """Valid question should pass validation."""
        assert validate_question(valid_question) is True

    def test_missing_id_fails(self, valid_question):
        """Question without id should fail."""
        del valid_question["id"]
        assert validate_question(valid_question) is False

    def test_empty_id_fails(self, valid_question):
        """Question with empty id should fail."""
        valid_question["id"] = ""
        assert validate_question(valid_question) is False

    def test_missing_type_fails(self, valid_question):
        """Question without type should fail."""
        del valid_question["type"]
        assert validate_question(valid_question) is False

    def test_invalid_type_fails(self, valid_question):
        """Question with invalid type should fail."""
        valid_question["type"] = "invalid_type"
        assert validate_question(valid_question) is False

    def test_invalid_topic_fails(self, valid_question):
        """Question with invalid topic should fail."""
        valid_question["topic"] = "invalid_topic"
        assert validate_question(valid_question) is False

    def test_invalid_difficulty_fails(self, valid_question):
        """Question with invalid difficulty should fail."""
        valid_question["difficulty"] = "impossible"
        assert validate_question(valid_question) is False

    def test_empty_options_fails(self, valid_question):
        """Question with empty options should fail."""
        valid_question["options"] = []
        assert validate_question(valid_question) is False

    def test_single_option_fails(self, valid_question):
        """Question with only one option should fail."""
        valid_question["options"] = ["Only option"]
        assert validate_question(valid_question) is False

    def test_answer_not_in_options_fails(self, valid_question):
        """Question with answer not in options should fail."""
        valid_question["answer"] = "Bet"
        assert validate_question(valid_question) is False


class TestCheckAnswer:
    """Tests for check_answer function."""

    @pytest.fixture
    def question(self):
        """Return a question dict."""
        return {
            "answer": "Raise",
        }

    def test_correct_answer(self, question):
        """Correct answer should return True."""
        assert check_answer(question, "Raise") is True

    def test_case_insensitive(self, question):
        """Answer check should be case insensitive."""
        assert check_answer(question, "raise") is True
        assert check_answer(question, "RAISE") is True
        assert check_answer(question, "RaIsE") is True

    def test_whitespace_trimmed(self, question):
        """Whitespace should be trimmed."""
        assert check_answer(question, "  Raise  ") is True
        assert check_answer(question, "\tRaise\n") is True

    def test_wrong_answer(self, question):
        """Wrong answer should return False."""
        assert check_answer(question, "Fold") is False
        assert check_answer(question, "Call") is False


class TestFormatQuestionDisplay:
    """Tests for format_question_display function."""

    def test_basic_question(self):
        """Should format basic question text."""
        question = {
            "question": "What should you do?",
            "scenario": {},
        }
        result = format_question_display(question)
        assert "[bold]What should you do?[/bold]" in result

    def test_with_hero_hand(self):
        """Should include formatted hero hand."""
        question = {
            "question": "What should you do?",
            "scenario": {"hero_hand": "As Kh"},
        }
        result = format_question_display(question)
        assert "Hand:" in result

    def test_with_position(self):
        """Should include position."""
        question = {
            "question": "What should you do?",
            "scenario": {"position": "BTN"},
        }
        result = format_question_display(question)
        assert "Position:" in result
        assert "BTN" in result

    def test_with_board(self):
        """Should include board."""
        question = {
            "question": "What should you do?",
            "scenario": {"board": "Ah Kc 2d"},
        }
        result = format_question_display(question)
        assert "Board:" in result


class TestFormatOptions:
    """Tests for format_options function."""

    def test_two_options(self):
        """Should format two options."""
        result = format_options(["Yes", "No"])
        assert result == ["A) Yes", "B) No"]

    def test_four_options(self):
        """Should format four options."""
        result = format_options(["Fold", "Call", "Raise", "All-in"])
        assert result[0] == "A) Fold"
        assert result[1] == "B) Call"
        assert result[2] == "C) Raise"
        assert result[3] == "D) All-in"


class TestGetOptionFromLabel:
    """Tests for get_option_from_label function."""

    def test_valid_labels(self):
        """Should return option for valid labels."""
        options = ["Fold", "Call", "Raise"]
        assert get_option_from_label(options, "A") == "Fold"
        assert get_option_from_label(options, "B") == "Call"
        assert get_option_from_label(options, "C") == "Raise"

    def test_lowercase_labels(self):
        """Should work with lowercase labels."""
        options = ["Fold", "Call", "Raise"]
        assert get_option_from_label(options, "a") == "Fold"
        assert get_option_from_label(options, "b") == "Call"

    def test_invalid_label(self):
        """Should return empty string for invalid label."""
        options = ["Fold", "Call"]
        assert get_option_from_label(options, "Z") == ""
        assert get_option_from_label(options, "C") == ""


class TestFilterQuestions:
    """Tests for filter_questions function."""

    @pytest.fixture
    def questions(self):
        """Return list of test questions."""
        return [
            {"topic": "preflop", "difficulty": "beginner"},
            {"topic": "preflop", "difficulty": "advanced"},
            {"topic": "ranges", "difficulty": "beginner"},
            {"topic": "pot_odds", "difficulty": "intermediate"},
        ]

    def test_no_filters(self, questions):
        """No filters should return all questions."""
        result = filter_questions(questions)
        assert len(result) == 4

    def test_filter_by_topic(self, questions):
        """Should filter by topic."""
        result = filter_questions(questions, topic="preflop")
        assert len(result) == 2
        assert all(q["topic"] == "preflop" for q in result)

    def test_filter_by_difficulty(self, questions):
        """Should filter by difficulty."""
        result = filter_questions(questions, difficulty="beginner")
        assert len(result) == 2
        assert all(q["difficulty"] == "beginner" for q in result)

    def test_filter_by_both(self, questions):
        """Should filter by topic and difficulty."""
        result = filter_questions(questions, topic="preflop", difficulty="beginner")
        assert len(result) == 1
        assert result[0]["topic"] == "preflop"
        assert result[0]["difficulty"] == "beginner"

    def test_all_topic_returns_all(self, questions):
        """Topic 'all' should return all."""
        result = filter_questions(questions, topic="all")
        assert len(result) == 4

    def test_all_difficulty_returns_all(self, questions):
        """Difficulty 'all' should return all."""
        result = filter_questions(questions, difficulty="all")
        assert len(result) == 4


class TestGetFunctions:
    """Tests for get_topics and get_difficulties functions."""

    def test_get_topics(self):
        """Should return list of topics."""
        topics = get_topics()
        assert isinstance(topics, list)
        assert len(topics) >= 5
        assert "preflop" in topics

    def test_get_difficulties(self):
        """Should return list of difficulties."""
        diffs = get_difficulties()
        assert isinstance(diffs, list)
        assert len(diffs) >= 3
        assert "beginner" in diffs
