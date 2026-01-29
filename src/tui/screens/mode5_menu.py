"""Mode 5: Hand History Manager - Menu Screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...database.service import get_hand_history_stats


class Mode5MenuScreen(Screen):
    """Hand history manager main menu screen."""

    CSS = """
    Mode5MenuScreen {
        align: center middle;
    }

    #menu_container {
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
        padding: 0 0 1 0;
        color: $text-muted;
    }

    #quick_stats {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $primary-lighten-2;
        background: $surface-lighten-1;
    }

    .stat_row {
        width: 100%;
        height: auto;
    }

    .stat_label {
        width: 1fr;
        color: $text-muted;
    }

    .stat_value {
        width: auto;
        text-style: bold;
    }

    .stat_value.positive {
        color: $success;
    }

    .stat_value.negative {
        color: $error;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    .help_text {
        color: $text-muted;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("n", "new_hand", "New Hand", show=True),
        Binding("h", "history", "History", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="menu_container"):
            yield Static("[bold cyan]Hand History Manager[/bold cyan]", id="title")
            yield Static("Track and analyze your notable hands", id="subtitle")

            # Quick stats panel
            with Container(id="quick_stats"):
                yield self._create_quick_stats()

            # Menu buttons
            yield Button("Log New Hand", id="new_hand_btn", variant="primary")
            yield Button("View History", id="history_btn", variant="default")
            yield Button("Back to Menu", id="back_btn", variant="default")

            yield Static(
                "[dim]Press N for new hand, H for history[/dim]",
                classes="help_text",
            )

        yield Footer()

    def on_screen_resume(self) -> None:
        """Called when returning to this screen - refresh stats."""
        self._refresh_quick_stats()

    def _refresh_quick_stats(self) -> None:
        """Refresh the quick stats display."""
        try:
            quick_stats = self.query_one("#quick_stats", Container)
            stats_widget = quick_stats.query_one(Static)
            stats_widget.update(self._get_quick_stats_text())
        except Exception:
            pass  # Screen may not be fully composed yet

    def _get_quick_stats_text(self) -> str:
        """Get formatted quick stats text."""
        stats = get_hand_history_stats(days=30)

        total_hands = stats.get("total_hands", 0)
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        win_rate = stats.get("win_rate", 0.0)

        # Format win rate with color
        if win_rate >= 50:
            win_rate_text = f"[green]{win_rate:.1f}%[/green]"
        else:
            win_rate_text = f"[red]{win_rate:.1f}%[/red]"

        common_tags = stats.get("common_tags", [])[:3]
        tags_text = ", ".join(common_tags) if common_tags else "None"

        return (
            f"[bold]Last 30 Days[/bold]\n"
            f"Hands: {total_hands}  |  "
            f"Won: [green]{wins}[/green]  |  "
            f"Lost: [red]{losses}[/red]  |  "
            f"Win Rate: {win_rate_text}\n"
            f"Top Tags: {tags_text}"
        )

    def _create_quick_stats(self) -> Static:
        """Create quick stats summary."""
        return Static(self._get_quick_stats_text(), id="stats_text")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "new_hand_btn":
            self.action_new_hand()
        elif button_id == "history_btn":
            self.action_history()

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()

    def action_new_hand(self) -> None:
        """Open new hand entry form."""
        from .mode5_entry import Mode5EntryScreen

        self.app.push_screen(Mode5EntryScreen())

    def action_history(self) -> None:
        """Open hand history."""
        from .mode5_history import Mode5HistoryScreen

        self.app.push_screen(Mode5HistoryScreen())
