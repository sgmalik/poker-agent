"""Main TUI application for Poker Coach."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding


class WelcomeScreen(Static):
    """Welcome screen with mode selection menu."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold cyan]🃏 Poker Coach[/bold cyan]", id="title")
        yield Static(
            "Select a mode to get started:",
            id="subtitle",
        )
        yield Button("Hand Evaluator & Spot Analyzer", id="mode_1", variant="primary")
        yield Button("Range Tools", id="mode_2", variant="default")
        yield Button("Quiz System", id="mode_3", variant="default")
        yield Button("Session Tracker", id="mode_4", variant="default")
        yield Button("Hand History Manager", id="mode_5", variant="default")
        yield Button("AI Agent Coach", id="mode_6", variant="success")
        yield Button("Quit", id="quit", variant="error")


class PokerCoachApp(App):
    """A Textual app for poker coaching and study."""

    CSS = """
    Container {
        align: center middle;
        width: 100%;
        height: 100%;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        margin-bottom: 1;
    }

    #subtitle {
        text-align: center;
        width: 100%;
        padding: 0 0 2 0;
        color: $text-muted;
    }

    WelcomeScreen {
        width: 60;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("1", "mode_1", "Hand Eval", show=True),
        Binding("2", "mode_2", "Ranges", show=True),
        Binding("3", "mode_3", "Quiz", show=True),
        Binding("4", "mode_4", "Sessions", show=True),
        Binding("5", "mode_5", "Hands", show=True),
        Binding("6", "mode_6", "Agent", show=True),
    ]

    TITLE = "Poker Coach"
    SUB_TITLE = "Your personal poker study companion"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(WelcomeScreen())
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "quit":
            self.exit()
        elif button_id == "mode_1":
            self.action_mode_1()
        elif button_id == "mode_2":
            self.action_mode_2()
        elif button_id == "mode_3":
            self.action_mode_3()
        elif button_id == "mode_4":
            self.action_mode_4()
        elif button_id == "mode_5":
            self.action_mode_5()
        elif button_id == "mode_6":
            self.action_mode_6()

    def action_mode_1(self) -> None:
        """Open Mode 1: Hand Evaluator & Spot Analyzer."""
        # TODO: Implement Mode 1 screen
        self.notify("Mode 1: Hand Evaluator (Coming soon!)")

    def action_mode_2(self) -> None:
        """Open Mode 2: Range Tools."""
        self.notify("Mode 2: Range Tools (Coming soon!)")

    def action_mode_3(self) -> None:
        """Open Mode 3: Quiz System."""
        self.notify("Mode 3: Quiz System (Coming soon!)")

    def action_mode_4(self) -> None:
        """Open Mode 4: Session Tracker."""
        self.notify("Mode 4: Session Tracker (Coming soon!)")

    def action_mode_5(self) -> None:
        """Open Mode 5: Hand History Manager."""
        self.notify("Mode 5: Hand History Manager (Coming soon!)")

    def action_mode_6(self) -> None:
        """Open Mode 6: AI Agent Coach."""
        self.notify("Mode 6: AI Agent Coach (Coming soon!)")


def run_app():
    """Run the Poker Coach TUI application."""
    app = PokerCoachApp()
    app.run()


if __name__ == "__main__":
    run_app()
