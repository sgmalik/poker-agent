"""Mode 3: Quiz System - Results Screen."""

from typing import Any, Dict
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding


class Mode3ResultsScreen(Screen):
    """Results screen showing final quiz score and breakdown."""

    CSS = """
    Mode3ResultsScreen {
        align: center middle;
    }

    #results_container {
        width: 80;
        height: auto;
        max-height: 90%;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        color: $accent;
        text-style: bold;
    }

    #score_display {
        text-align: center;
        width: 100%;
        padding: 2;
        margin-bottom: 1;
    }

    #score_big {
        text-style: bold;
    }

    #score_big.excellent {
        color: $success;
    }

    #score_big.good {
        color: $warning;
    }

    #score_big.needs_work {
        color: $error;
    }

    .section {
        width: 100%;
        margin-bottom: 1;
        padding: 1;
        border: solid $primary;
    }

    .section_title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .breakdown_row {
        height: auto;
    }

    .breakdown_label {
        width: 1fr;
        color: $text;
    }

    .breakdown_value {
        width: auto;
        min-width: 10;
        text-align: right;
    }

    .breakdown_value.good {
        color: $success;
    }

    .breakdown_value.bad {
        color: $error;
    }

    #incorrect_scroll {
        height: auto;
        max-height: 20;
    }

    .incorrect_item {
        padding: 1;
        margin-bottom: 1;
        border: solid $error;
        background: $surface-darken-1;
    }

    .incorrect_question {
        color: $text;
        margin-bottom: 1;
    }

    .incorrect_answers {
        color: $text-muted;
    }

    .incorrect_correct {
        color: $success;
    }

    .incorrect_explanation {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }

    #nav_row {
        margin-top: 2;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    #time_display {
        text-align: center;
        width: 100%;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "main_menu", "Main Menu", show=True),
        Binding("r", "try_again", "Try Again", show=True),
    ]

    def __init__(self, results: Dict[str, Any]) -> None:
        """
        Initialize the results screen.

        Args:
            results: Quiz results dictionary from QuizEngine
        """
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="results_container"):
            yield Static("[bold cyan]Quiz Complete![/bold cyan]", id="title")

            # Score display
            with Container(id="score_display"):
                yield self._create_score_display()

            # Time display
            yield Static(self._format_time(), id="time_display")

            with VerticalScroll():
                # Topic breakdown
                if self.results.get("by_topic"):
                    with Container(classes="section"):
                        yield Static("Performance by Topic", classes="section_title")
                        yield self._create_topic_breakdown()

                # Difficulty breakdown
                if self.results.get("by_difficulty"):
                    with Container(classes="section"):
                        yield Static(
                            "Performance by Difficulty", classes="section_title"
                        )
                        yield self._create_difficulty_breakdown()

                # Incorrect questions
                incorrect = self.results.get("incorrect_questions", [])
                if incorrect:
                    with Container(classes="section"):
                        yield Static(
                            f"Review Incorrect Answers ({len(incorrect)})",
                            classes="section_title",
                        )
                        with VerticalScroll(id="incorrect_scroll"):
                            for i, q in enumerate(incorrect[:5]):  # Show first 5
                                yield self._create_incorrect_item(i + 1, q)
                            if len(incorrect) > 5:
                                yield Static(
                                    f"[dim]... and {len(incorrect) - 5} more[/dim]"
                                )

            # Navigation
            with Horizontal(id="nav_row"):
                yield Button("Try Again", id="try_again_btn", variant="primary")
                yield Button("Main Menu", id="menu_btn", variant="default")

        yield Footer()

    def _create_score_display(self) -> Static:
        """Create the main score display."""
        score = self.results.get("score", 0)
        total = self.results.get("total", 0)
        pct = self.results.get("percentage", 0)

        # Determine grade
        if pct >= 80:
            grade_class = "excellent"
            grade_text = "Excellent!"
        elif pct >= 60:
            grade_class = "good"
            grade_text = "Good job!"
        else:
            grade_class = "needs_work"
            grade_text = "Keep practicing!"

        text = f"[bold {grade_class}]{score}/{total}[/bold {grade_class}] ({pct:.1f}%)\n{grade_text}"
        widget = Static(text, id="score_big")
        widget.add_class(grade_class)
        return widget

    def _format_time(self) -> str:
        """Format total time."""
        seconds = self.results.get("time_total", 0)
        mins = seconds // 60
        secs = seconds % 60
        return f"[dim]Time: {mins}m {secs}s[/dim]"

    def _create_topic_breakdown(self) -> Container:
        """Create topic breakdown display."""
        container = Container()
        by_topic = self.results.get("by_topic", {})

        for topic, data in sorted(by_topic.items()):
            correct = data.get("correct", 0)
            total = data.get("total", 0)
            pct = (correct / total * 100) if total > 0 else 0

            row = Horizontal(classes="breakdown_row")
            label = Static(topic.replace("_", " ").title(), classes="breakdown_label")
            value_class = "good" if pct >= 70 else "bad"
            value = Static(
                f"{correct}/{total} ({pct:.0f}%)",
                classes=f"breakdown_value {value_class}",
            )

            container.compose_add_child(row)
            row.compose_add_child(label)
            row.compose_add_child(value)

        return container

    def _create_difficulty_breakdown(self) -> Container:
        """Create difficulty breakdown display."""
        container = Container()
        by_diff = self.results.get("by_difficulty", {})

        # Order difficulties
        order = ["beginner", "intermediate", "advanced"]
        sorted_diffs = sorted(
            by_diff.items(), key=lambda x: order.index(x[0]) if x[0] in order else 99
        )

        for diff, data in sorted_diffs:
            correct = data.get("correct", 0)
            total = data.get("total", 0)
            pct = (correct / total * 100) if total > 0 else 0

            row = Horizontal(classes="breakdown_row")
            label = Static(diff.title(), classes="breakdown_label")
            value_class = "good" if pct >= 70 else "bad"
            value = Static(
                f"{correct}/{total} ({pct:.0f}%)",
                classes=f"breakdown_value {value_class}",
            )

            container.compose_add_child(row)
            row.compose_add_child(label)
            row.compose_add_child(value)

        return container

    def _create_incorrect_item(self, num: int, item: Dict[str, Any]) -> Container:
        """Create an incorrect question display item."""
        container = Container(classes="incorrect_item")

        question = item.get("question", "")
        your_answer = item.get("your_answer", "")
        correct_answer = item.get("correct_answer", "")
        explanation = item.get("explanation", "")
        topic = item.get("topic", "").replace("_", " ").title()

        container.compose_add_child(
            Static(
                f"[bold]{num}. {question}[/bold] [{topic}]",
                classes="incorrect_question",
            )
        )
        container.compose_add_child(
            Static(
                f"Your answer: [red]{your_answer}[/red]", classes="incorrect_answers"
            )
        )
        container.compose_add_child(
            Static(
                f"Correct: [green]{correct_answer}[/green]", classes="incorrect_correct"
            )
        )
        if explanation:
            container.compose_add_child(
                Static(f"[dim]{explanation}[/dim]", classes="incorrect_explanation")
            )

        return container

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "menu_btn":
            self.action_main_menu()
        elif button_id == "try_again_btn":
            self.action_try_again()

    def action_main_menu(self) -> None:
        """Return to main menu."""
        # Pop both results and quiz screens to get back to setup
        # Then pop setup to get to main menu
        self.app.pop_screen()  # This screen (results)
        self.app.pop_screen()  # Setup screen

    def action_try_again(self) -> None:
        """Start a new quiz with same settings."""
        # Just pop this screen to go back to setup
        self.app.pop_screen()
