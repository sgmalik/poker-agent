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
        height: 85%;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }

    #header_section {
        height: auto;
        width: 100%;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        color: $accent;
        text-style: bold;
    }

    #score_big {
        text-align: center;
        width: 100%;
        padding: 1;
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

    #time_display {
        text-align: center;
        width: 100%;
        color: $text-muted;
    }

    #incorrect_title {
        color: $error;
        text-style: bold;
        padding: 1 0;
    }

    #incorrect_scroll {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    .incorrect_item {
        padding: 1;
        margin-bottom: 1;
    }

    #nav_row {
        height: 3;
        width: 100%;
        align: center middle;
    }

    #nav_row Button {
        margin: 0 1;
        width: 20;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("escape", "main_menu", "Main Menu", show=True),
        Binding("n", "new_quiz", "New Quiz", show=True),
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

        incorrect = self.results.get("incorrect_questions", [])

        with Container(id="results_container"):
            # Header section (fixed height)
            with Container(id="header_section"):
                yield Static("[bold cyan]Quiz Complete![/bold cyan]", id="title")
                yield self._create_score_display()
                yield Static(self._format_time(), id="time_display")

            # Incorrect questions scroll area (takes remaining space)
            if incorrect:
                yield Static(
                    f"Review Incorrect Answers ({len(incorrect)})",
                    id="incorrect_title",
                )
                with VerticalScroll(id="incorrect_scroll"):
                    for i, q in enumerate(incorrect):
                        yield self._create_incorrect_item(i + 1, q)

            # Navigation buttons (fixed height at bottom)
            with Horizontal(id="nav_row"):
                yield Button("New Quiz", id="new_quiz_btn", variant="primary")
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
        order = ["beginner", "intermediate", "advanced", "elite"]
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

    def _create_incorrect_item(self, num: int, item: Dict[str, Any]) -> Static:
        """Create an incorrect question display item."""
        question = item.get("question", "")
        your_answer = item.get("your_answer", "")
        correct_answer = item.get("correct_answer", "")

        text = (
            f"[bold]{num}. {question}[/bold]\n"
            f"   Your answer: [red]{your_answer}[/red]\n"
            f"   Correct: [green]{correct_answer}[/green]\n"
        )
        return Static(text, classes="incorrect_item")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "menu_btn":
            self.action_main_menu()
        elif button_id == "new_quiz_btn":
            self.action_new_quiz()

    def action_main_menu(self) -> None:
        """Return to main menu."""
        # Pop results and setup screens (quiz used switch_screen)
        self.app.pop_screen()  # Results screen
        self.app.pop_screen()  # Setup screen

    def action_new_quiz(self) -> None:
        """Go to quiz setup to start a new quiz."""
        # Pop results screen to get back to setup (quiz used switch_screen)
        self.app.pop_screen()  # Results screen
