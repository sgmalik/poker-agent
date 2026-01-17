"""Mode 1: Hand Evaluator & Spot Analyzer - Input Screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Input, Static, Label
from textual.binding import Binding


class Mode1InputScreen(Screen):
    """Interactive input screen for hand evaluation and spot analysis."""

    CSS = """
    Mode1InputScreen {
        align: center middle;
    }

    #input_container {
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

    #subtitle {
        text-align: center;
        width: 100%;
        padding: 0 0 2 0;
        color: $text-muted;
    }

    .input_group {
        height: auto;
        margin-bottom: 1;
    }

    .label {
        width: 25;
        color: $text;
        content-align: left middle;
    }

    Input {
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
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+a", "analyze", "Analyze", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the input screen."""
        super().__init__()
        self.hero_hand = ""
        self.board = ""
        self.pot_size = None
        self.bet_to_call = None
        self.effective_stack = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="input_container"):
            yield Static(
                "[bold cyan]Hand Evaluator & Spot Analyzer[/bold cyan]", id="title"
            )
            yield Static("Enter hand details below", id="subtitle")

            # Hero hand input
            with Horizontal(classes="input_group"):
                yield Label("Hero Hand:", classes="label")
                yield Input(
                    placeholder="e.g., As Kh",
                    id="hero_hand",
                )

            # Board input
            with Horizontal(classes="input_group"):
                yield Label("Board:", classes="label")
                yield Input(
                    placeholder="e.g., Qh Jh 2c (3-5 cards)",
                    id="board",
                )

            # Pot size input (optional for spot analysis)
            with Horizontal(classes="input_group"):
                yield Label("Pot Size (optional):", classes="label")
                yield Input(
                    placeholder="e.g., 100",
                    id="pot_size",
                )

            # Bet to call input (optional for spot analysis)
            with Horizontal(classes="input_group"):
                yield Label("Bet to Call (optional):", classes="label")
                yield Input(
                    placeholder="e.g., 50",
                    id="bet_to_call",
                )

            # Effective stack input (optional for spot analysis)
            with Horizontal(classes="input_group"):
                yield Label("Effective Stack (optional):", classes="label")
                yield Input(
                    placeholder="e.g., 500",
                    id="effective_stack",
                )

            # Buttons
            with Horizontal(classes="button_row"):
                yield Button("Analyze Hand", id="analyze", variant="primary")
                yield Button("Back", id="back", variant="default")

            # Help text
            yield Static(
                "[dim]Analyzes hand strength, equity, outs, pot odds, SPR, and EV (pot/bet optional)[/dim]",
                classes="help_text",
            )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back":
            self.action_back()
        elif button_id == "analyze":
            self.action_analyze()

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()

    def action_analyze(self) -> None:
        """Perform hand analysis."""
        # Get input values
        if not self._collect_inputs():
            return

        # Validate required fields
        if not self.hero_hand or not self.board:
            self.notify("Error: Hero hand and board are required", severity="error")
            return

        # Push to analysis screen
        from .mode1_comprehensive import Mode1ComprehensiveScreen

        self.app.push_screen(
            Mode1ComprehensiveScreen(
                hero_hand=self.hero_hand,
                board=self.board,
                pot_size=self.pot_size,
                bet_to_call=self.bet_to_call,
                effective_stack=self.effective_stack,
            )
        )

    def _collect_inputs(self) -> bool:
        """
        Collect and validate all input values.

        Returns:
            True if inputs are valid, False otherwise
        """
        try:
            # Get text inputs
            hero_input = self.query_one("#hero_hand", Input)
            board_input = self.query_one("#board", Input)
            pot_input = self.query_one("#pot_size", Input)
            bet_input = self.query_one("#bet_to_call", Input)
            stack_input = self.query_one("#effective_stack", Input)

            self.hero_hand = hero_input.value.strip()
            self.board = board_input.value.strip()

            # Parse numeric inputs (optional)
            try:
                pot_value = pot_input.value.strip()
                self.pot_size = float(pot_value) if pot_value else None
            except ValueError:
                self.notify(
                    f"Error: Pot size must be a number (got '{pot_input.value}')",
                    severity="error",
                )
                return False

            try:
                bet_value = bet_input.value.strip()
                self.bet_to_call = float(bet_value) if bet_value else None
            except ValueError:
                self.notify(
                    f"Error: Bet to call must be a number (got '{bet_input.value}')",
                    severity="error",
                )
                return False

            try:
                stack_value = stack_input.value.strip()
                self.effective_stack = float(stack_value) if stack_value else None
            except ValueError:
                self.notify(
                    f"Error: Effective stack must be a number (got '{stack_input.value}')",
                    severity="error",
                )
                return False

            return True

        except Exception as e:
            self.notify(f"Error collecting inputs: {str(e)}", severity="error")
            return False
