"""Mode 4: Session Tracker - Stats Screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Select
from textual.binding import Binding

from ...database.service import get_session_stats, get_bankroll_data, get_poker_sessions
from ...core.session_tracker import (
    analyze_bankroll_health,
    calculate_streak_info,
    calculate_max_drawdown,
    generate_ascii_graph,
)


class Mode4StatsScreen(Screen):
    """Stats and graphs screen."""

    CSS = """
    Mode4StatsScreen {
        align: center middle;
    }

    #stats_container {
        width: 95%;
        height: 90%;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    #title {
        text-align: center;
        width: 100%;
        padding: 1;
        color: $accent;
        text-style: bold;
    }

    #filter_row {
        height: 3;
        width: 100%;
        padding: 0 1;
    }

    #filter_row Select {
        width: 20;
        margin-right: 1;
    }

    #filter_row Static {
        width: auto;
        content-align: left middle;
        padding-right: 1;
    }

    #content_scroll {
        height: 1fr;
        width: 100%;
    }

    .stats_section {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $primary-lighten-2;
    }

    .section_title {
        color: $accent;
        text-style: bold;
        padding-bottom: 1;
    }

    .stats_grid {
        width: 100%;
        height: auto;
    }

    .stat_row {
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    .stat_label {
        width: 1fr;
        color: $text-muted;
    }

    .stat_value {
        width: auto;
    }

    .stat_value.positive {
        color: $success;
    }

    .stat_value.negative {
        color: $error;
    }

    .stat_value.excellent {
        color: $success;
    }

    .stat_value.good {
        color: $warning;
    }

    .stat_value.caution {
        color: $warning-darken-2;
    }

    .stat_value.critical {
        color: $error;
    }

    #graph_section {
        height: auto;
        padding: 1;
    }

    #graph_display {
        padding: 1;
        background: $surface-lighten-1;
    }

    #button_row {
        height: 3;
        width: 100%;
        align: center middle;
    }

    #button_row Button {
        margin: 0 1;
        width: 18;
    }

    .recommendation {
        color: $text;
        padding: 0 1;
    }

    .stake_item {
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the stats screen."""
        super().__init__()
        self.selected_days: int = 30

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="stats_container"):
            yield Static("[bold cyan]Stats & Analysis[/bold cyan]", id="title")

            # Filter row
            with Horizontal(id="filter_row"):
                yield Static("Time Range:")
                yield Select(
                    [
                        ("Last 7 days", "7"),
                        ("Last 30 days", "30"),
                        ("Last 90 days", "90"),
                        ("All time", "0"),
                    ],
                    id="days_select",
                    value="30",
                )

            # Scrollable content
            with VerticalScroll(id="content_scroll"):
                # Overview stats
                with Container(classes="stats_section", id="overview_section"):
                    yield Static("Overview", classes="section_title")
                    yield Static(id="overview_stats")

                # Bankroll graph
                with Container(classes="stats_section", id="graph_section"):
                    yield Static("Bankroll Progression", classes="section_title")
                    yield Static(id="graph_display")

                # Streak info
                with Container(classes="stats_section", id="streak_section"):
                    yield Static("Streaks & Variance", classes="section_title")
                    yield Static(id="streak_stats")

                # By stake breakdown
                with Container(classes="stats_section", id="stake_section"):
                    yield Static("By Stake Level", classes="section_title")
                    yield Static(id="stake_breakdown")

                # Bankroll health
                with Container(classes="stats_section", id="health_section"):
                    yield Static("Bankroll Health", classes="section_title")
                    yield Static(id="health_stats")

            # Button row
            with Horizontal(id="button_row"):
                yield Button("Refresh", id="refresh_btn", variant="default")
                yield Button("Back", id="back_btn", variant="default")

        yield Footer()

    def on_mount(self) -> None:
        """Load stats when mounted."""
        self._load_stats()

    def _load_stats(self) -> None:
        """Load and display all statistics."""
        self._update_overview()
        self._update_graph()
        self._update_streaks()
        self._update_stake_breakdown()
        self._update_health()

    def _update_overview(self) -> None:
        """Update overview statistics."""
        stats = get_session_stats(days=self.selected_days)

        total_sessions = stats.get("total_sessions", 0)
        total_profit = stats.get("total_profit", 0)
        total_hours = stats.get("total_hours", 0)
        hourly_rate = stats.get("hourly_rate", 0)
        win_rate = stats.get("win_rate", 0)
        winning = stats.get("winning_sessions", 0)
        losing = stats.get("losing_sessions", 0)
        biggest_win = stats.get("biggest_win", 0)
        biggest_loss = stats.get("biggest_loss", 0)
        avg_session = stats.get("average_session", 0)

        # Format values
        if total_profit >= 0:
            profit_text = f"[green]+${total_profit:,.2f}[/green]"
        else:
            profit_text = f"[red]-${abs(total_profit):,.2f}[/red]"

        if hourly_rate >= 0:
            hourly_text = f"[green]+${hourly_rate:,.2f}/hr[/green]"
        else:
            hourly_text = f"[red]-${abs(hourly_rate):,.2f}/hr[/red]"

        if avg_session >= 0:
            avg_text = f"[green]+${avg_session:,.2f}[/green]"
        else:
            avg_text = f"[red]-${abs(avg_session):,.2f}[/red]"

        text = (
            f"Total Sessions: {total_sessions}\n"
            f"Total Profit: {profit_text}\n"
            f"Total Hours: {total_hours:,.1f}\n"
            f"Hourly Rate: {hourly_text}\n"
            f"Win Rate: {win_rate:.1f}% ({winning}W / {losing}L)\n"
            f"Avg Session: {avg_text}\n"
            f"Biggest Win: [green]+${biggest_win:,.2f}[/green]\n"
            f"Biggest Loss: [red]-${abs(biggest_loss):,.2f}[/red]"
        )

        self.query_one("#overview_stats", Static).update(text)

    def _update_graph(self) -> None:
        """Update the bankroll graph."""
        # Use days=0 for all time to get all sessions
        bankroll = get_bankroll_data(days=self.selected_days)
        data_points = bankroll.get("data_points", [])

        if not data_points:
            self.query_one("#graph_display", Static).update(
                "[dim]No data to display - log some sessions first![/dim]"
            )
            return

        # Generate ASCII graph - use larger size for better readability
        graph_lines = generate_ascii_graph(data_points, width=80, height=15)
        graph_text = "\n".join(graph_lines)

        self.query_one("#graph_display", Static).update(graph_text)

    def _update_streaks(self) -> None:
        """Update streak and variance information."""
        sessions = get_poker_sessions(days=self.selected_days)
        profits = [s.get("profit_loss", 0) for s in reversed(sessions)]  # Chronological

        streak_info = calculate_streak_info(profits)

        current_streak = streak_info.get("current_streak", 0)
        streak_type = streak_info.get("current_streak_type", "none")
        longest_win = streak_info.get("longest_win_streak", 0)
        longest_loss = streak_info.get("longest_loss_streak", 0)

        # Format current streak
        if streak_type == "win":
            streak_text = f"[green]{current_streak} winning sessions[/green]"
        elif streak_type == "loss":
            streak_text = f"[red]{current_streak} losing sessions[/red]"
        else:
            streak_text = "No streak"

        # Calculate cumulative for drawdown
        cumulative = []
        total = 0
        for p in profits:
            total += p
            cumulative.append(total)

        drawdown = calculate_max_drawdown(cumulative)
        max_dd = drawdown.get("max_drawdown", 0)
        max_dd_pct = drawdown.get("max_drawdown_pct", 0)

        text = (
            f"Current Streak: {streak_text}\n"
            f"Longest Win Streak: [green]{longest_win} sessions[/green]\n"
            f"Longest Loss Streak: [red]{longest_loss} sessions[/red]\n"
            f"Max Drawdown: [red]-${max_dd:,.2f}[/red] ({max_dd_pct:.1f}% from peak)"
        )

        self.query_one("#streak_stats", Static).update(text)

    def _update_stake_breakdown(self) -> None:
        """Update stake level breakdown."""
        stats = get_session_stats(days=self.selected_days)
        by_stake = stats.get("by_stake", {})

        if not by_stake:
            self.query_one("#stake_breakdown", Static).update(
                "[dim]No stake data available[/dim]"
            )
            return

        lines: list[str] = []
        for stake, data in sorted(by_stake.items()):
            sessions = data.get("sessions", 0)
            profit = data.get("profit", 0)
            hours = data.get("hours", 0)
            hourly = profit / hours if hours > 0 else 0

            if profit >= 0:
                profit_text = f"[green]+${profit:,.2f}[/green]"
                hourly_text = f"[green]+${hourly:,.2f}/hr[/green]"
            else:
                profit_text = f"[red]-${abs(profit):,.2f}[/red]"
                hourly_text = f"[red]-${abs(hourly):,.2f}/hr[/red]"

            lines.append(
                f"{stake}: {sessions} sessions | {profit_text} | {hourly_text}"
            )

        self.query_one("#stake_breakdown", Static).update("\n".join(lines))

    def _update_health(self) -> None:
        """Update bankroll health analysis."""
        sessions = get_poker_sessions(days=90)

        if not sessions:
            self.query_one("#health_stats", Static).update(
                "[dim]Not enough data for bankroll analysis[/dim]"
            )
            return

        # Get most common stake for analysis
        stakes = [s.get("stake_level", "") for s in sessions]
        if stakes:
            most_common = max(set(stakes), key=stakes.count)
        else:
            most_common = "1/2"

        # Parse BB from stake
        try:
            if "/" in most_common:
                bb = float(most_common.split("/")[1])
            elif most_common.upper().startswith("NL"):
                bb = float(most_common[2:]) / 100
            else:
                bb = 2.0  # Default
        except (ValueError, IndexError):
            bb = 2.0

        # Calculate current bankroll (sum of all profits as proxy)
        total_profit = sum(s.get("profit_loss", 0) for s in sessions)
        # Assume some starting bankroll for analysis
        estimated_bankroll = max(1000, abs(total_profit) * 3)

        health = analyze_bankroll_health(
            current_bankroll=estimated_bankroll,
            stake_big_blind=bb,
            sessions=sessions,
        )

        buyins = health.get("buyins_available", 0)
        ror = health.get("risk_of_ruin", 0)
        status = health.get("health_status", "unknown")
        recommendations = health.get("recommendations", [])
        recommended_stakes = health.get("recommended_stakes", [])

        # Color code status
        status_colors = {
            "excellent": "green",
            "good": "yellow",
            "caution": "orange3",
            "critical": "red",
        }
        status_color = status_colors.get(status, "white")

        lines = [
            f"Health Status: [{status_color}]{status.upper()}[/{status_color}]",
            f"Buyins Available: {buyins:.0f} (at {most_common})",
            f"Risk of Ruin: {ror:.1f}%",
            "",
            f"Recommended Stakes: {', '.join(recommended_stakes) if recommended_stakes else 'N/A'}",
            "",
            "[bold]Recommendations:[/bold]",
        ]

        for rec in recommendations:
            lines.append(f"  - {rec}")

        self.query_one("#health_stats", Static).update("\n".join(lines))

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter changes."""
        if event.select.id == "days_select":
            value = str(event.value) if event.value else "30"
            self.selected_days = int(value)
            self._load_stats()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "refresh_btn":
            self.action_refresh()

    def action_back(self) -> None:
        """Return to session tracker menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh all statistics."""
        self._load_stats()
        self.notify("Stats refreshed")
