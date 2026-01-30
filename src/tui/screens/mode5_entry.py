"""Mode 5: Hand History Manager - Entry Screen (Step-by-Step Wizard)."""

from typing import List, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static, Input, Select, TextArea
from textual.binding import Binding

from ...database.service import save_hand_history
from ...core.hand_history import (
    POSITIONS,
    RESULTS,
    format_cards,
    validate_hero_hand,
    validate_hand_and_board,
    suggest_tags,
)


class Mode5EntryScreen(Screen):
    """Hand entry form screen with step-by-step wizard."""

    CSS = """
    Mode5EntryScreen {
        align: center middle;
    }

    #entry_container {
        width: 75;
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

    .hand_text_area {
        width: 100%;
        height: 8;
        margin-bottom: 1;
    }

    #card_preview {
        text-align: center;
        width: 100%;
        padding: 1;
        text-style: bold;
        border: solid $primary-lighten-2;
        background: $surface-lighten-1;
        margin-bottom: 1;
    }

    #validation_msg {
        text-align: center;
        width: 100%;
        padding: 0 1 1 1;
    }

    .validation_error {
        color: $error;
    }

    .validation_success {
        color: $success;
    }

    #suggested_tags {
        width: 100%;
        padding: 0 0 1 0;
        color: $text-muted;
    }

    .tag_chips {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    .tag_chip {
        width: auto;
        margin-right: 1;
        padding: 0 1;
        background: $primary-lighten-2;
    }

    .tag_chip.selected {
        background: $primary;
        color: $text;
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
        self.selected_tags: List[str] = []

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="entry_container"):
            yield Static("[bold cyan]Log New Hand[/bold cyan]", id="title")
            yield Static("Enter hand details below", id="subtitle")

            # Step 1: Hero Hand
            yield Static("1. Hero Hand", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Cards:", classes="label")
                yield Input(
                    placeholder="e.g., As Kh (two cards)",
                    id="hero_hand_input",
                )
            yield Static("", id="card_preview")
            yield Static("", id="validation_msg")

            # Step 2: Position
            yield Static("2. Position", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Position:", classes="label")
                yield Select(
                    [(pos, pos) for pos in POSITIONS],
                    id="position_select",
                    prompt="Select position",
                )

            # Step 3: Board
            yield Static("3. Board (optional)", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Board:", classes="label")
                yield Input(
                    placeholder="e.g., Qh Jh 2c (flop/turn/river)",
                    id="board_input",
                )

            # Step 4: Action & Result
            yield Static("4. Action & Result", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Action:", classes="label")
                yield TextArea(
                    id="action_input",
                )
            with Horizontal(classes="input_group"):
                yield Static("Result:", classes="label")
                yield Select(
                    [(r.capitalize(), r) for r in RESULTS],
                    id="result_select",
                    prompt="Select result",
                )

            # Step 5: Tags & Notes
            yield Static("5. Tags & Notes", classes="section_title")
            yield Static("Suggested tags:", id="suggested_tags")
            with Horizontal(classes="input_group"):
                yield Static("Tags:", classes="label")
                yield Input(
                    placeholder="bluff, value, c-bet (comma-separated)",
                    id="tags_input",
                )
            with Horizontal(classes="input_group"):
                yield Static("Notes:", classes="label")
                yield TextArea(
                    id="notes_input",
                )

            # Optional: Hand Text (raw hand history)
            yield Static("6. Hand Text (optional)", classes="section_title")
            yield Static(
                "[dim]Paste full hand history from poker site[/dim]",
                classes="help_text",
            )
            yield TextArea(id="hand_text_input", classes="hand_text_area")

            # Optional: Stake and Pot
            yield Static("7. Additional Info (optional)", classes="section_title")
            with Horizontal(classes="input_group"):
                yield Static("Stake Level:", classes="label")
                yield Select(
                    [
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
                        ("Other", "other"),
                    ],
                    id="stake_select",
                    prompt="Select stake (optional)",
                    allow_blank=True,
                )
            with Horizontal(classes="input_group"):
                yield Static("Pot Size ($):", classes="label")
                yield Input(
                    placeholder="150.00 (optional)",
                    id="pot_input",
                )

            # Buttons
            with Horizontal(classes="button_row"):
                yield Button("Save Hand", id="save_btn", variant="primary")
                yield Button("Clear", id="clear_btn", variant="warning")
                yield Button("Cancel", id="cancel_btn", variant="default")

            yield Static(
                "[dim]Ctrl+S to save | Escape to cancel[/dim]",
                classes="help_text",
            )

        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to update preview and validation."""
        input_id = event.input.id

        if input_id == "hero_hand_input":
            self._update_card_preview()
            self._update_validation()
            self._update_suggested_tags()

        elif input_id == "board_input":
            self._update_card_preview()
            self._update_validation()

        elif input_id == "action_input":
            self._update_suggested_tags()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area changes."""
        if event.text_area.id == "action_input":
            self._update_suggested_tags()

    def _update_card_preview(self) -> None:
        """Update the card preview display."""
        preview = self.query_one("#card_preview", Static)

        hero_hand = self.query_one("#hero_hand_input", Input).value.strip()
        board = self.query_one("#board_input", Input).value.strip()

        if not hero_hand:
            preview.update("")
            return

        formatted_hero = format_cards(hero_hand)
        formatted_board = format_cards(board) if board else ""

        if formatted_board:
            preview.update(f"[bold]{formatted_hero}[/bold]  |  {formatted_board}")
        else:
            preview.update(f"[bold]{formatted_hero}[/bold]")

    def _update_validation(self) -> None:
        """Update validation message."""
        validation_msg = self.query_one("#validation_msg", Static)

        hero_hand = self.query_one("#hero_hand_input", Input).value.strip()
        board = self.query_one("#board_input", Input).value.strip()

        if not hero_hand:
            validation_msg.update("")
            validation_msg.remove_class("validation_error", "validation_success")
            return

        is_valid, error = validate_hand_and_board(hero_hand, board)

        if is_valid:
            validation_msg.update("[green]Valid[/green]")
            validation_msg.remove_class("validation_error")
            validation_msg.add_class("validation_success")
        else:
            validation_msg.update(f"[red]{error}[/red]")
            validation_msg.remove_class("validation_success")
            validation_msg.add_class("validation_error")

    def _update_suggested_tags(self) -> None:
        """Update suggested tags based on action and hand."""
        suggested = self.query_one("#suggested_tags", Static)

        hero_hand = self.query_one("#hero_hand_input", Input).value.strip()
        action = self.query_one("#action_input", TextArea).text.strip()

        tags = suggest_tags(action_summary=action, hero_hand=hero_hand)

        if tags:
            suggested.update(f"Suggested: [cyan]{', '.join(tags)}[/cyan]")
        else:
            suggested.update("Suggested: [dim]Enter action to get suggestions[/dim]")

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
        self.query_one("#hero_hand_input", Input).value = ""
        self.query_one("#board_input", Input).value = ""
        self.query_one("#action_input", TextArea).clear()
        self.query_one("#tags_input", Input).value = ""
        self.query_one("#notes_input", TextArea).clear()
        self.query_one("#hand_text_input", TextArea).clear()
        self.query_one("#pot_input", Input).value = ""
        self.query_one("#card_preview", Static).update("")
        self.query_one("#validation_msg", Static).update("")
        self.query_one("#suggested_tags", Static).update(
            "Suggested: [dim]Enter action to get suggestions[/dim]"
        )
        self.selected_tags = []
        self.notify("Form cleared")

    def action_back(self) -> None:
        """Return to hand history menu."""
        self.app.pop_screen()

    def action_save(self) -> None:
        """Save the hand."""
        # Get values
        hero_hand = self.query_one("#hero_hand_input", Input).value.strip()
        position_select = self.query_one("#position_select", Select)
        board = self.query_one("#board_input", Input).value.strip()
        action = self.query_one("#action_input", TextArea).text.strip()
        result_select = self.query_one("#result_select", Select)
        tags_str = self.query_one("#tags_input", Input).value.strip()
        notes = self.query_one("#notes_input", TextArea).text.strip()
        hand_text = self.query_one("#hand_text_input", TextArea).text.strip()
        stake_select = self.query_one("#stake_select", Select)
        pot_str = self.query_one("#pot_input", Input).value.strip()

        # Validate required fields
        errors = []

        # Validate hero hand
        is_valid, error = validate_hero_hand(hero_hand)
        if not is_valid:
            errors.append(error or "Invalid hero hand")

        # Validate position
        if position_select.value is None or position_select.value == Select.BLANK:
            errors.append("Please select a position")

        # Validate board (if provided)
        if board:
            is_valid, error = validate_hand_and_board(hero_hand, board)
            if not is_valid:
                errors.append(error or "Invalid board")

        # Validate result
        if result_select.value is None or result_select.value == Select.BLANK:
            errors.append("Please select a result")

        if errors:
            self.notify("\n".join(errors), severity="error")
            return

        # Parse tags
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

        # Parse pot size
        pot_size: Optional[float] = None
        if pot_str:
            try:
                pot_size = float(pot_str)
                if pot_size < 0:
                    self.notify("Pot size cannot be negative", severity="error")
                    return
            except ValueError:
                self.notify("Invalid pot size", severity="error")
                return

        # Build hand data
        hand_data = {
            "hero_hand": hero_hand,
            "position": str(position_select.value),
            "board": board or None,
            "action_summary": action or None,
            "result": str(result_select.value),
            "tags": tags,
            "notes": notes or None,
            "hand_text": hand_text or None,
            "stake_level": (
                str(stake_select.value)
                if stake_select.value and stake_select.value != Select.BLANK
                else None
            ),
            "pot_size": pot_size,
        }

        # Save to database
        try:
            save_hand_history(hand_data)
            formatted = format_cards(hero_hand)
            result = str(result_select.value).capitalize()
            self.notify(f"Hand saved! {formatted} - {result}", severity="information")
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"Error saving hand: {e}", severity="error")
