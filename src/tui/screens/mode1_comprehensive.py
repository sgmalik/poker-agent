"""Mode 1: Comprehensive Analysis Screen."""

from typing import Optional, Dict, Any
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from ...core.spot_analyzer import SpotAnalyzer


class Mode1ComprehensiveScreen(Screen):
    """Display comprehensive hand analysis."""

    CSS = """
    Mode1ComprehensiveScreen {
        background: $surface;
    }

    VerticalScroll {
        width: 100%;
        height: 100%;
        padding: 0 2;
    }

    .title {
        text-align: center;
        width: 100%;
        padding: 1 0;
        color: $accent;
        text-style: bold;
    }

    .cards {
        text-align: center;
        width: 100%;
        padding: 0;
    }

    .section {
        width: 100%;
        height: auto;
        padding: 0 1;
        margin: 0;
        border: solid $primary;
    }

    .section-title {
        color: $accent;
        text-style: bold;
        padding: 0;
        margin: 0;
    }

    .line {
        width: 100%;
        padding: 0;
        margin: 0;
    }

    .recommendation {
        width: 100%;
        height: auto;
        padding: 1;
        margin: 0;
        border: solid $success;
        background: $boost;
    }

    .rec-action {
        text-align: center;
        color: $success;
        text-style: bold;
        padding: 0;
        margin: 0;
    }

    .error {
        color: $error;
        text-align: center;
        padding: 1;
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
        hero_hand: str,
        board: str,
        pot_size: Optional[float] = None,
        bet_to_call: Optional[float] = None,
        effective_stack: Optional[float] = None,
    ) -> None:
        """Initialize analysis screen."""
        super().__init__()
        self.hero_hand = hero_hand
        self.board = board
        self.pot_size = pot_size
        self.bet_to_call = bet_to_call
        self.effective_stack = effective_stack
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self._analyze()

    def _analyze(self) -> None:
        """Run the analysis."""
        try:
            analyzer = SpotAnalyzer()
            self.result = analyzer.analyze(
                hero_hand=self.hero_hand,
                board=self.board,
                pot_size=self.pot_size,
                bet_to_call=self.bet_to_call,
                effective_stack=self.effective_stack,
            )
        except Exception as e:
            self.error = str(e)

    def compose(self) -> ComposeResult:
        """Create widgets."""
        yield Header()

        with VerticalScroll():
            yield Static("[bold cyan]Hand Analysis[/bold cyan]", classes="title")

            if self.error:
                yield Static(
                    f"[bold red]Error:[/bold red] {self.error}", classes="error"
                )
            elif self.result:
                # Cards
                yield Static(f"Hero: {self._fmt(self.hero_hand)}", classes="cards")
                yield Static(f"Board: {self._fmt(self.board)}", classes="cards")

                # Situation info
                if self.pot_size or self.bet_to_call or self.effective_stack:
                    info = []
                    if self.pot_size:
                        info.append(f"Pot: ${self.pot_size}")
                    if self.bet_to_call:
                        info.append(f"Bet: ${self.bet_to_call}")
                    if self.effective_stack:
                        info.append(f"Stack: ${self.effective_stack}")
                    yield Static(" | ".join(info), classes="cards")

                # Hand Strength
                with Container(classes="section"):
                    yield Static("HAND STRENGTH", classes="section-title")
                    yield Static(
                        self.result["hand_strength"]["description"], classes="line"
                    )

                # Equity & Outs
                with Container(classes="section"):
                    yield Static("EQUITY & OUTS", classes="section-title")
                    yield Static(f"Equity: {self.result['equity']}%", classes="line")
                    yield Static(
                        f"Total Outs: {self.result['out_count']}", classes="line"
                    )

                    outs = self.result.get("outs", {})
                    flush = outs.get("flush_draw", {})
                    if flush.get("count", 0) > 0:
                        flush_type = (
                            "Backdoor Flush"
                            if flush.get("type") == "backdoor_flush"
                            else "Flush Draw"
                        )
                        yield Static(
                            f"  • {flush_type}: {flush['count']} outs", classes="line"
                        )

                    straight = outs.get("straight_draw", {})
                    if straight.get("count", 0) > 0:
                        yield Static(
                            f"  • Straight ({straight.get('type', '')}): {straight['count']} outs",
                            classes="line",
                        )

                    overcards = outs.get("overcards", {})
                    if overcards.get("count", 0) > 0:
                        yield Static(
                            f"  • Overcards: {overcards['count']} outs", classes="line"
                        )

                # Pot Odds (if available)
                if self.result.get("pot_odds"):
                    with Container(classes="section"):
                        yield Static("POT ODDS", classes="section-title")
                        po = self.result["pot_odds"]
                        yield Static(
                            f"Required Equity: {po['percentage']}% ({po['ratio']})",
                            classes="line",
                        )
                        yield Static(
                            f"Your Equity: {self.result['equity']}%", classes="line"
                        )
                        if self.result["equity"] >= po["percentage"]:
                            yield Static(
                                "✓ Profitable to call (direct odds)", classes="line"
                            )
                        else:
                            yield Static(
                                "✗ Not profitable (direct odds)", classes="line"
                            )

                # SPR (if available)
                if self.result.get("spr") is not None:
                    with Container(classes="section"):
                        yield Static("STACK CONSIDERATIONS", classes="section-title")
                        yield Static(
                            f"SPR: {self.result['spr']} ({self.result['spr_category']})",
                            classes="line",
                        )

                # EV (if available)
                if self.result.get("ev"):
                    with Container(classes="section"):
                        yield Static("EXPECTED VALUE", classes="section-title")
                        ev = self.result["ev"]
                        if ev["call"] > 0:
                            yield Static(
                                f"EV of Call: [green]+${ev['call']:.2f}[/green]",
                                classes="line",
                            )
                        else:
                            yield Static(
                                f"EV of Call: [red]${ev['call']:.2f}[/red]",
                                classes="line",
                            )
                        yield Static(f"EV of Fold: ${ev['fold']:.2f}", classes="line")

                # Recommendation
                rec = self.result.get("recommendation", {})
                with Container(classes="recommendation"):
                    action = rec.get("action", "UNKNOWN")
                    if action == "ANALYZE":
                        yield Static("HAND ANALYSIS", classes="rec-action")
                        yield Static(
                            "Provide pot/bet for action recommendation", classes="line"
                        )
                    else:
                        yield Static(f"RECOMMENDATION: {action}", classes="rec-action")
                        for reason in rec.get("reasoning", []):
                            yield Static(f"• {reason}", classes="line")

            # Buttons
            with Container(classes="buttons"):
                yield Button("New Hand", id="new_hand", variant="primary")
                yield Button("Main Menu", id="main_menu", variant="default")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new_hand":
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

    def _fmt(self, cards: str) -> str:
        """Format cards with suit symbols."""
        suits = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
        result: list[str] = []
        for card in cards.split():
            if len(card) == 2:
                result.append(f"{card[0].upper()}{suits.get(card[1].lower(), card[1])}")
            else:
                result.append(card)
        return " ".join(result)
