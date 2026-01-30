"""Mode 7: Admin - Dynamic Detail View Screen."""

from typing import Any, Callable, Dict, List, Optional, TypedDict

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...database.service import (
    get_quiz_attempt_by_id,
    get_quiz_session_by_id,
    get_poker_session_by_id,
    get_hand_history_by_id,
    delete_quiz_attempt,
    delete_quiz_session,
    delete_poker_session,
    delete_hand_history,
)


class DetailFieldConfig(TypedDict):
    """Configuration for a detail field."""

    label: str
    key: str
    type: str  # "text", "date", "boolean", "money", "duration", "time", "percentage", "result", "long_text", "tags"


class DetailTableConfig(TypedDict):
    """Configuration for detail view of a table."""

    title: str
    fetch_func: Callable[[int], Optional[Dict[str, Any]]]
    delete_func: Callable[[int], bool]
    fields: List[DetailFieldConfig]
    highlight_field: Optional[str]  # Field to show prominently at top


# Detail view configuration for each table
# Fields should match the columns shown in TABLE_CONFIG in mode7_admin.py
DETAIL_CONFIG: Dict[str, DetailTableConfig] = {
    "quiz_attempts": {
        "title": "Quiz Attempt Details",
        "fetch_func": get_quiz_attempt_by_id,
        "delete_func": delete_quiz_attempt,
        "highlight_field": "is_correct",
        "fields": [
            {"label": "ID", "key": "id", "type": "text"},
            {"label": "Date", "key": "created_at", "type": "date"},
            {"label": "Question ID", "key": "question_id", "type": "text"},
            {"label": "Topic", "key": "topic", "type": "text"},
            {"label": "Difficulty", "key": "difficulty", "type": "text"},
            {"label": "Your Answer", "key": "user_answer", "type": "text"},
            {"label": "Correct Answer", "key": "correct_answer", "type": "text"},
            {"label": "Result", "key": "is_correct", "type": "boolean"},
            {"label": "Time Taken", "key": "time_taken", "type": "time"},
            {"label": "Scenario", "key": "scenario", "type": "long_text"},
        ],
    },
    "quiz_sessions": {
        "title": "Quiz Session Details",
        "fetch_func": get_quiz_session_by_id,
        "delete_func": delete_quiz_session,
        "highlight_field": "percentage",
        "fields": [
            {"label": "ID", "key": "id", "type": "text"},
            {"label": "Date", "key": "created_at", "type": "date"},
            {"label": "Topic", "key": "topic", "type": "text"},
            {"label": "Difficulty", "key": "difficulty", "type": "text"},
            {"label": "Total Questions", "key": "total_questions", "type": "text"},
            {"label": "Attempted", "key": "questions_attempted", "type": "text"},
            {"label": "Correct", "key": "correct_answers", "type": "text"},
            {"label": "Accuracy", "key": "percentage", "type": "percentage"},
            {"label": "Total Time", "key": "time_total", "type": "duration"},
        ],
    },
    "poker_sessions": {
        "title": "Poker Session Details",
        "fetch_func": get_poker_session_by_id,
        "delete_func": delete_poker_session,
        "highlight_field": "profit_loss",
        "fields": [
            {"label": "ID", "key": "id", "type": "text"},
            {"label": "Date", "key": "date", "type": "date"},
            {"label": "Stake Level", "key": "stake_level", "type": "text"},
            {"label": "Buy-in", "key": "buy_in", "type": "money"},
            {"label": "Cash-out", "key": "cash_out", "type": "money"},
            {"label": "Profit/Loss", "key": "profit_loss", "type": "profit"},
            {"label": "Duration", "key": "duration_minutes", "type": "duration"},
            {"label": "Hands Played", "key": "hands_played", "type": "text"},
            {"label": "Hourly Rate", "key": "hourly_rate", "type": "hourly"},
            {"label": "BB/Hour", "key": "bb_per_hour", "type": "text"},
            {"label": "Location", "key": "location", "type": "text"},
            {"label": "Game Type", "key": "game_type", "type": "text"},
            {"label": "Notes", "key": "notes", "type": "long_text"},
        ],
    },
    "hand_histories": {
        "title": "Hand History Details",
        "fetch_func": get_hand_history_by_id,
        "delete_func": delete_hand_history,
        "highlight_field": "hero_hand",
        "fields": [
            {"label": "ID", "key": "id", "type": "text"},
            {"label": "Date", "key": "created_at", "type": "date"},
            {"label": "Hero Hand", "key": "hero_hand", "type": "text"},
            {"label": "Position", "key": "position", "type": "text"},
            {"label": "Board", "key": "board", "type": "text"},
            {"label": "Result", "key": "result", "type": "result"},
            {"label": "Stake Level", "key": "stake_level", "type": "text"},
            {"label": "Pot Size", "key": "pot_size", "type": "money"},
            {"label": "Tags", "key": "tags", "type": "tags"},
            {"label": "Action Summary", "key": "action_summary", "type": "long_text"},
            {"label": "Notes", "key": "notes", "type": "long_text"},
            {"label": "Hand Text", "key": "hand_text", "type": "long_text"},
        ],
    },
}


class Mode7DetailScreen(Screen):
    """Dynamic detail view screen for admin mode."""

    CSS = """
    Mode7DetailScreen {
        align: center middle;
    }

    #detail_container {
        width: 80;
        height: 90%;
        border: solid $warning;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        color: $warning;
        text-style: bold;
    }

    #scroll_area {
        height: 1fr;
        width: 100%;
    }

    #highlight_display {
        text-align: center;
        width: 100%;
        padding: 1;
        text-style: bold;
        background: $surface-lighten-1;
        border: solid $warning-lighten-2;
        margin-bottom: 1;
    }

    #info_section {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .info_row {
        width: 100%;
        height: auto;
        margin-bottom: 0;
    }

    .info_label {
        width: 18;
        color: $text-muted;
    }

    .info_value {
        width: 1fr;
    }

    .positive {
        color: $success;
    }

    .negative {
        color: $error;
    }

    .long_text_section {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .section_title {
        color: $text-muted;
        text-style: bold;
        margin-bottom: 1;
    }

    .section_content {
        width: 100%;
    }

    .tags_display {
        width: 100%;
    }

    .button_row {
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
        width: 18;
    }

    #not_found {
        text-align: center;
        width: 100%;
        padding: 2;
        color: $error;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("d", "delete", "Delete", show=True),
    ]

    def __init__(self, table_type: str, record_id: int) -> None:
        """Initialize with table type and record ID."""
        super().__init__()
        self.table_type = table_type
        self.record_id = record_id
        self.record: Optional[Dict[str, Any]] = None
        self.config = DETAIL_CONFIG.get(table_type)

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="detail_container"):
            if not self.config:
                yield Static(f"Unknown table type: {self.table_type}", id="not_found")
                with Horizontal(classes="button_row"):
                    yield Button("Back", id="back_btn", variant="default")
            else:
                # Load record data
                fetch_func = self.config["fetch_func"]
                self.record = fetch_func(self.record_id)

                yield Static(
                    f"[bold yellow]{self.config['title']}[/bold yellow]", id="title"
                )

                if not self.record:
                    yield Static("Record not found", id="not_found")
                    with Horizontal(classes="button_row"):
                        yield Button("Back", id="back_btn", variant="default")
                else:
                    with VerticalScroll(id="scroll_area"):
                        # Highlight field at top (if configured)
                        highlight_key = self.config.get("highlight_field")
                        if highlight_key and highlight_key in self.record:
                            highlight_value = self._format_highlight(
                                highlight_key, self.record.get(highlight_key)
                            )
                            yield Static(highlight_value, id="highlight_display")

                        # Regular fields section
                        regular_fields = [
                            f
                            for f in self.config["fields"]
                            if f["type"] not in ("long_text", "tags")
                        ]
                        if regular_fields:
                            with Container(id="info_section"):
                                for field in regular_fields:
                                    value = self.record.get(field["key"])
                                    formatted = self._format_value(
                                        field["type"], value, self.record
                                    )
                                    value_class = self._get_value_class(
                                        field["type"], value
                                    )

                                    with Horizontal(classes="info_row"):
                                        yield Static(
                                            f"{field['label']}:", classes="info_label"
                                        )
                                        yield Static(formatted, classes=value_class)

                        # Tags section (if present)
                        tags_fields = [
                            f for f in self.config["fields"] if f["type"] == "tags"
                        ]
                        for field in tags_fields:
                            tags = self.record.get(field["key"], [])
                            with Container(classes="long_text_section"):
                                yield Static(
                                    f"{field['label']}:", classes="section_title"
                                )
                                if tags and isinstance(tags, list):
                                    tags_display = " ".join(
                                        f"[on blue] {tag} [/on blue]" for tag in tags
                                    )
                                    yield Static(tags_display, classes="tags_display")
                                else:
                                    yield Static("-", classes="section_content")

                        # Long text sections - always show all fields
                        long_text_fields = [
                            f for f in self.config["fields"] if f["type"] == "long_text"
                        ]
                        for field in long_text_fields:
                            value = self.record.get(field["key"])
                            display_value = str(value) if value else "-"
                            with Container(classes="long_text_section"):
                                yield Static(
                                    f"{field['label']}:", classes="section_title"
                                )
                                yield Static(display_value, classes="section_content")

                    # Buttons (outside scroll area)
                    with Horizontal(classes="button_row"):
                        yield Button("Delete", id="delete_btn", variant="error")
                        yield Button("Back", id="back_btn", variant="default")

        yield Footer()

    def _format_highlight(self, key: str, value: Any) -> str:
        """Format the highlight field for prominent display."""
        if key == "is_correct":
            if value:
                return "[bold green]CORRECT[/bold green]"
            else:
                return "[bold red]INCORRECT[/bold red]"
        elif key == "percentage":
            if value is not None:
                if value >= 70:
                    return f"[bold green]{value:.1f}%[/bold green]"
                elif value >= 50:
                    return f"[bold yellow]{value:.1f}%[/bold yellow]"
                else:
                    return f"[bold red]{value:.1f}%[/bold red]"
            return "-"
        elif key == "profit_loss":
            if value is not None:
                if value >= 0:
                    return f"[bold green]+${value:,.2f}[/bold green]"
                else:
                    return f"[bold red]-${abs(value):,.2f}[/bold red]"
            return "-"
        elif key == "hero_hand":
            return f"[bold white]{value or '-'}[/bold white]"
        else:
            return str(value) if value else "-"

    def _format_value(self, field_type: str, value: Any, record: Dict[str, Any]) -> str:
        """Format a value based on its field type."""
        if value is None:
            return "-"

        if field_type == "date":
            return str(value)[:10] if value else "-"

        if field_type == "boolean":
            return "[green]Yes[/green]" if value else "[red]No[/red]"

        if field_type == "money":
            try:
                return f"${float(value):,.2f}"
            except (ValueError, TypeError):
                return str(value)

        if field_type == "profit":
            try:
                v = float(value)
                if v >= 0:
                    return f"[green]+${v:,.2f}[/green]"
                else:
                    return f"[red]-${abs(v):,.2f}[/red]"
            except (ValueError, TypeError):
                return str(value)

        if field_type == "hourly":
            if value is None:
                return "-"
            try:
                v = float(value)
                if v >= 0:
                    return f"[green]+${v:,.2f}/hr[/green]"
                else:
                    return f"[red]-${abs(v):,.2f}/hr[/red]"
            except (ValueError, TypeError):
                return str(value)

        if field_type == "percentage":
            try:
                return f"{float(value):.1f}%"
            except (ValueError, TypeError):
                return str(value)

        if field_type == "time":
            if value:
                return f"{value}s"
            return "-"

        if field_type == "duration":
            if value:
                try:
                    mins = int(value)
                    hours = mins // 60
                    remaining_mins = mins % 60
                    if hours > 0:
                        return f"{hours}h {remaining_mins}m"
                    return f"{remaining_mins}m"
                except (ValueError, TypeError):
                    return str(value)
            return "-"

        if field_type == "result":
            if value == "won":
                return "[green]Won[/green]"
            elif value == "lost":
                return "[red]Lost[/red]"
            elif value:
                return str(value).capitalize()
            return "-"

        # Default: return as string
        return str(value) if value else "-"

    def _get_value_class(self, field_type: str, value: Any) -> str:
        """Get CSS class for value based on type and value."""
        if field_type == "profit" and value is not None:
            try:
                if float(value) >= 0:
                    return "info_value positive"
                else:
                    return "info_value negative"
            except (ValueError, TypeError):
                pass

        if field_type == "hourly" and value is not None:
            try:
                if float(value) >= 0:
                    return "info_value positive"
                else:
                    return "info_value negative"
            except (ValueError, TypeError):
                pass

        if field_type == "result":
            if value == "won":
                return "info_value positive"
            elif value == "lost":
                return "info_value negative"

        return "info_value"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "delete_btn":
            self.action_delete()

    def action_back(self) -> None:
        """Return to admin screen."""
        self.app.pop_screen()

    def action_delete(self) -> None:
        """Delete this record."""
        if not self.config:
            self.notify("Cannot delete: unknown table type", severity="error")
            return

        delete_func = self.config["delete_func"]
        if delete_func(self.record_id):
            self.notify("Record deleted")
            self.app.pop_screen()
        else:
            self.notify("Failed to delete record", severity="error")
