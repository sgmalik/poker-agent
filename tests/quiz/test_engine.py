"""Tests for quiz engine."""

import pytest
from src.quiz.engine import QuizEngine


class TestQuizEngineInit:
    """Tests for QuizEngine initialization."""

    def test_creates_with_default_bank(self):
        """Should create engine with default bank file."""
        engine = QuizEngine()
        assert engine._all_questions is not None
        assert len(engine._all_questions) > 0

    def test_loads_valid_questions(self):
        """Should only load valid questions."""
        engine = QuizEngine()
        # All loaded questions should be valid
        for q in engine._all_questions:
            assert "id" in q
            assert "type" in q
            assert "options" in q
            assert "answer" in q


class TestLoadQuestions:
    """Tests for loading and filtering questions."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine instance."""
        return QuizEngine()

    def test_load_all_questions(self, engine):
        """Should load all questions with no filters."""
        count = engine.load_questions(limit=100)
        assert count > 0
        assert len(engine._questions) == count

    def test_load_with_limit(self, engine):
        """Should respect question limit."""
        count = engine.load_questions(limit=5)
        assert count <= 5
        assert len(engine._questions) <= 5

    def test_load_by_topic(self, engine):
        """Should filter by topic."""
        count = engine.load_questions(topic="preflop", limit=100)
        assert count > 0
        for q in engine._questions:
            assert q["topic"] == "preflop"

    def test_load_by_difficulty(self, engine):
        """Should filter by difficulty."""
        count = engine.load_questions(difficulty="beginner", limit=100)
        assert count > 0
        for q in engine._questions:
            assert q["difficulty"] == "beginner"

    def test_load_by_topic_and_difficulty(self, engine):
        """Should filter by both topic and difficulty."""
        for q in engine._questions:
            assert q["topic"] == "preflop"
            assert q["difficulty"] == "beginner"

    def test_load_resets_state(self, engine):
        """Loading should reset quiz state."""
        engine.load_questions(limit=5)
        engine._current_idx = 3
        engine._answers = [{"is_correct": True}]

        engine.load_questions(limit=5)
        assert engine._current_idx == 0
        assert len(engine._answers) == 0


class TestQuizFlow:
    """Tests for quiz question flow."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine with loaded questions."""
        engine = QuizEngine()
        engine.load_questions(limit=5, shuffle=False)
        return engine

    def test_get_current_question(self, engine):
        """Should get current question."""
        q = engine.get_current_question()
        assert q is not None
        assert "question" in q
        assert "options" in q

    def test_get_current_question_empty(self):
        """Should return None if no questions loaded."""
        engine = QuizEngine()
        # Don't call load_questions
        assert engine.get_current_question() is None

    def test_next_question(self, engine):
        """Should advance to next question."""
        second = engine.next_question()

        # First and second should be different (when not at end)
        if second is not None:
            assert engine._current_idx == 1

    def test_next_question_at_end(self, engine):
        """Should return None at end of quiz."""
        # Advance to end
        for _ in range(10):
            engine.next_question()

        assert engine.get_current_question() is None


class TestSubmitAnswer:
    """Tests for answer submission."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine with loaded questions."""
        engine = QuizEngine()
        engine.load_questions(limit=5, shuffle=False)
        return engine

    def test_correct_answer(self, engine):
        """Should identify correct answer."""
        q = engine.get_current_question()
        correct_answer = q["answer"]

        result = engine.submit_answer(correct_answer)
        assert result["is_correct"] is True
        assert result["correct_answer"] == correct_answer

    def test_incorrect_answer(self, engine):
        """Should identify incorrect answer."""
        q = engine.get_current_question()
        correct_answer = q["answer"]
        wrong_answer = [opt for opt in q["options"] if opt != correct_answer][0]

        result = engine.submit_answer(wrong_answer)
        assert result["is_correct"] is False
        assert result["correct_answer"] == correct_answer

    def test_returns_explanation(self, engine):
        """Should return explanation."""
        q = engine.get_current_question()
        result = engine.submit_answer(q["answer"])
        assert "explanation" in result
        assert len(result["explanation"]) > 0

    def test_records_answer(self, engine):
        """Should record answer in answers list."""
        q = engine.get_current_question()
        engine.submit_answer(q["answer"])

        assert len(engine._answers) == 1
        assert engine._answers[0]["question_id"] == q["id"]

    def test_tracks_time(self, engine):
        """Should track time taken."""
        q = engine.get_current_question()
        result = engine.submit_answer(q["answer"])

        assert "time_taken" in result
        assert isinstance(result["time_taken"], int)


class TestProgress:
    """Tests for progress tracking."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine with loaded questions."""
        engine = QuizEngine()
        engine.load_questions(limit=5, shuffle=False)
        return engine

    def test_initial_progress(self, engine):
        """Should show initial progress."""
        progress = engine.get_progress()
        assert progress["current"] == 1
        assert progress["total"] == 5
        assert progress["correct"] == 0
        assert progress["incorrect"] == 0

    def test_progress_after_answer(self, engine):
        """Should update after answering."""
        q = engine.get_current_question()
        engine.submit_answer(q["answer"])

        progress = engine.get_progress()
        assert progress["answered"] == 1
        assert progress["correct"] == 1

    def test_progress_percentage(self, engine):
        """Should calculate percentage."""
        # Answer first correctly
        q1 = engine.get_current_question()
        engine.submit_answer(q1["answer"])
        engine.next_question()

        # Answer second incorrectly
        q2 = engine.get_current_question()
        wrong = [opt for opt in q2["options"] if opt != q2["answer"]][0]
        engine.submit_answer(wrong)

        progress = engine.get_progress()
        assert progress["percentage"] == 50.0


class TestIsComplete:
    """Tests for quiz completion."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine with loaded questions."""
        engine = QuizEngine()
        engine.load_questions(limit=2, shuffle=False)
        return engine

    def test_not_complete_initially(self, engine):
        """Should not be complete at start."""
        assert engine.is_complete() is False

    def test_not_complete_partial(self, engine):
        """Should not be complete with partial answers."""
        q = engine.get_current_question()
        engine.submit_answer(q["answer"])
        assert engine.is_complete() is False

    def test_complete_after_all_answered(self, engine):
        """Should be complete after all questions answered."""
        for _ in range(2):
            q = engine.get_current_question()
            if q:
                engine.submit_answer(q["answer"])
                engine.next_question()

        assert engine.is_complete() is True


class TestResults:
    """Tests for final results."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine and complete a quiz."""
        engine = QuizEngine()
        engine.load_questions(limit=3, shuffle=False)

        # Answer all questions (first correct, rest wrong)
        for i in range(3):
            q = engine.get_current_question()
            if q:
                if i == 0:
                    engine.submit_answer(q["answer"])
                else:
                    wrong = [opt for opt in q["options"] if opt != q["answer"]][0]
                    engine.submit_answer(wrong)
                engine.next_question()

        return engine

    def test_results_score(self, engine):
        """Should return correct score."""
        results = engine.get_results()
        assert results["score"] == 1
        assert results["total"] == 3

    def test_results_percentage(self, engine):
        """Should calculate percentage."""
        results = engine.get_results()
        assert abs(results["percentage"] - 33.33) < 1

    def test_results_by_topic(self, engine):
        """Should break down by topic."""
        results = engine.get_results()
        assert "by_topic" in results
        assert isinstance(results["by_topic"], dict)

    def test_results_incorrect_questions(self, engine):
        """Should list incorrect questions."""
        results = engine.get_results()
        assert "incorrect_questions" in results
        assert len(results["incorrect_questions"]) == 2


class TestMetadata:
    """Tests for question metadata queries."""

    @pytest.fixture
    def engine(self):
        """Create QuizEngine instance."""
        return QuizEngine()

    def test_get_available_topics(self, engine):
        """Should return available topics."""
        topics = engine.get_available_topics()
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert "preflop" in topics

    def test_get_available_difficulties(self, engine):
        """Should return available difficulties."""
        diffs = engine.get_available_difficulties()
        assert isinstance(diffs, list)
        assert len(diffs) > 0
        assert "beginner" in diffs

    def test_get_question_count(self, engine):
        """Should return question count."""
        count = engine.get_question_count()
        assert count > 0

    def test_get_question_count_filtered(self, engine):
        """Should return filtered count."""
        total = engine.get_question_count()
        preflop = engine.get_question_count(topic="preflop")
        assert preflop <= total
        assert preflop > 0
