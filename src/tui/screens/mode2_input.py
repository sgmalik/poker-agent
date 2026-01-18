"""Mode 2: Range Tools - Input Screen."""

from typing import Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Input, Static, Label, Select
from textual.binding import Binding

from ...core.gto_charts import GTOCharts


class Mode2InputScreen(Screen):
    """Interactive input screen for range visualization."""

    CSS = """
    Mode2InputScreen {
        align: center middle;
    }

    #input_container {
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
        padding: 0 0 2 0;
        color: $text-muted;
    }

    .section_title {
        width: 100%;
        padding: 1 0 0 0;
        color: $accent;
        text-style: bold;
    }

    .position_row {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    .position_btn {
        width: 1fr;
        min-width: 6;
        margin: 0 1 0 0;
    }

    .position_btn.selected {
        background: $accent;
        color: $surface;
    }

    .input_group {
        height: auto;
        margin-bottom: 1;
    }

    .label {
        width: 20;
        color: $text;
        content-align: left middle;
    }

    Input {
        width: 1fr;
    }

    Select {
        width: 1fr;
    }

    .button_row {
        margin-top: 2;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .help_text {
        color: $text-muted;
        text-align: center;
        width: 100%;
        padding: 1 0 0 0;
    }

    .or_divider {
        text-align: center;
        width: 100%;
        padding: 1 0;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+v", "view_range", "View Range", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the input screen."""
        super().__init__()
        self.charts = GTOCharts()
        self.selected_position: Optional[str] = None
        self.selected_action: Optional[str] = None
        self.custom_range: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="input_container"):
            yield Static("[bold cyan]Range Tools[/bold cyan]", id="title")
            yield Static("View GTO preflop ranges (9-handed)", id="subtitle")

            # Position selection
            yield Static("Select Position:", classes="section_title")

            # Row 1: Early/Middle positions
            with Horizontal(classes="position_row"):
                yield Button("UTG", id="pos_UTG", classes="position_btn")
                yield Button("UTG+1", id="pos_UTG-1", classes="position_btn")
                yield Button("MP", id="pos_MP", classes="position_btn")
                yield Button("LJ", id="pos_LJ", classes="position_btn")
                yield Button("HJ", id="pos_HJ", classes="position_btn")

            # Row 2: Late positions
            with Horizontal(classes="position_row"):
                yield Button("CO", id="pos_CO", classes="position_btn")
                yield Button("BTN", id="pos_BTN", classes="position_btn")
                yield Button("SB", id="pos_SB", classes="position_btn")
                yield Button("BB", id="pos_BB", classes="position_btn")

            # Action selection
            with Horizontal(classes="input_group"):
                yield Label("Action:", classes="label")
                yield Select(
                    [("Select position first", "")],
                    id="action_select",
                    value="",
                )

            yield Static("- or -", classes="or_divider")

            # Custom range input
            with Horizontal(classes="input_group"):
                yield Label("Custom Range:", classes="label")
                yield Input(
                    placeholder="e.g., QQ+, AKs, 98s+",
                    id="custom_range",
                )

            # Buttons
            with Horizontal(classes="button_row"):
                yield Button("View Range", id="view_range", variant="primary")
                yield Button("Back", id="back", variant="default")

            # Help text
            yield Static(
                "[dim]Select a position + action OR enter a custom range[/dim]",
                classes="help_text",
            )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id or ""

        if button_id == "back":
            self.action_back()
        elif button_id == "view_range":
            self.action_view_range()
        elif button_id.startswith("pos_"):
            self._select_position(button_id[4:])

    def _select_position(self, position: str) -> None:
        """Handle position button selection."""
        # Update visual state - remove selected from all, add to clicked
        for btn in self.query(".position_btn"):
            btn.remove_class("selected")

        clicked_btn = self.query_one(f"#pos_{position}", Button)
        clicked_btn.add_class("selected")

        # Map button ID back to data key (UTG-1 -> UTG+1)
        self.selected_position = position.replace("-1", "+1")

        # Update action dropdown
        actions = self.charts.get_actions(self.selected_position)
        select = self.query_one("#action_select", Select)

        if actions:
            # Format action names for display
            formatted_actions = []
            for action in actions:
                if action == "open":
                    formatted_actions.append(("Open/Raise", action))
                elif action == "call_vs_BTN":
                    formatted_actions.append(("Call vs BTN Open", action))
                elif action == "3bet_vs_BTN":
                    formatted_actions.append(("3-bet vs BTN Open", action))
                else:
                    formatted_actions.append((action.replace("_", " ").title(), action))

            select.set_options(formatted_actions)
            select.value = actions[0]
            self.selected_action = actions[0]
        else:
            select.set_options([("No actions available", "")])
            select.value = ""
            self.selected_action = None

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle action selection change."""
        if event.select.id == "action_select":
            self.selected_action = str(event.value) if event.value else None

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()

    def action_view_range(self) -> None:
        """View the selected or custom range."""
        # Check for custom range first
        custom_input = self.query_one("#custom_range", Input)
        self.custom_range = custom_input.value.strip()

        if self.custom_range:
            # Use custom range
            from .mode2_matrix import Mode2MatrixScreen

            self.app.push_screen(
                Mode2MatrixScreen(
                    custom_range=self.custom_range,
                )
            )
        elif self.selected_position and self.selected_action:
            # Use GTO range
            from .mode2_matrix import Mode2MatrixScreen

            self.app.push_screen(
                Mode2MatrixScreen(
                    position=self.selected_position,
                    action=self.selected_action,
                )
            )
        else:
            self.notify(
                "Please select a position + action or enter a custom range",
                severity="error",
            )
