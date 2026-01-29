"""Mode 4: Session Tracker - Menu Screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...database.service import get_session_stats


class Mode4MenuScreen(Screen):
    """Session tracker main menu screen."""

    CSS = """
    Mode4MenuScreen {
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
        Binding("n", "new_session", "New Session", show=True),
        Binding("h", "history", "History", show=True),
        Binding("s", "stats", "Stats", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="menu_container"):
            yield Static("[bold cyan]Session Tracker[/bold cyan]", id="title")
            yield Static("Track your poker sessions and bankroll", id="subtitle")

            # Quick stats panel
            with Container(id="quick_stats"):
                yield self._create_quick_stats()

            # Menu buttons
            yield Button("Log New Session", id="new_session_btn", variant="primary")
            yield Button("Session History", id="history_btn", variant="default")
            yield Button("Stats & Graphs", id="stats_btn", variant="default")
            yield Button("Back to Menu", id="back_btn", variant="default")

            yield Static(
                "[dim]Press N for new session, H for history, S for stats[/dim]",
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
            # Get the Static widget inside the container
            stats_widget = quick_stats.query_one(Static)
            stats_widget.update(self._get_quick_stats_text())
        except Exception:
            pass  # Screen may not be fully composed yet

    def _get_quick_stats_text(self) -> str:
        """Get formatted quick stats text."""
        stats = get_session_stats(days=30)

        total_sessions = stats.get("total_sessions", 0)
        total_profit = stats.get("total_profit", 0.0)
        hourly_rate = stats.get("hourly_rate", 0.0)
        win_rate = stats.get("win_rate", 0.0)

        # Format profit with color
        if total_profit >= 0:
            profit_text = f"[green]+${total_profit:,.2f}[/green]"
        else:
            profit_text = f"[red]-${abs(total_profit):,.2f}[/red]"

        # Format hourly rate
        if hourly_rate >= 0:
            hourly_text = f"[green]+${hourly_rate:,.2f}/hr[/green]"
        else:
            hourly_text = f"[red]-${abs(hourly_rate):,.2f}/hr[/red]"

        return (
            f"[bold]Last 30 Days[/bold]\n"
            f"Sessions: {total_sessions}  |  "
            f"Profit: {profit_text}  |  "
            f"Rate: {hourly_text}\n"
            f"Win Rate: {win_rate:.0f}%"
        )

    def _create_quick_stats(self) -> Static:
        """Create quick stats summary."""
        return Static(self._get_quick_stats_text(), id="stats_text")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "new_session_btn":
            self.action_new_session()
        elif button_id == "history_btn":
            self.action_history()
        elif button_id == "stats_btn":
            self.action_stats()

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()

    def action_new_session(self) -> None:
        """Open new session entry form."""
        from .mode4_entry import Mode4EntryScreen

        self.app.push_screen(Mode4EntryScreen())

    def action_history(self) -> None:
        """Open session history."""
        from .mode4_history import Mode4HistoryScreen

        self.app.push_screen(Mode4HistoryScreen())

    def action_stats(self) -> None:
        """Open stats and graphs."""
        from .mode4_stats import Mode4StatsScreen

        self.app.push_screen(Mode4StatsScreen())
