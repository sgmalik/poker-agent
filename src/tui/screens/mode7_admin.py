"""Mode 7: Admin - Dynamic Table Viewer."""

from typing import Any, Dict, List, Optional, TypedDict

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Select, DataTable
from textual.binding import Binding

from ...database.service import (
    get_quiz_attempts,
    get_quiz_sessions_list,
    get_poker_sessions,
    get_hand_histories,
    delete_quiz_attempt,
    delete_quiz_session,
    delete_poker_session,
    delete_hand_history,
    get_admin_stats,
)


class TableConfigEntry(TypedDict):
    """Type definition for table configuration entries."""

    title: str
    columns: List[tuple[str, str, int]]
    filters: List[str]


# Table configuration - defines columns and data mapping for each table
TABLE_CONFIG: Dict[str, TableConfigEntry] = {
    "quiz_attempts": {
        "title": "Quiz Attempts",
        "columns": [
            ("ID", "id", 6),
            ("Date", "created_at", 12),
            ("Question", "question_id", 12),
            ("Topic", "topic", 12),
            ("Difficulty", "difficulty", 12),
            ("Your Answer", "user_answer", 18),
            ("Correct Answer", "correct_answer", 18),
            ("Result", "is_correct", 8),
            ("Time", "time_taken", 6),
            ("Scenario", "scenario", 30),
        ],
        "filters": ["topic", "difficulty", "result"],
    },
    "quiz_sessions": {
        "title": "Quiz Sessions",
        "columns": [
            ("ID", "id", 6),
            ("Date", "created_at", 12),
            ("Topic", "topic", 14),
            ("Difficulty", "difficulty", 12),
            ("Total Q's", "total_questions", 10),
            ("Attempted", "questions_attempted", 10),
            ("Correct", "correct_answers", 10),
            ("Accuracy", "percentage", 10),
            ("Time", "time_total", 8),
        ],
        "filters": ["topic", "difficulty"],
    },
    "poker_sessions": {
        "title": "Poker Sessions",
        "columns": [
            ("ID", "id", 6),
            ("Date", "date", 12),
            ("Stake", "stake_level", 10),
            ("Buy-in", "buy_in", 10),
            ("Cash-out", "cash_out", 10),
            ("Profit", "profit_loss", 10),
            ("Duration", "duration_minutes", 10),
            ("Hands", "hands_played", 8),
            ("$/hr", "hourly_rate", 10),
            ("BB/hr", "bb_per_hour", 10),
            ("Location", "location", 15),
            ("Game", "game_type", 10),
            ("Notes", "notes", 30),
        ],
        "filters": ["stake"],
    },
    "hand_histories": {
        "title": "Hand Histories",
        "columns": [
            ("ID", "id", 6),
            ("Date", "created_at", 12),
            ("Hand", "hero_hand", 10),
            ("Position", "position", 8),
            ("Board", "board", 18),
            ("Result", "result", 8),
            ("Stake", "stake_level", 10),
            ("Pot", "pot_size", 10),
            ("Tags", "tags", 20),
            ("Action", "action_summary", 30),
            ("Notes", "notes", 30),
            ("Hand Text", "hand_text", 40),
        ],
        "filters": ["position", "result"],
    },
}

TOPIC_OPTIONS = [
    ("All", "all"),
    ("preflop", "preflop"),
    ("postflop", "postflop"),
    ("ranges", "ranges"),
    ("pot_odds", "pot_odds"),
    ("hand_strength", "hand_strength"),
    ("position", "position"),
    ("game_theory", "game_theory"),
]

DIFFICULTY_OPTIONS = [
    ("All", "all"),
    ("beginner", "beginner"),
    ("intermediate", "intermediate"),
    ("advanced", "advanced"),
    ("elite", "elite"),
]

RESULT_OPTIONS = [
    ("All", "all"),
    ("Correct", "correct"),
    ("Incorrect", "incorrect"),
]

POSITION_OPTIONS = [
    ("All", "all"),
    ("BTN", "BTN"),
    ("CO", "CO"),
    ("HJ", "HJ"),
    ("MP", "MP"),
    ("UTG", "UTG"),
    ("SB", "SB"),
    ("BB", "BB"),
]

HAND_RESULT_OPTIONS = [
    ("All", "all"),
    ("Won", "won"),
    ("Lost", "lost"),
]


class Mode7AdminScreen(Screen):
    """Dynamic admin table viewer screen."""

    CSS = """
    Mode7AdminScreen {
        align: center middle;
    }

    #admin_container {
        width: 98%;
        height: 95%;
        border: solid $warning;
        background: $surface;
        padding: 1;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        color: $warning;
        text-style: bold;
    }

    #table_selector_row {
        height: 3;
        width: 100%;
        padding: 0 1;
        margin-bottom: 1;
    }

    #table_selector_row Select {
        width: 30;
        margin-right: 2;
    }

    #table_selector_row Static {
        width: auto;
        content-align: left middle;
        padding-right: 1;
    }

    #stats_display {
        width: auto;
        padding-left: 2;
        color: $text-muted;
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

    #table_container {
        height: 1fr;
        width: 100%;
        margin-top: 1;
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
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("d", "delete_selected", "Delete", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the screen."""
        super().__init__()
        self.current_table: str = "quiz_attempts"
        self.data: List[Dict[str, Any]] = []
        self._loading: bool = False
        # Filter states
        self.filter_topic: Optional[str] = None
        self.filter_difficulty: Optional[str] = None
        self.filter_result: Optional[str] = None
        self.filter_stake: Optional[str] = None
        self.filter_position: Optional[str] = None
        self.filter_hand_result: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="admin_container"):
            yield Static(
                "[bold yellow]Admin Mode - Database Viewer[/bold yellow]", id="title"
            )

            # Table selector row
            with Horizontal(id="table_selector_row"):
                yield Static("Table:")
                yield Select(
                    [
                        ("Quiz Attempts", "quiz_attempts"),
                        ("Quiz Sessions", "quiz_sessions"),
                        ("Poker Sessions", "poker_sessions"),
                        ("Hand Histories", "hand_histories"),
                    ],
                    id="table_select",
                    value="quiz_attempts",
                )
                yield Static("", id="stats_display")

            # Dynamic filter row
            with Horizontal(id="filter_row"):
                yield Static("Filter:", id="filter_label")
                yield Select(TOPIC_OPTIONS, id="filter1", value="all")
                yield Select(DIFFICULTY_OPTIONS, id="filter2", value="all")
                yield Select(RESULT_OPTIONS, id="filter3", value="all")

            # Table
            with Container(id="table_container"):
                yield DataTable(id="table", zebra_stripes=True, cursor_type="row")

            # Summary row
            with Horizontal(id="summary_row"):
                yield Static("", id="summary_1", classes="summary_stat")
                yield Static("", id="summary_2", classes="summary_stat")
                yield Static("", id="summary_3", classes="summary_stat")
                yield Static("", id="summary_4", classes="summary_stat")

            # Button row
            with Horizontal(id="button_row"):
                yield Button("Refresh", id="refresh_btn", variant="default")
                yield Button("Delete Selected", id="delete_btn", variant="error")
                yield Button("Back", id="back_btn", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when mounted."""
        self._setup_table_for_current()
        self._update_stats_display()

    def on_screen_resume(self) -> None:
        """Refresh when returning to screen."""
        self._load_data()
        self._update_stats_display()

    def _update_stats_display(self) -> None:
        """Update the stats display."""
        try:
            stats = get_admin_stats()
            stats_widget = self.query_one("#stats_display", Static)
            stats_widget.update(
                f"[dim]Records: QA={stats['quiz_attempts']} | "
                f"QS={stats['quiz_sessions']} | "
                f"PS={stats['poker_sessions']} | "
                f"HH={stats['hand_histories']}[/dim]"
            )
        except Exception:
            pass

    def _setup_table_for_current(self) -> None:
        """Set up the table columns and filters for current table selection."""
        config = TABLE_CONFIG[self.current_table]
        table = self.query_one("#table", DataTable)

        # Clear and set up columns
        table.clear(columns=True)
        for col_name, col_key, col_width in config["columns"]:
            table.add_column(col_name, key=col_key, width=col_width)

        # Set up filters based on table type
        self._setup_filters(config["filters"])

        # Load data
        self._load_data()

    def _setup_filters(self, filter_types: List[str]) -> None:
        """Configure filter dropdowns based on table type."""
        filter1 = self.query_one("#filter1", Select)
        filter2 = self.query_one("#filter2", Select)
        filter3 = self.query_one("#filter3", Select)

        # Reset filter values
        self.filter_topic = None
        self.filter_difficulty = None
        self.filter_result = None
        self.filter_stake = None
        self.filter_position = None
        self.filter_hand_result = None

        # Configure based on table type
        if self.current_table == "quiz_attempts":
            filter1.set_options(TOPIC_OPTIONS)
            filter1.value = "all"
            filter1.display = True
            filter2.set_options(DIFFICULTY_OPTIONS)
            filter2.value = "all"
            filter2.display = True
            filter3.set_options(RESULT_OPTIONS)
            filter3.value = "all"
            filter3.display = True

        elif self.current_table == "quiz_sessions":
            filter1.set_options(TOPIC_OPTIONS)
            filter1.value = "all"
            filter1.display = True
            filter2.set_options(DIFFICULTY_OPTIONS)
            filter2.value = "all"
            filter2.display = True
            filter3.display = False

        elif self.current_table == "poker_sessions":
            # Get unique stakes from data
            filter1.set_options([("All Stakes", "all")])
            filter1.value = "all"
            filter1.display = True
            filter2.display = False
            filter3.display = False

        elif self.current_table == "hand_histories":
            filter1.set_options(POSITION_OPTIONS)
            filter1.value = "all"
            filter1.display = True
            filter2.set_options(HAND_RESULT_OPTIONS)
            filter2.value = "all"
            filter2.display = True
            filter3.display = False

    def _load_data(self) -> None:
        """Load data based on current table and filters."""
        if self._loading:
            return
        self._loading = True

        try:
            if self.current_table == "quiz_attempts":
                self.data = get_quiz_attempts(
                    topic=self.filter_topic,
                    difficulty=self.filter_difficulty,
                    is_correct=self.filter_result,
                    limit=500,
                )
            elif self.current_table == "quiz_sessions":
                self.data = get_quiz_sessions_list(
                    topic=self.filter_topic,
                    difficulty=self.filter_difficulty,
                    limit=500,
                )
            elif self.current_table == "poker_sessions":
                self.data = get_poker_sessions(
                    stake_level=self.filter_stake,
                    days=0,
                    limit=500,
                )
            elif self.current_table == "hand_histories":
                self.data = get_hand_histories(
                    position=self.filter_position,
                    result=self.filter_hand_result,
                    days=0,
                    limit=500,
                )

            self._populate_table()
            self._update_summary()
        finally:
            self._loading = False

    def _populate_table(self) -> None:
        """Populate the data table with current data."""
        table = self.query_one("#table", DataTable)
        config = TABLE_CONFIG[self.current_table]
        table.clear()

        for row in self.data:
            row_values = []
            for col_name, col_key, col_width in config["columns"]:
                value = row.get(col_key, "")
                formatted = self._format_value(col_key, value, row)
                row_values.append(formatted)

            row_id = row.get("id", "")
            table.add_row(*row_values, key=str(row_id))

    def _format_value(self, key: str, value: Any, row: Dict[str, Any]) -> str:
        """Format a value for display based on its key."""
        if value is None:
            return "-"

        # Date formatting
        if key in ("created_at", "date"):
            return str(value)[:10] if value else "-"

        # Boolean/result formatting
        if key == "is_correct":
            return "[green]Yes[/green]" if value else "[red]No[/red]"

        # Score formatting for quiz sessions
        if key == "score":
            correct = row.get("correct_answers", 0)
            total = row.get("total_questions", 0)
            return f"{correct}/{total}"

        # Percentage formatting
        if key == "percentage":
            return f"{value:.1f}%"

        # Time formatting
        if key == "time_taken":
            return f"{value}s" if value else "-"

        if key == "time_total":
            if value:
                mins = value // 60
                secs = value % 60
                return f"{mins}m {secs}s" if mins else f"{secs}s"
            return "-"

        # Duration formatting
        if key == "duration_minutes":
            if value:
                hours = value // 60
                mins = value % 60
                return f"{hours}h {mins}m" if hours else f"{mins}m"
            return "-"

        # Money formatting
        if key in ("buy_in", "cash_out", "pot_size"):
            return f"${value:,.2f}" if value else "-"

        if key == "profit_loss":
            if value >= 0:
                return f"[green]+${value:,.2f}[/green]"
            else:
                return f"[red]-${abs(value):,.2f}[/red]"

        if key == "hourly_rate":
            if value is None:
                return "-"
            if value >= 0:
                return f"[green]+${value:,.0f}[/green]"
            else:
                return f"[red]-${abs(value):,.0f}[/red]"

        # Result formatting for hands
        if key == "result" and self.current_table == "hand_histories":
            if value == "won":
                return "[green]Won[/green]"
            elif value == "lost":
                return "[red]Lost[/red]"
            return str(value)

        # Truncate long strings
        str_value = str(value)
        max_len = 18
        if len(str_value) > max_len:
            return str_value[: max_len - 2] + ".."

        return str_value

    def _update_summary(self) -> None:
        """Update summary statistics based on current table."""
        total = len(self.data)

        if self.current_table == "quiz_attempts":
            correct = sum(1 for a in self.data if a.get("is_correct"))
            incorrect = total - correct
            accuracy = (correct / total * 100) if total > 0 else 0
            self.query_one("#summary_1", Static).update(f"Total: {total}")
            self.query_one("#summary_2", Static).update(
                f"Correct: [green]{correct}[/green]"
            )
            self.query_one("#summary_3", Static).update(
                f"Incorrect: [red]{incorrect}[/red]"
            )
            self.query_one("#summary_4", Static).update(f"Accuracy: {accuracy:.1f}%")

        elif self.current_table == "quiz_sessions":
            total_q = sum(s.get("total_questions", 0) for s in self.data)
            total_correct = sum(s.get("correct_answers", 0) for s in self.data)
            avg_acc = (total_correct / total_q * 100) if total_q > 0 else 0
            self.query_one("#summary_1", Static).update(f"Sessions: {total}")
            self.query_one("#summary_2", Static).update(f"Questions: {total_q}")
            self.query_one("#summary_3", Static).update(f"Correct: {total_correct}")
            self.query_one("#summary_4", Static).update(f"Avg Accuracy: {avg_acc:.1f}%")

        elif self.current_table == "poker_sessions":
            total_profit = sum(s.get("profit_loss", 0) for s in self.data)
            total_mins = sum(s.get("duration_minutes", 0) or 0 for s in self.data)
            hours = total_mins / 60
            hourly = total_profit / hours if hours > 0 else 0
            profit_str = (
                f"[green]+${total_profit:,.2f}[/green]"
                if total_profit >= 0
                else f"[red]-${abs(total_profit):,.2f}[/red]"
            )
            self.query_one("#summary_1", Static).update(f"Sessions: {total}")
            self.query_one("#summary_2", Static).update(f"Profit: {profit_str}")
            self.query_one("#summary_3", Static).update(f"Hours: {hours:.1f}")
            self.query_one("#summary_4", Static).update(f"$/hr: ${hourly:,.2f}")

        elif self.current_table == "hand_histories":
            won = sum(1 for h in self.data if h.get("result") == "won")
            lost = sum(1 for h in self.data if h.get("result") == "lost")
            win_rate = (won / total * 100) if total > 0 else 0
            self.query_one("#summary_1", Static).update(f"Total: {total}")
            self.query_one("#summary_2", Static).update(f"Won: [green]{won}[/green]")
            self.query_one("#summary_3", Static).update(f"Lost: [red]{lost}[/red]")
            self.query_one("#summary_4", Static).update(f"Win Rate: {win_rate:.1f}%")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        select_id = event.select.id
        value = str(event.value) if event.value else None

        if select_id == "table_select":
            self.current_table = value or "quiz_attempts"
            self._setup_table_for_current()
            return

        # Handle filter changes based on current table
        if self.current_table == "quiz_attempts":
            if select_id == "filter1":
                self.filter_topic = value if value != "all" else None
            elif select_id == "filter2":
                self.filter_difficulty = value if value != "all" else None
            elif select_id == "filter3":
                self.filter_result = value if value != "all" else None

        elif self.current_table == "quiz_sessions":
            if select_id == "filter1":
                self.filter_topic = value if value != "all" else None
            elif select_id == "filter2":
                self.filter_difficulty = value if value != "all" else None

        elif self.current_table == "poker_sessions":
            if select_id == "filter1":
                self.filter_stake = value if value != "all" else None

        elif self.current_table == "hand_histories":
            if select_id == "filter1":
                self.filter_position = value if value != "all" else None
            elif select_id == "filter2":
                self.filter_hand_result = value if value != "all" else None

        self._load_data()

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
        """Return to main menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the data."""
        self._load_data()
        self._update_stats_display()
        self.notify("Data refreshed")

    def action_delete_selected(self) -> None:
        """Delete the selected row."""
        table = self.query_one("#table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No row selected", severity="warning")
            return

        cursor_row = table.cursor_row
        if cursor_row >= len(table.rows):
            self.notify("No row selected", severity="warning")
            return

        row_key = list(table.rows.keys())[cursor_row]
        row_id = int(str(row_key.value))

        # Call appropriate delete function
        success = False
        if self.current_table == "quiz_attempts":
            success = delete_quiz_attempt(row_id)
        elif self.current_table == "quiz_sessions":
            success = delete_quiz_session(row_id)
        elif self.current_table == "poker_sessions":
            success = delete_poker_session(row_id)
        elif self.current_table == "hand_histories":
            success = delete_hand_history(row_id)

        if success:
            self.notify("Record deleted")
            self._load_data()
            self._update_stats_display()
        else:
            self.notify("Failed to delete record", severity="error")
