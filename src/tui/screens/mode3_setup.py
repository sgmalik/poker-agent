"""Mode 3: Quiz System - Setup Screen."""

from typing import Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Label, Select
from textual.binding import Binding

from ...quiz import QuizEngine


class Mode3SetupScreen(Screen):
    """Quiz setup screen for topic, difficulty, and question count selection."""

    CSS = """
    Mode3SetupScreen {
        align: center middle;
    }

    #setup_container {
        width: 65;
        height: auto;
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

    #subtitle {
        text-align: center;
        width: 100%;
        padding: 0 0 2 0;
        color: $text-muted;
    }

    .section_title {
        width: 100%;
        padding: 1 0 0 0;
        color: $accent;
        text-style: bold;
    }

    .input_group {
        height: auto;
        margin-bottom: 1;
    }

    .label {
        width: 18;
        color: $text;
        content-align: left middle;
    }

    Select {
        width: 1fr;
    }

    .button_row {
        margin-top: 2;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
        width: 20;
        text-align: center;
    }

    .help_text {
        color: $text-muted;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }

    #question_count {
        text-align: center;
        width: 100%;
        padding: 1 0;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("enter", "start_quiz", "Start Quiz", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the setup screen."""
        super().__init__()
        self.engine = QuizEngine()
        self.selected_topic: Optional[str] = None
        self.selected_difficulty: Optional[str] = None
        self.selected_count: int = 10

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="setup_container"):
            yield Static("[bold cyan]Quiz System[/bold cyan]", id="title")
            yield Static("Test your poker knowledge", id="subtitle")

            # Topic selection
            yield Static("Select Topic:", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Label("Topic:", classes="label")
                topics = self.engine.get_available_topics()
                topic_options = [("All Topics", "all")] + [
                    (t.replace("_", " ").title(), t) for t in topics
                ]
                yield Select(
                    topic_options,
                    id="topic_select",
                    value="all",
                )

            # Difficulty selection
            with Horizontal(classes="input_group"):
                yield Label("Difficulty:", classes="label")
                diffs = self.engine.get_available_difficulties()
                diff_options = [("All Levels", "all")] + [(d.title(), d) for d in diffs]
                yield Select(
                    diff_options,
                    id="difficulty_select",
                    value="all",
                )

            # Question count selection
            with Horizontal(classes="input_group"):
                yield Label("Questions:", classes="label")
                yield Select(
                    [
                        ("5 questions", "5"),
                        ("10 questions", "10"),
                        ("15 questions", "15"),
                        ("20 questions", "20"),
                    ],
                    id="count_select",
                    value="10",
                )

            # Question count display
            yield Static(
                self._get_count_text(),
                id="question_count",
            )

            # Buttons
            with Horizontal(classes="button_row"):
                yield Button("Start Quiz", id="start_btn", variant="primary")
                yield Button("Back", id="back_btn", variant="default")

            # Help text
            yield Static(
                "[dim]Press Enter to start or Escape to go back[/dim]",
                classes="help_text",
            )

        yield Footer()

    def _get_count_text(self) -> str:
        """Get available question count text."""
        topic = self.selected_topic if self.selected_topic != "all" else None
        diff = self.selected_difficulty if self.selected_difficulty != "all" else None
        count = self.engine.get_question_count(topic=topic, difficulty=diff)
        return f"[dim]{count} questions available[/dim]"

    def _update_count_display(self) -> None:
        """Update the question count display."""
        count_label = self.query_one("#question_count", Static)
        count_label.update(self._get_count_text())

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle selection changes."""
        select_id = event.select.id
        value = str(event.value) if event.value else None

        if select_id == "topic_select":
            self.selected_topic = value
            self._update_count_display()
        elif select_id == "difficulty_select":
            self.selected_difficulty = value
            self._update_count_display()
        elif select_id == "count_select":
            self.selected_count = int(value) if value else 10

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "start_btn":
            self.action_start_quiz()

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()

    def action_start_quiz(self) -> None:
        """Start the quiz with selected options."""
        # Get selected values
        topic = self.selected_topic if self.selected_topic != "all" else None
        difficulty = (
            self.selected_difficulty if self.selected_difficulty != "all" else None
        )

        # Check if we have questions
        available = self.engine.get_question_count(topic=topic, difficulty=difficulty)
        if available == 0:
            self.notify(
                "No questions match the selected filters",
                severity="error",
            )
            return

        # Start quiz
        from .mode3_quiz import Mode3QuizScreen

        self.app.push_screen(
            Mode3QuizScreen(
                topic=topic,
                difficulty=difficulty,
                question_count=min(self.selected_count, available),
            )
        )
