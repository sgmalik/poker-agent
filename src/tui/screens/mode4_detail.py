"""Mode 4: Session Tracker - Detail Screen."""

from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...database.service import get_poker_session_by_id, delete_poker_session


class Mode4DetailScreen(Screen):
    """Session detail view screen."""

    CSS = """
    Mode4DetailScreen {
        align: center middle;
    }

    #detail_container {
        width: 70;
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

    #profit_display {
        text-align: center;
        width: 100%;
        padding: 2;
        text-style: bold;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    #info_section {
        width: 100%;
        height: auto;
        padding: 1;
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

    .info_value.positive {
        color: $success;
    }

    .info_value.negative {
        color: $error;
    }

    #notes_section {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .section_label {
        color: $text-muted;
        margin-bottom: 1;
    }

    .section_content {
        width: 100%;
    }

    .button_row {
        margin-top: 1;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
        width: 18;
        text-align: center;
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

    def __init__(self, session_id: int) -> None:
        """Initialize with session ID."""
        super().__init__()
        self.session_id = session_id
        self.session: Optional[Dict[str, Any]] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="detail_container"):
            yield Static("[bold cyan]Session Details[/bold cyan]", id="title")

            # Load session data
            self.session = get_poker_session_by_id(self.session_id)

            if not self.session:
                yield Static("Session not found", id="not_found")
                with Horizontal(classes="button_row"):
                    yield Button("Back", id="back_btn", variant="default")
            else:
                # Profit display (large, centered)
                profit = self.session.get("profit_loss", 0)
                if profit >= 0:
                    profit_str = f"[bold green]+${profit:,.2f}[/bold green]"
                else:
                    profit_str = f"[bold red]-${abs(profit):,.2f}[/bold red]"
                yield Static(profit_str, id="profit_display")

                # Info section
                with Container(id="info_section"):
                    # Date
                    date = self.session.get("date", "")
                    date_str = date[:10] if date else "-"
                    with Horizontal(classes="info_row"):
                        yield Static("Date:", classes="info_label")
                        yield Static(date_str, classes="info_value")

                    # Stake level
                    stake = self.session.get("stake_level", "-") or "-"
                    with Horizontal(classes="info_row"):
                        yield Static("Stake:", classes="info_label")
                        yield Static(stake, classes="info_value")

                    # Game type
                    game_type = self.session.get("game_type", "cash") or "cash"
                    with Horizontal(classes="info_row"):
                        yield Static("Game Type:", classes="info_label")
                        yield Static(game_type.capitalize(), classes="info_value")

                    # Buy-in
                    buy_in = self.session.get("buy_in", 0)
                    with Horizontal(classes="info_row"):
                        yield Static("Buy-in:", classes="info_label")
                        yield Static(f"${buy_in:,.2f}", classes="info_value")

                    # Cash-out
                    cash_out = self.session.get("cash_out", 0)
                    with Horizontal(classes="info_row"):
                        yield Static("Cash-out:", classes="info_label")
                        yield Static(f"${cash_out:,.2f}", classes="info_value")

                    # Profit/Loss
                    profit_class = (
                        "info_value positive" if profit >= 0 else "info_value negative"
                    )
                    with Horizontal(classes="info_row"):
                        yield Static("Profit/Loss:", classes="info_label")
                        yield Static(
                            (
                                f"+${profit:,.2f}"
                                if profit >= 0
                                else f"-${abs(profit):,.2f}"
                            ),
                            classes=profit_class,
                        )

                    # Duration
                    duration = self.session.get("duration_minutes")
                    if duration:
                        hours = duration // 60
                        mins = duration % 60
                        duration_str = f"{hours}h {mins}m" if hours else f"{mins}m"
                    else:
                        duration_str = "-"
                    with Horizontal(classes="info_row"):
                        yield Static("Duration:", classes="info_label")
                        yield Static(duration_str, classes="info_value")

                    # Hourly rate
                    hourly = self.session.get("hourly_rate")
                    if hourly is not None:
                        hourly_class = (
                            "info_value positive"
                            if hourly >= 0
                            else "info_value negative"
                        )
                        hourly_str = (
                            f"+${hourly:,.2f}/hr"
                            if hourly >= 0
                            else f"-${abs(hourly):,.2f}/hr"
                        )
                    else:
                        hourly_class = "info_value"
                        hourly_str = "-"
                    with Horizontal(classes="info_row"):
                        yield Static("Hourly Rate:", classes="info_label")
                        yield Static(hourly_str, classes=hourly_class)

                    # Hands played (if present)
                    hands = self.session.get("hands_played")
                    if hands:
                        with Horizontal(classes="info_row"):
                            yield Static("Hands Played:", classes="info_label")
                            yield Static(f"{hands:,}", classes="info_value")

                    # Location
                    location = self.session.get("location", "") or "-"
                    with Horizontal(classes="info_row"):
                        yield Static("Location:", classes="info_label")
                        yield Static(location, classes="info_value")

                # Notes section (if present)
                notes = self.session.get("notes")
                if notes:
                    with Container(id="notes_section"):
                        yield Static("Notes:", classes="section_label")
                        yield Static(notes, classes="section_content")

                # Buttons
                with Horizontal(classes="button_row"):
                    yield Button("Delete", id="delete_btn", variant="error")
                    yield Button("Back", id="back_btn", variant="default")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "delete_btn":
            self.action_delete()

    def action_back(self) -> None:
        """Return to history screen."""
        self.app.pop_screen()

    def action_delete(self) -> None:
        """Delete this session."""
        if delete_poker_session(self.session_id):
            self.notify("Session deleted")
            self.app.pop_screen()
        else:
            self.notify("Failed to delete session", severity="error")
