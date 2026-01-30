"""Mode 5: Hand History Manager - Detail Screen."""

from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
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
        width: 80;
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

    #hero_hand_display {
        text-align: center;
        width: 100%;
        padding: 2;
        text-style: bold;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    #board_section {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
    }

    .board_street {
        width: 1fr;
        text-align: center;
        padding: 0 1;
    }

    .street_label {
        color: $text-muted;
        text-align: center;
        width: 100%;
    }

    .street_cards {
        text-align: center;
        width: 100%;
        text-style: bold;
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
        width: 15;
        color: $text-muted;
    }

    .info_value {
        width: 1fr;
    }

    .info_value.won {
        color: $success;
    }

    .info_value.lost {
        color: $error;
    }

    #tags_section {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
    }

    .tags_display {
        width: 100%;
    }

    .tag {
        background: $primary-lighten-2;
        padding: 0 1;
        margin-right: 1;
    }

    #action_section {
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

    #notes_section {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary-lighten-2;
        margin-bottom: 1;
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

    def __init__(self, hand_id: int) -> None:
        """Initialize with hand ID."""
        super().__init__()
        self.hand_id = hand_id
        self.hand: Optional[Dict[str, Any]] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="detail_container"):
            yield Static("[bold cyan]Hand Details[/bold cyan]", id="title")

            # Load hand data
            self.hand = get_hand_history_by_id(self.hand_id)

            if not self.hand:
                yield Static("Hand not found", id="not_found")
                with Horizontal(classes="button_row"):
                    yield Button("Back", id="back_btn", variant="default")
            else:
                # Hero hand display (large, centered)
                hero_hand = format_cards(self.hand.get("hero_hand", ""))
                yield Static(
                    f"[bold white]{hero_hand}[/bold white]", id="hero_hand_display"
                )

                # Board by street
                board = self.hand.get("board", "")
                if board:
                    board_by_street = format_board_by_street(board)
                    with Horizontal(id="board_section"):
                        with Vertical(classes="board_street"):
                            yield Static("Flop", classes="street_label")
                            yield Static(
                                board_by_street.get("flop", "-") or "-",
                                classes="street_cards",
                            )
                        with Vertical(classes="board_street"):
                            yield Static("Turn", classes="street_label")
                            yield Static(
                                board_by_street.get("turn", "-") or "-",
                                classes="street_cards",
                            )
                        with Vertical(classes="board_street"):
                            yield Static("River", classes="street_label")
                            yield Static(
                                board_by_street.get("river", "-") or "-",
                                classes="street_cards",
                            )

                # Basic info section
                with Container(id="info_section"):
                    # Position
                    with Horizontal(classes="info_row"):
                        yield Static("Position:", classes="info_label")
                        yield Static(
                            self.hand.get("position", "-"),
                            classes="info_value",
                        )

                    # Result
                    result = self.hand.get("result", "")
                    result_display = result.capitalize() if result else "-"
                    result_class = "info_value"
                    if result == "won":
                        result_class = "info_value won"
                        result_display = f"[green]{result_display}[/green]"
                    elif result == "lost":
                        result_class = "info_value lost"
                        result_display = f"[red]{result_display}[/red]"

                    with Horizontal(classes="info_row"):
                        yield Static("Result:", classes="info_label")
                        yield Static(result_display, classes=result_class)

                    # Street
                    with Horizontal(classes="info_row"):
                        yield Static("Street:", classes="info_label")
                        yield Static(
                            self.hand.get("street", "-").capitalize(),
                            classes="info_value",
                        )

                    # Stake level (if present)
                    stake = self.hand.get("stake_level")
                    if stake:
                        with Horizontal(classes="info_row"):
                            yield Static("Stakes:", classes="info_label")
                            yield Static(stake, classes="info_value")

                    # Pot size (if present)
                    pot = self.hand.get("pot_size")
                    if pot:
                        with Horizontal(classes="info_row"):
                            yield Static("Pot Size:", classes="info_label")
                            yield Static(f"${pot:,.2f}", classes="info_value")

                    # Date
                    created = self.hand.get("created_at", "")
                    date_str = created[:10] if created else "-"
                    with Horizontal(classes="info_row"):
                        yield Static("Date:", classes="info_label")
                        yield Static(date_str, classes="info_value")

                # Tags section
                tags = self.hand.get("tags", [])
                if tags:
                    with Container(id="tags_section"):
                        yield Static("Tags:", classes="section_label")
                        tags_display = " ".join(
                            f"[on blue] {tag} [/on blue]" for tag in tags
                        )
                        yield Static(tags_display, classes="tags_display")

                # Action section
                action = self.hand.get("action_summary")
                if action:
                    with Container(id="action_section"):
                        yield Static("Action:", classes="section_label")
                        yield Static(action, classes="section_content")

                # Notes section
                notes = self.hand.get("notes")
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
        """Delete this hand."""
        if delete_hand_history(self.hand_id):
            self.notify("Hand deleted")
            self.app.pop_screen()
        else:
            self.notify("Failed to delete hand", severity="error")
