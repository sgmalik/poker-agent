"""Mode 5: Hand History Manager - Detail Screen."""

from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...database.service import get_hand_history_by_id, delete_hand_history
from ...core.hand_history import format_cards, format_board_by_street


class Mode5DetailScreen(Screen):
    """Hand detail view screen."""

    CSS = """
    Mode5DetailScreen {
        align: center middle;
    }

    #detail_container {
        width: 85;
        height: 95%;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 0 1;
        color: $accent;
        text-style: bold;
    }

    #scroll_area {
        height: 1fr;
        width: 100%;
    }

    #hero_hand_display {
        text-align: center;
        width: 100%;
        padding: 0;
        text-style: bold;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    #board_section {
        width: 100%;
        height: 3;
        padding: 0 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .board_street {
        width: 1fr;
        height: 3;
        text-align: center;
        content-align: center middle;
    }

    .street_label {
        color: $text-muted;
        text-align: center;
        width: auto;
        margin-right: 1;
    }

    .street_cards {
        text-align: center;
        width: auto;
        text-style: bold;
    }

    #info_section {
        width: 100%;
        height: auto;
        padding: 0 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .info_row {
        width: 100%;
        height: 1;
        margin-bottom: 0;
    }

    .info_label {
        width: 18;
        color: $text-muted;
    }

    .info_value {
        width: 1fr;
    }

    .won {
        color: $success;
    }

    .lost {
        color: $error;
    }

    #tags_section {
        width: 100%;
        height: auto;
        padding: 0 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .section_title {
        color: $text-muted;
        text-style: bold;
    }

    .tags_display {
        width: 100%;
    }

    #action_section {
        width: 100%;
        height: auto;
        padding: 0 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .section_content {
        width: 100%;
    }

    #notes_section {
        width: 100%;
        height: auto;
        padding: 0 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    #hand_text_section {
        width: 100%;
        height: auto;
        padding: 0 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
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

    def __init__(self, hand_id: int) -> None:
        """Initialize with hand ID."""
        super().__init__()
        self.hand_id = hand_id
        self.hand: Optional[Dict[str, Any]] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Load hand data
        self.hand = get_hand_history_by_id(self.hand_id)

        with Container(id="detail_container"):
            yield Static("[bold cyan]Hand Details[/bold cyan]", id="title")

            if not self.hand:
                yield Static("Hand not found", id="not_found")
                with Horizontal(classes="button_row"):
                    yield Button("Back", id="back_btn", variant="default")
            else:
                with VerticalScroll(id="scroll_area"):
                    # Hero hand display (large, centered)
                    hero_hand = format_cards(self.hand.get("hero_hand", ""))
                    yield Static(
                        f"[bold white]{hero_hand}[/bold white]", id="hero_hand_display"
                    )

                    # Board by street (compact layout)
                    board = self.hand.get("board", "")
                    if board:
                        board_by_street = format_board_by_street(board)
                        with Horizontal(id="board_section"):
                            with Horizontal(classes="board_street"):
                                yield Static("Flop:", classes="street_label")
                                yield Static(
                                    board_by_street.get("flop", "-") or "-",
                                    classes="street_cards",
                                )
                            with Horizontal(classes="board_street"):
                                yield Static("Turn:", classes="street_label")
                                yield Static(
                                    board_by_street.get("turn", "-") or "-",
                                    classes="street_cards",
                                )
                            with Horizontal(classes="board_street"):
                                yield Static("River:", classes="street_label")
                                yield Static(
                                    board_by_street.get("river", "-") or "-",
                                    classes="street_cards",
                                )

                    # Info section - always show all fields
                    with Container(id="info_section"):
                        # Position
                        position = self.hand.get("position", "") or "-"
                        with Horizontal(classes="info_row"):
                            yield Static("Position:", classes="info_label")
                            yield Static(position, classes="info_value")

                        # Result
                        result = self.hand.get("result", "")
                        if result == "won":
                            result_display = "[green]Won[/green]"
                            result_class = "info_value won"
                        elif result == "lost":
                            result_display = "[red]Lost[/red]"
                            result_class = "info_value lost"
                        elif result:
                            result_display = result.capitalize()
                            result_class = "info_value"
                        else:
                            result_display = "-"
                            result_class = "info_value"

                        with Horizontal(classes="info_row"):
                            yield Static("Result:", classes="info_label")
                            yield Static(result_display, classes=result_class)

                        # Street
                        street = self.hand.get("street", "") or "-"
                        with Horizontal(classes="info_row"):
                            yield Static("Street:", classes="info_label")
                            yield Static(
                                street.capitalize() if street != "-" else "-",
                                classes="info_value",
                            )

                        # Stake level
                        stake = self.hand.get("stake_level", "") or "-"
                        with Horizontal(classes="info_row"):
                            yield Static("Stakes:", classes="info_label")
                            yield Static(stake, classes="info_value")

                        # Pot size
                        pot = self.hand.get("pot_size")
                        pot_str = f"${pot:,.2f}" if pot else "-"
                        with Horizontal(classes="info_row"):
                            yield Static("Pot Size:", classes="info_label")
                            yield Static(pot_str, classes="info_value")

                        # Date
                        created = self.hand.get("created_at", "")
                        date_str = created[:10] if created else "-"
                        with Horizontal(classes="info_row"):
                            yield Static("Date:", classes="info_label")
                            yield Static(date_str, classes="info_value")

                    # Tags section
                    tags = self.hand.get("tags", [])
                    with Container(id="tags_section"):
                        yield Static("Tags:", classes="section_title")
                        if tags:
                            tags_display = " ".join(
                                f"[on blue] {tag} [/on blue]" for tag in tags
                            )
                            yield Static(tags_display, classes="tags_display")
                        else:
                            yield Static("-", classes="tags_display")

                    # Action section
                    action = self.hand.get("action_summary", "") or "-"
                    with Container(id="action_section"):
                        yield Static("Action Summary:", classes="section_title")
                        yield Static(action, classes="section_content")

                    # Notes section
                    notes = self.hand.get("notes", "") or "-"
                    with Container(id="notes_section"):
                        yield Static("Notes:", classes="section_title")
                        yield Static(notes, classes="section_content")

                    # Hand Text section (full hand history)
                    hand_text = self.hand.get("hand_text", "") or "-"
                    with Container(id="hand_text_section"):
                        yield Static("Hand Text:", classes="section_title")
                        yield Static(hand_text, classes="section_content")

                # Buttons (outside scroll area)
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
        """Delete this hand."""
        if delete_hand_history(self.hand_id):
            self.notify("Hand deleted")
            self.app.pop_screen()
        else:
            self.notify("Failed to delete hand", severity="error")
