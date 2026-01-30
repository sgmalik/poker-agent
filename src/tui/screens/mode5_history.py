"""Mode 5: Hand History Manager - History Screen."""

from typing import Any, Dict, List, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Select, DataTable
from textual.binding import Binding

from ...database.service import get_hand_histories, delete_hand_history
from ...core.hand_history import format_cards, POSITIONS, RESULTS


class Mode5HistoryScreen(Screen):
    """Hand history screen with searchable table view."""

    CSS = """
    Mode5HistoryScreen {
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
        width: 18;
        margin-right: 1;
    }

    #filter_row Static {
        width: auto;
        content-align: left middle;
        padding-right: 1;
    }

    #hands_table {
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
        Binding("enter", "view_detail", "View", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the history screen."""
        super().__init__()
        self.hands: List[Dict[str, Any]] = []
        self.selected_days: int = 0  # Default to all time
        self.selected_result: Optional[str] = None
        self.selected_position: Optional[str] = None
        self.selected_tag: Optional[str] = None
        self._loading: bool = False
        self._filters_loaded: bool = False

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="history_container"):
            yield Static("[bold cyan]Hand History[/bold cyan]", id="title")

            # Filter row
            with Horizontal(id="filter_row"):
                yield Static("Time:")
                yield Select(
                    [
                        ("Last 7 days", "7"),
                        ("Last 30 days", "30"),
                        ("Last 90 days", "90"),
                        ("All time", "0"),
                    ],
                    id="days_select",
                    value="0",
                )
                yield Static("Result:")
                yield Select(
                    [("All", "all")] + [(r.capitalize(), r) for r in RESULTS],
                    id="result_filter",
                    value="all",
                )
                yield Static("Position:")
                yield Select(
                    [("All", "all")] + [(p, p) for p in POSITIONS],
                    id="position_filter",
                    value="all",
                )

            # Hands table
            with Container(id="hands_table"):
                yield DataTable(id="table", zebra_stripes=True, cursor_type="row")

            # Summary row
            with Horizontal(id="summary_row"):
                yield Static("", id="summary_hands", classes="summary_stat")
                yield Static("", id="summary_wins", classes="summary_stat")
                yield Static("", id="summary_losses", classes="summary_stat")
                yield Static("", id="summary_winrate", classes="summary_stat")

            # Button row
            with Horizontal(id="button_row"):
                yield Button("View Details", id="view_btn", variant="primary")
                yield Button("Refresh", id="refresh_btn", variant="default")
                yield Button("Delete", id="delete_btn", variant="error")
                yield Button("Back", id="back_btn", variant="default")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the table when mounted."""
        table = self.query_one("#table", DataTable)

        # Add columns
        table.add_column("Date", key="date", width=12)
        table.add_column("Hand", key="hand", width=10)
        table.add_column("Board", key="board", width=16)
        table.add_column("Pos", key="position", width=5)
        table.add_column("Result", key="result", width=7)
        table.add_column("Street", key="street", width=8)
        table.add_column("Stake", key="stake", width=10)
        table.add_column("Tags", key="tags", width=15)
        table.add_column("Notes", key="notes", width=18)

        # Load initial data
        self._load_hands()

    def on_screen_resume(self) -> None:
        """Called when returning to this screen - refresh data."""
        self._load_hands()

    def _load_hands(self) -> None:
        """Load hands from database."""
        if self._loading:
            return
        self._loading = True

        try:
            # Build filter parameters
            tags_filter = [self.selected_tag] if self.selected_tag else None

            self.hands = get_hand_histories(
                days=self.selected_days,
                result=self.selected_result,
                position=self.selected_position,
                tags=tags_filter,
                limit=100,
            )

            # Populate table
            self._populate_table()
            self._update_summary()
        finally:
            self._loading = False

    def _populate_table(self) -> None:
        """Populate the data table with hands."""
        table = self.query_one("#table", DataTable)
        table.clear()

        for hand in self.hands:
            date_str = hand.get("created_at", "")[:10] if hand.get("created_at") else ""
            hero_hand = format_cards(hand.get("hero_hand", ""))
            board = hand.get("board", "")
            board_display = format_cards(board)[:15] if board else "-"
            position = hand.get("position", "")
            result = hand.get("result", "")
            street = hand.get("street", "").capitalize()
            tags = hand.get("tags", [])
            tags_str = ", ".join(tags[:2]) if tags else "-"
            if len(tags) > 2:
                tags_str += "..."

            # Format result with color indicator
            if result == "won":
                result_display = "Won"
            elif result == "lost":
                result_display = "Lost"
            else:
                result_display = "Split"

            # Get stake and notes
            stake = hand.get("stake_level", "") or "-"
            notes = hand.get("notes", "") or ""
            notes_display = (
                notes[:16] + ".." if len(notes) > 18 else notes if notes else "-"
            )

            table.add_row(
                date_str,
                hero_hand,
                board_display,
                position,
                result_display,
                street,
                stake,
                tags_str,
                notes_display,
                key=str(hand.get("id", "")),
            )

    def _update_summary(self) -> None:
        """Update the summary statistics."""
        if not self.hands:
            self.query_one("#summary_hands", Static).update("Hands: 0")
            self.query_one("#summary_wins", Static).update("Wins: 0")
            self.query_one("#summary_losses", Static).update("Losses: 0")
            self.query_one("#summary_winrate", Static).update("Win Rate: 0%")
            return

        total_hands = len(self.hands)
        wins = sum(1 for h in self.hands if h.get("result") == "won")
        losses = sum(1 for h in self.hands if h.get("result") == "lost")
        win_rate = (wins / total_hands * 100) if total_hands > 0 else 0

        self.query_one("#summary_hands", Static).update(f"Hands: {total_hands}")
        self.query_one("#summary_wins", Static).update(f"Wins: [green]{wins}[/green]")
        self.query_one("#summary_losses", Static).update(f"Losses: [red]{losses}[/red]")

        if win_rate >= 50:
            self.query_one("#summary_winrate", Static).update(
                f"Win Rate: [green]{win_rate:.1f}%[/green]"
            )
        else:
            self.query_one("#summary_winrate", Static).update(
                f"Win Rate: [red]{win_rate:.1f}%[/red]"
            )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter changes."""
        select_id = event.select.id
        value = str(event.value) if event.value else None

        if select_id == "days_select":
            self.selected_days = int(value) if value else 0
            self._load_hands()
        elif select_id == "result_filter":
            self.selected_result = value if value != "all" else None
            self._load_hands()
        elif select_id == "position_filter":
            self.selected_position = value if value != "all" else None
            self._load_hands()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "refresh_btn":
            self.action_refresh()
        elif button_id == "delete_btn":
            self.action_delete_selected()
        elif button_id == "view_btn":
            self.action_view_detail()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle double-click on row to view details."""
        self.action_view_detail()

    def action_back(self) -> None:
        """Return to hand history menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the hand list."""
        self._load_hands()
        self.notify("Hands refreshed")

    def action_delete_selected(self) -> None:
        """Delete the selected hand."""
        table = self.query_one("#table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No hand selected", severity="warning")
            return

        # Get the hand ID from the row key
        cursor_row = table.cursor_row
        row_keys = list(table.rows.keys())
        if cursor_row < len(row_keys):
            hand_id = int(str(row_keys[cursor_row].value))

            if delete_hand_history(hand_id):
                self.notify("Hand deleted")
                self._load_hands()
            else:
                self.notify("Failed to delete hand", severity="error")

    def action_view_detail(self) -> None:
        """View details of selected hand."""
        table = self.query_one("#table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No hand selected", severity="warning")
            return

        # Get the hand ID from the row key
        cursor_row = table.cursor_row
        row_keys = list(table.rows.keys())
        if cursor_row < len(row_keys):
            hand_id = int(str(row_keys[cursor_row].value))

            from .mode5_detail import Mode5DetailScreen

            self.app.push_screen(Mode5DetailScreen(hand_id))
