"""Mode 4: Session Tracker - Entry Screen."""

from datetime import datetime, timezone
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Input, Select, TextArea
from textual.binding import Binding
from textual.validation import Number

from ...database.service import save_poker_session


class Mode4EntryScreen(Screen):
    """Session entry form screen."""

    CSS = """
    Mode4EntryScreen {
        align: center middle;
    }

    #entry_container {
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

    #subtitle {
        text-align: center;
        width: 100%;
        padding: 0 0 1 0;
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

    Input, Select {
        width: 1fr;
    }

    TextArea {
        width: 1fr;
        height: 4;
    }

    #profit_display {
        text-align: center;
        width: 100%;
        padding: 1;
        text-style: bold;
    }

    #profit_display.positive {
        color: $success;
    }

    #profit_display.negative {
        color: $error;
    }

    #profit_display.zero {
        color: $text-muted;
    }

    .button_row {
        margin-top: 2;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
        width: 18;
        text-align: center;
    }

    .help_text {
        color: $text-muted;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }

    .error {
        color: $error;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the entry screen."""
        super().__init__()
        self.buy_in_value: float = 0.0
        self.cash_out_value: float = 0.0

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="entry_container"):
            yield Static("[bold cyan]Log Session[/bold cyan]", id="title")
            yield Static("Enter your session details", id="subtitle")

            # Date
            yield Static("Session Details", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Date:", classes="label")
                yield Input(
                    placeholder="YYYY-MM-DD (leave empty for today)",
                    id="date_input",
                )

            # Stake level
            with Horizontal(classes="input_group"):
                yield Static("Stake Level:", classes="label")
                yield Select(
                    [
                        ("$0.25/0.50 NL", "0.25/0.50"),
                        ("1/2 NL", "1/2"),
                        ("1/3 NL", "1/3"),
                        ("2/5 NL", "2/5"),
                        ("5/10 NL", "5/10"),
                        ("NL2", "NL2"),
                        ("NL5", "NL5"),
                        ("NL10", "NL10"),
                        ("NL25", "NL25"),
                        ("NL50", "NL50"),
                        ("NL100", "NL100"),
                        ("NL200", "NL200"),
                        ("Other", "other"),
                    ],
                    id="stake_select",
                    prompt="Select stake level",
                )

            # Game type
            with Horizontal(classes="input_group"):
                yield Static("Game Type:", classes="label")
                yield Select(
                    [
                        ("Cash Game", "cash"),
                        ("Tournament", "tournament"),
                    ],
                    id="game_type_select",
                    value="cash",
                )

            # Financial
            yield Static("Financials", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Buy-in ($):", classes="label")
                yield Input(
                    placeholder="100.00",
                    id="buyin_input",
                    validators=[Number(minimum=0)],
                )

            with Horizontal(classes="input_group"):
                yield Static("Cash-out ($):", classes="label")
                yield Input(
                    placeholder="150.00",
                    id="cashout_input",
                    validators=[Number(minimum=0)],
                )

            # Profit display
            yield Static("Profit/Loss: $0.00", id="profit_display", classes="zero")

            # Duration and hands
            yield Static("Session Info", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Duration (min):", classes="label")
                yield Input(
                    placeholder="120",
                    id="duration_input",
                    validators=[Number(minimum=0)],
                )

            with Horizontal(classes="input_group"):
                yield Static("Hands Played:", classes="label")
                yield Input(
                    placeholder="250 (optional)",
                    id="hands_input",
                    validators=[Number(minimum=0)],
                )

            with Horizontal(classes="input_group"):
                yield Static("Location:", classes="label")
                yield Input(
                    placeholder="Casino name or online site",
                    id="location_input",
                )

            # Notes
            with Horizontal(classes="input_group"):
                yield Static("Notes:", classes="label")
                yield TextArea(
                    id="notes_input",
                )

            # Buttons
            with Horizontal(classes="button_row"):
                yield Button("Save Session", id="save_btn", variant="primary")
                yield Button("Clear", id="clear_btn", variant="warning")
                yield Button("Cancel", id="cancel_btn", variant="default")

            yield Static(
                "[dim]Ctrl+S to save | Escape to cancel[/dim]",
                classes="help_text",
            )

        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to update profit display."""
        input_id = event.input.id

        if input_id == "buyin_input":
            try:
                self.buy_in_value = float(event.value) if event.value else 0.0
            except ValueError:
                self.buy_in_value = 0.0
            self._update_profit_display()

        elif input_id == "cashout_input":
            try:
                self.cash_out_value = float(event.value) if event.value else 0.0
            except ValueError:
                self.cash_out_value = 0.0
            self._update_profit_display()

    def _update_profit_display(self) -> None:
        """Update the profit display."""
        profit = self.cash_out_value - self.buy_in_value
        display = self.query_one("#profit_display", Static)

        # Remove old classes
        display.remove_class("positive", "negative", "zero")

        if profit > 0:
            display.update(f"Profit/Loss: [green]+${profit:,.2f}[/green]")
            display.add_class("positive")
        elif profit < 0:
            display.update(f"Profit/Loss: [red]-${abs(profit):,.2f}[/red]")
            display.add_class("negative")
        else:
            display.update("Profit/Loss: $0.00")
            display.add_class("zero")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "cancel_btn":
            self.action_back()
        elif button_id == "save_btn":
            self.action_save()
        elif button_id == "clear_btn":
            self._clear_form()

    def _clear_form(self) -> None:
        """Clear all form inputs."""
        self.query_one("#date_input", Input).value = ""
        self.query_one("#buyin_input", Input).value = ""
        self.query_one("#cashout_input", Input).value = ""
        self.query_one("#duration_input", Input).value = ""
        self.query_one("#hands_input", Input).value = ""
        self.query_one("#location_input", Input).value = ""
        self.query_one("#notes_input", TextArea).clear()
        self.buy_in_value = 0.0
        self.cash_out_value = 0.0
        self._update_profit_display()
        self.notify("Form cleared")

    def action_back(self) -> None:
        """Return to session tracker menu."""
        self.app.pop_screen()

    def action_save(self) -> None:
        """Save the session."""
        # Get values
        date_str = self.query_one("#date_input", Input).value.strip()
        stake_select = self.query_one("#stake_select", Select)
        game_type_select = self.query_one("#game_type_select", Select)
        buyin_str = self.query_one("#buyin_input", Input).value.strip()
        cashout_str = self.query_one("#cashout_input", Input).value.strip()
        duration_str = self.query_one("#duration_input", Input).value.strip()
        hands_str = self.query_one("#hands_input", Input).value.strip()
        location = self.query_one("#location_input", Input).value.strip()
        notes = self.query_one("#notes_input", TextArea).text.strip()

        # Validate required fields
        errors = []

        if stake_select.value is None or stake_select.value == Select.BLANK:
            errors.append("Please select a stake level")

        buy_in: float = 0.0
        cash_out: float = 0.0

        if not buyin_str:
            errors.append("Buy-in is required")
        else:
            try:
                buy_in = float(buyin_str)
                if buy_in < 0:
                    errors.append("Buy-in cannot be negative")
            except ValueError:
                errors.append("Invalid buy-in amount")

        if not cashout_str:
            errors.append("Cash-out is required")
        else:
            try:
                cash_out = float(cashout_str)
                if cash_out < 0:
                    errors.append("Cash-out cannot be negative")
            except ValueError:
                errors.append("Invalid cash-out amount")

        if errors:
            self.notify("\n".join(errors), severity="error")
            return

        # Parse date
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                self.notify("Invalid date format. Use YYYY-MM-DD", severity="error")
                return
        else:
            date = datetime.now(timezone.utc)

        # Parse optional fields
        duration_minutes = int(duration_str) if duration_str else None
        hands_played = int(hands_str) if hands_str else None

        # Build session data
        session_data = {
            "date": date,
            "stake_level": str(stake_select.value),
            "game_type": (
                str(game_type_select.value) if game_type_select.value else "cash"
            ),
            "buy_in": buy_in,
            "cash_out": cash_out,
            "duration_minutes": duration_minutes,
            "hands_played": hands_played,
            "location": location or None,
            "notes": notes or None,
        }

        # Save to database
        try:
            save_poker_session(session_data)
            profit = cash_out - buy_in
            if profit >= 0:
                self.notify(f"Session saved! (+${profit:,.2f})", severity="information")
            else:
                self.notify(
                    f"Session saved! (-${abs(profit):,.2f})", severity="information"
                )
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"Error saving session: {e}", severity="error")
