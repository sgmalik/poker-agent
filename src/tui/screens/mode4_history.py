"""Mode 4: Session Tracker - History Screen."""

from typing import Any, Dict, List
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Select, DataTable
from textual.binding import Binding

from ...database.service import get_poker_sessions, delete_poker_session


class Mode4HistoryScreen(Screen):
    """Session history screen with table view."""

    CSS = """
    Mode4HistoryScreen {
        align: center middle;
    }

    #history_container {
        width: 95%;
        height: 90%;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        color: $accent;
        text-style: bold;
    }

    #filter_row {
        height: 3;
        width: 100%;
        padding: 0 1;
    }

    #filter_row Select {
        width: 20;
        margin-right: 1;
    }

    #filter_row Static {
        width: auto;
        content-align: left middle;
        padding-right: 1;
    }

    #sessions_table {
        height: 1fr;
        width: 100%;
    }

    DataTable {
        height: 100%;
    }

    #summary_row {
        height: auto;
        width: 100%;
        padding: 1;
        background: $surface-lighten-1;
    }

    .summary_stat {
        width: 1fr;
        text-align: center;
    }

    #button_row {
        height: 3;
        width: 100%;
        align: center middle;
    }

    #button_row Button {
        margin: 0 1;
        width: 18;
    }

    .positive {
        color: $success;
    }

    .negative {
        color: $error;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("d", "delete_selected", "Delete", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the history screen."""
        super().__init__()
        self.sessions: List[Dict[str, Any]] = []
        self.selected_days: int = 0  # Default to all time
        self.selected_stake: str | None = None
        self._loading: bool = False  # Guard against recursive loading
        self._stakes_loaded: bool = False  # Only load stake options once

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="history_container"):
            yield Static("[bold cyan]Session History[/bold cyan]", id="title")

            # Filter row
            with Horizontal(id="filter_row"):
                yield Static("Time Range:")
                yield Select(
                    [
                        ("Last 7 days", "7"),
                        ("Last 30 days", "30"),
                        ("Last 90 days", "90"),
                        ("All time", "0"),
                    ],
                    id="days_select",
                    value="0",  # Default to all time
                )
                yield Static("Stake:")
                yield Select(
                    [("All stakes", "all")],
                    id="stake_filter",
                    value="all",
                )

            # Sessions table
            with Container(id="sessions_table"):
                yield DataTable(id="table", zebra_stripes=True, cursor_type="row")

            # Summary row
            with Horizontal(id="summary_row"):
                yield Static("", id="summary_sessions", classes="summary_stat")
                yield Static("", id="summary_profit", classes="summary_stat")
                yield Static("", id="summary_hours", classes="summary_stat")
                yield Static("", id="summary_rate", classes="summary_stat")

            # Button row
            with Horizontal(id="button_row"):
                yield Button("Refresh", id="refresh_btn", variant="default")
                yield Button("Delete Selected", id="delete_btn", variant="error")
                yield Button("Back", id="back_btn", variant="default")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the table when mounted."""
        table = self.query_one("#table", DataTable)

        # Add columns
        table.add_column("Date", key="date", width=12)
        table.add_column("Stake", key="stake", width=10)
        table.add_column("Buy-in", key="buyin", width=12)
        table.add_column("Cash-out", key="cashout", width=12)
        table.add_column("Profit", key="profit", width=12)
        table.add_column("Duration", key="duration", width=10)
        table.add_column("$/hr", key="hourly", width=10)
        table.add_column("Location", key="location", width=15)

        # Load initial data
        self._load_sessions()

    def on_screen_resume(self) -> None:
        """Called when returning to this screen - refresh data."""
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load sessions from database."""
        # Guard against recursive loading (triggered by set_options)
        if self._loading:
            return
        self._loading = True

        try:
            self.sessions = get_poker_sessions(
                days=self.selected_days,
                stake_level=self.selected_stake,
                limit=100,
            )

            # Update stake filter options only once to avoid event loops
            if not self._stakes_loaded:
                self._stakes_loaded = True
                stakes = set()
                all_sessions = get_poker_sessions(days=0, limit=500)
                for s in all_sessions:
                    if s.get("stake_level"):
                        stakes.add(s["stake_level"])

                stake_select = self.query_one("#stake_filter", Select)
                stake_options = [("All stakes", "all")] + [
                    (s, s) for s in sorted(stakes)
                ]
                stake_select.set_options(stake_options)

            # Populate table
            self._populate_table()
            self._update_summary()
        finally:
            self._loading = False

    def _populate_table(self) -> None:
        """Populate the data table with sessions."""
        table = self.query_one("#table", DataTable)
        table.clear()

        for session in self.sessions:
            date_str = session.get("date", "")[:10] if session.get("date") else ""
            stake = session.get("stake_level", "")
            buy_in = session.get("buy_in", 0)
            cash_out = session.get("cash_out", 0)
            profit = session.get("profit_loss", 0)
            duration = session.get("duration_minutes")
            hourly = session.get("hourly_rate")
            location = session.get("location", "") or ""

            # Format duration
            if duration:
                hours = duration // 60
                mins = duration % 60
                duration_str = f"{hours}h {mins}m" if hours else f"{mins}m"
            else:
                duration_str = "-"

            # Format profit with color
            if profit >= 0:
                profit_str = f"+${profit:,.2f}"
            else:
                profit_str = f"-${abs(profit):,.2f}"

            # Format hourly rate
            if hourly is not None:
                if hourly >= 0:
                    hourly_str = f"+${hourly:,.0f}"
                else:
                    hourly_str = f"-${abs(hourly):,.0f}"
            else:
                hourly_str = "-"

            table.add_row(
                date_str,
                stake,
                f"${buy_in:,.2f}",
                f"${cash_out:,.2f}",
                profit_str,
                duration_str,
                hourly_str,
                location[:15],
                key=str(session.get("id", "")),
            )

    def _update_summary(self) -> None:
        """Update the summary statistics."""
        if not self.sessions:
            self.query_one("#summary_sessions", Static).update("Sessions: 0")
            self.query_one("#summary_profit", Static).update("Total: $0.00")
            self.query_one("#summary_hours", Static).update("Hours: 0")
            self.query_one("#summary_rate", Static).update("Rate: $0/hr")
            return

        total_sessions = len(self.sessions)
        total_profit = sum(s.get("profit_loss", 0) for s in self.sessions)
        total_minutes = sum(s.get("duration_minutes", 0) or 0 for s in self.sessions)
        total_hours = total_minutes / 60

        hourly_rate = total_profit / total_hours if total_hours > 0 else 0

        # Update displays
        self.query_one("#summary_sessions", Static).update(
            f"Sessions: {total_sessions}"
        )

        if total_profit >= 0:
            self.query_one("#summary_profit", Static).update(
                f"Total: [green]+${total_profit:,.2f}[/green]"
            )
        else:
            self.query_one("#summary_profit", Static).update(
                f"Total: [red]-${abs(total_profit):,.2f}[/red]"
            )

        self.query_one("#summary_hours", Static).update(f"Hours: {total_hours:,.1f}")

        if hourly_rate >= 0:
            self.query_one("#summary_rate", Static).update(
                f"Rate: [green]+${hourly_rate:,.2f}/hr[/green]"
            )
        else:
            self.query_one("#summary_rate", Static).update(
                f"Rate: [red]-${float(abs(hourly_rate)):,.2f}/hr[/red]"
            )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter changes."""
        select_id = event.select.id
        value = str(event.value) if event.value else None

        if select_id == "days_select":
            self.selected_days = int(value) if value else 30
            self._load_sessions()
        elif select_id == "stake_filter":
            self.selected_stake = value if value != "all" else None
            self._load_sessions()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "refresh_btn":
            self.action_refresh()
        elif button_id == "delete_btn":
            self.action_delete_selected()

    def action_back(self) -> None:
        """Return to session tracker menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the session list."""
        self._load_sessions()
        self.notify("Sessions refreshed")

    def action_delete_selected(self) -> None:
        """Delete the selected session."""
        table = self.query_one("#table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No session selected", severity="warning")
            return

        # Get the session ID from the row key
        row_key = table.get_row_at(table.cursor_row)
        if row_key:
            # The row key is the session ID
            cursor_row = table.cursor_row
            session_key = list(table.rows.keys())[cursor_row]
            session_id = int(str(session_key.value))

            if delete_poker_session(session_id):
                self.notify("Session deleted")
                self._load_sessions()
            else:
                self.notify("Failed to delete session", severity="error")
