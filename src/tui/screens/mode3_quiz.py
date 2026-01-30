"""Mode 3: Quiz System - Quiz Screen."""

from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, ProgressBar
from textual.binding import Binding

from ...quiz import QuizEngine, format_options, format_question_display
from ...database.service import save_quiz_session
from .mode3_results import Mode3ResultsScreen


class Mode3QuizScreen(Screen):
    """Quiz screen for displaying and answering questions."""

    CSS = """
    Mode3QuizScreen {
        align: center middle;
    }

    #quiz_container {
        width: 80;
        height: 85%;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }

    #quiz_scroll {
        height: 1fr;
    }

    #header_row {
        height: auto;
        width: 100%;
        margin-bottom: 1;
    }

    #progress_text {
        width: 1fr;
        text-align: left;
        color: $accent;
    }

    #score_text {
        width: 1fr;
        text-align: right;
        color: $success;
    }

    #progress_container {
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 1;
    }

    #progress_bar {
        width: 50%;
    }

    #question_area {
        width: 100%;
        height: auto;
        min-height: 8;
        padding: 1;
        margin-bottom: 1;
        border: solid $primary;
        background: $surface-darken-1;
    }

    #question_text {
        width: 100%;
    }

    #options_area {
        width: 100%;
        height: auto;
    }

    .option_btn {
        width: 100%;
        margin: 0 0 1 0;
    }

    .option_btn.correct {
        background: $success;
    }

    .option_btn.incorrect {
        background: $error;
    }

    .option_btn.revealed {
        background: $success-darken-2;
    }

    #feedback_area {
        width: 100%;
        height: auto;
        padding: 1;
        margin-top: 1;
        border: solid $primary;
        display: none;
    }

    #feedback_area.show {
        display: block;
    }

    #feedback_result {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #feedback_result.correct {
        color: $success;
    }

    #feedback_result.incorrect {
        color: $error;
    }

    #explanation_text {
        color: $text;
    }

    #nav_row {
        margin-top: 1;
        height: 3;
        align: center middle;
    }

    #nav_row Button {
        margin: 0 1;
        width: 20;
        text-align: center;
    }

    #next_btn {
        display: none;
    }

    #next_btn.show {
        display: block;
    }
    """

    BINDINGS = [
        Binding("escape", "quit_quiz", "Quit Quiz", show=True),
        Binding("a", "select_a", "A", show=False),
        Binding("b", "select_b", "B", show=False),
        Binding("c", "select_c", "C", show=False),
        Binding("d", "select_d", "D", show=False),
        Binding("enter", "next_or_submit", "Next", show=False),
    ]

    def __init__(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        question_count: int = 10,
    ) -> None:
        """
        Initialize the quiz screen.

        Args:
            topic: Topic filter (None for all)
            difficulty: Difficulty filter (None for all)
            question_count: Number of questions
        """
        super().__init__()
        self.topic = topic
        self.difficulty = difficulty
        self.question_count = question_count
        self.engine = QuizEngine()
        self.current_question: Optional[Dict[str, Any]] = None
        self.answered = False
        self.feedback_result: Optional[Dict[str, Any]] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="quiz_container"):
            # Header with progress and score
            with Horizontal(id="header_row"):
                yield Static("Question 1/10", id="progress_text")
                yield Static("Score: 0/0", id="score_text")

            # Progress bar
            with Container(id="progress_container"):
                yield ProgressBar(id="progress_bar", total=100, show_eta=False)

            # Scrollable content area
            with VerticalScroll(id="quiz_scroll"):
                # Question area
                with Container(id="question_area"):
                    yield Static("Loading question...", id="question_text")

                # Options area
                with Container(id="options_area"):
                    yield Button("A) ...", id="opt_A", classes="option_btn")
                    yield Button("B) ...", id="opt_B", classes="option_btn")
                    yield Button("C) ...", id="opt_C", classes="option_btn")
                    yield Button("D) ...", id="opt_D", classes="option_btn")

                # Feedback area (hidden initially)
                with Container(id="feedback_area"):
                    yield Static("", id="feedback_result")
                    yield Static("", id="explanation_text")

            # Navigation (outside scroll, always visible)
            with Horizontal(id="nav_row"):
                yield Button("Next Question", id="next_btn", variant="primary")
                yield Button("Quit Quiz", id="quit_btn", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize quiz when screen is mounted."""
        # Load questions
        self.engine.load_questions(
            topic=self.topic,
            difficulty=self.difficulty,
            limit=self.question_count,
        )
        self._display_current_question()

    def _display_current_question(self) -> None:
        """Display the current question."""
        self.current_question = self.engine.get_current_question()
        self.answered = False
        self.feedback_result = None

        if not self.current_question:
            # Quiz complete
            self._show_results()
            return

        # Update progress
        progress = self.engine.get_progress()
        progress_text = self.query_one("#progress_text", Static)
        progress_text.update(f"Question {progress['current']}/{progress['total']}")

        score_text = self.query_one("#score_text", Static)
        score_text.update(f"Score: {progress['correct']}/{progress['answered']}")

        # Update progress bar (based on questions answered)
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        pct = progress["answered"] / progress["total"] * 100
        progress_bar.progress = pct

        # Display question
        question_display = format_question_display(self.current_question)
        question_text = self.query_one("#question_text", Static)
        question_text.update(question_display)

        # Display options
        options = self.current_question.get("options", [])
        formatted = format_options(options)
        labels = ["A", "B", "C", "D"]

        for i, label in enumerate(labels):
            btn = self.query_one(f"#opt_{label}", Button)
            if i < len(formatted):
                btn.label = formatted[i]
                btn.display = True
                btn.remove_class("correct", "incorrect", "revealed")
                btn.disabled = False
            else:
                btn.display = False

        # Hide feedback
        feedback = self.query_one("#feedback_area", Container)
        feedback.remove_class("show")

        # Hide next button
        next_btn = self.query_one("#next_btn", Button)
        next_btn.remove_class("show")

    def _submit_answer(self, answer: str) -> None:
        """Submit an answer."""
        if self.answered or not self.current_question:
            return

        self.answered = True
        self.feedback_result = self.engine.submit_answer(answer)

        # Update button styles
        options = self.current_question.get("options", [])
        correct_answer = self.current_question.get("answer", "")
        labels = ["A", "B", "C", "D"]

        for i, label in enumerate(labels):
            if i >= len(options):
                break
            btn = self.query_one(f"#opt_{label}", Button)
            btn.disabled = True

            if options[i] == answer:
                if self.feedback_result["is_correct"]:
                    btn.add_class("correct")
                else:
                    btn.add_class("incorrect")

            if options[i] == correct_answer and not self.feedback_result["is_correct"]:
                btn.add_class("revealed")

        # Show feedback
        feedback = self.query_one("#feedback_area", Container)
        feedback.add_class("show")

        result_text = self.query_one("#feedback_result", Static)
        if self.feedback_result["is_correct"]:
            result_text.update("[bold green]Correct![/bold green]")
            result_text.add_class("correct")
            result_text.remove_class("incorrect")
        else:
            result_text.update(
                f"[bold red]Incorrect[/bold red] - Answer: {correct_answer}"
            )
            result_text.add_class("incorrect")
            result_text.remove_class("correct")

        explanation = self.query_one("#explanation_text", Static)
        explanation.update(self.feedback_result.get("explanation", ""))

        # Show next button (change label on last question)
        next_btn = self.query_one("#next_btn", Button)
        progress = self.engine.get_progress()
        if progress["answered"] >= progress["total"]:
            next_btn.label = "View Results"
        else:
            next_btn.label = "Next Question"
        next_btn.remove_class("show")
        next_btn.add_class("show")

        # Update score display
        progress = self.engine.get_progress()
        score_text = self.query_one("#score_text", Static)
        score_text.update(f"Score: {progress['correct']}/{progress['answered']}")

    def _next_question(self) -> None:
        """Move to next question."""
        if not self.answered:
            return

        self.engine.next_question()

        if self.engine.is_complete():
            self._show_results()
        else:
            self._display_current_question()

    def _show_results(self) -> None:
        """Show quiz results screen and save to database."""
        results = self.engine.get_results()

        # Save session (also saves individual attempts internally)
        try:
            save_quiz_session(
                results=results,
                topic=self.topic,
                difficulty=self.difficulty,
            )
        except Exception:
            pass  # Continue to show results even if save fails

        self.app.switch_screen(Mode3ResultsScreen(results=results))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id or ""

        if button_id == "quit_btn":
            self.action_quit_quiz()
        elif button_id == "next_btn":
            self._next_question()
        elif button_id.startswith("opt_"):
            label = button_id[4:]  # Extract A, B, C, D
            options = (
                self.current_question.get("options", [])
                if self.current_question
                else []
            )
            labels = ["A", "B", "C", "D"]
            if label in labels:
                idx = labels.index(label)
                if idx < len(options):
                    self._submit_answer(options[idx])

    def action_select_a(self) -> None:
        """Select option A."""
        self._select_option(0)

    def action_select_b(self) -> None:
        """Select option B."""
        self._select_option(1)

    def action_select_c(self) -> None:
        """Select option C."""
        self._select_option(2)

    def action_select_d(self) -> None:
        """Select option D."""
        self._select_option(3)

    def _select_option(self, index: int) -> None:
        """Select option by index."""
        if self.answered or not self.current_question:
            return
        options = self.current_question.get("options", [])
        if index < len(options):
            self._submit_answer(options[index])

    def action_next_or_submit(self) -> None:
        """Handle enter key - next question if answered."""
        if self.answered:
            self._next_question()

    def action_quit_quiz(self) -> None:
        """Quit quiz and return to setup, saving any progress."""
        results = self.engine.get_results()
        if results.get("answers"):
            # Save session (also saves individual attempts internally)
            try:
                save_quiz_session(
                    results=results,
                    topic=self.topic,
                    difficulty=self.difficulty,
                )
            except Exception:
                pass

        self.app.pop_screen()
