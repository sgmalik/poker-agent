"""Mode 2: Range Tools - Matrix Display Screen."""

from typing import Optional, List
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...core.gto_charts import GTOCharts, RANKS


class Mode2MatrixScreen(Screen):
    """Display 13x13 hand range matrix."""

    CSS = """
    Mode2MatrixScreen {
        background: $surface;
    }

    VerticalScroll {
        width: 100%;
        height: 100%;
        padding: 0 1;
    }

    .title {
        text-align: center;
        width: 100%;
        padding: 1 0;
        color: $accent;
        text-style: bold;
    }

    .subtitle {
        text-align: center;
        width: 100%;
        padding: 0 0 1 0;
        color: $text-muted;
    }

    #matrix_container {
        width: 100%;
        height: auto;
        align: center top;
        padding: 0;
    }

    .matrix_row {
        width: auto;
        height: 1;
        align: center middle;
    }

    .cell {
        width: 4;
        height: 1;
        text-align: center;
        content-align: center middle;
    }

    .header_cell {
        width: 4;
        height: 1;
        text-align: center;
        content-align: center middle;
        color: $accent;
        text-style: bold;
    }

    .pair {
        background: #442222;
        color: #aa8888;
    }

    .pair.in_range {
        background: #ff4444;
        color: black;
        text-style: bold;
    }

    .suited {
        background: #224422;
        color: #88aa88;
    }

    .suited.in_range {
        background: #44dd44;
        color: black;
        text-style: bold;
    }

    .offsuit {
        background: #222244;
        color: #8888aa;
    }

    .offsuit.in_range {
        background: #4488ff;
        color: black;
        text-style: bold;
    }

    .summary {
        width: 100%;
        height: auto;
        padding: 1;
        margin-top: 1;
        border: solid $primary;
    }

    .summary_line {
        width: 100%;
        padding: 0;
    }

    .legend {
        width: 100%;
        height: auto;
        padding: 1 0;
        align: center middle;
    }

    .legend_item {
        width: auto;
        padding: 0 2;
    }

    .buttons {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
    ]

    def __init__(
        self,
        position: Optional[str] = None,
        action: Optional[str] = None,
        custom_range: Optional[str] = None,
    ) -> None:
        """
        Initialize matrix screen.

        Args:
            position: GTO position (e.g., "BTN")
            action: GTO action (e.g., "open")
            custom_range: Custom range notation string
        """
        super().__init__()
        self.position = position
        self.action = action
        self.custom_range = custom_range
        self.charts = GTOCharts()

        # Load range data
        self.hands: List[str] = []
        self.notation: str = ""
        self.total_combos: int = 0
        self.percentage: float = 0.0
        self.matrix: List[List[bool]] = [[False] * 13 for _ in range(13)]

        self._load_range()

    def _load_range(self) -> None:
        """Load the range data."""
        if self.custom_range:
            # Parse custom range
            result = self.charts.parse_custom_range(self.custom_range)
            self.hands = result.get("hands", [])
            self.notation = self.custom_range
            self.total_combos = result.get("total_combos", 0)
            self.percentage = result.get("percentage", 0.0)
        elif self.position and self.action:
            # Load GTO range
            range_data = self.charts.get_range(self.position, self.action)
            if range_data:
                self.hands = range_data.get("hands", [])
                self.notation = range_data.get("notation", "")
                self.total_combos = range_data.get("total_combos", 0)
                self.percentage = range_data.get("percentage", 0.0)

        # Convert to matrix
        self.matrix = self.charts.hands_to_matrix(self.hands)

    def compose(self) -> ComposeResult:
        """Create widgets."""
        yield Header()

        with VerticalScroll():
            # Title
            if self.custom_range:
                yield Static("[bold cyan]Custom Range[/bold cyan]", classes="title")
            else:
                title = (
                    f"[bold cyan]{self.position} {self._format_action()}[/bold cyan]"
                )
                yield Static(title, classes="title")

            yield Static(
                f"{self.total_combos} combos ({self.percentage}%)", classes="subtitle"
            )

            # Matrix container
            with Container(id="matrix_container"):
                # Header row with rank labels
                header_cells = "    " + "".join(f" {r}  " for r in RANKS)
                yield Static(header_cells, classes="matrix_row")

                # Matrix rows
                for row in range(13):
                    row_widgets = self._create_matrix_row(row)
                    with Horizontal(classes="matrix_row"):
                        for widget in row_widgets:
                            yield widget

            # Legend
            with Horizontal(classes="legend"):
                yield Static("[on red] PP [/] Pairs", classes="legend_item")
                yield Static("[on green] s [/] Suited", classes="legend_item")
                yield Static("[on blue] o [/] Offsuit", classes="legend_item")

            # Summary section
            with Container(classes="summary"):
                yield Static(
                    f"[bold]Notation:[/bold] {self.notation}", classes="summary_line"
                )
                yield Static(
                    f"[bold]Hands in range:[/bold] {len(self.hands)} unique hands",
                    classes="summary_line",
                )
                yield Static(
                    f"[bold]Total combos:[/bold] {self.total_combos} / 1326 ({self.percentage}%)",
                    classes="summary_line",
                )

            # Buttons
            with Container(classes="buttons"):
                yield Button("New Range", id="new_range", variant="primary")
                yield Button("Main Menu", id="main_menu", variant="default")

        yield Footer()

    def _create_matrix_row(self, row: int) -> List[Static]:
        """Create widgets for a matrix row."""
        widgets = []

        # Row label
        widgets.append(Static(f" {RANKS[row]} ", classes="header_cell"))

        # Cells
        for col in range(13):
            hand = self.charts.get_matrix_hand(row, col)
            in_range = self.matrix[row][col]

            # Determine cell type
            if row == col:
                cell_type = "pair"
            elif row < col:
                cell_type = "suited"
            else:
                cell_type = "offsuit"

            # Create cell with appropriate styling
            classes = f"cell {cell_type}"
            if in_range:
                classes += " in_range"

            # Display hand name (shortened for offsuit)
            display = hand[:2] if len(hand) == 2 else hand
            widgets.append(Static(display, classes=classes))

        return widgets

    def _format_action(self) -> str:
        """Format action name for display."""
        if not self.action:
            return ""

        if self.action == "open":
            return "Open Range"
        elif self.action == "call_vs_BTN":
            return "Call vs BTN"
        elif self.action == "3bet_vs_BTN":
            return "3-bet vs BTN"
        else:
            return self.action.replace("_", " ").title()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new_range":
            self.action_back()
        elif event.button.id == "main_menu":
            self.action_quit()

    def action_back(self) -> None:
        """Return to input screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()
        self.app.pop_screen()
