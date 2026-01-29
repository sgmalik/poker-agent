"""Tests for session tracker core logic."""

import pytest

from src.core.session_tracker import (
    calculate_variance,
    calculate_standard_deviation,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    analyze_bankroll_health,
    calculate_streak_info,
    format_currency,
    format_duration,
    generate_ascii_graph,
)


class TestVarianceCalculations:
    """Tests for variance and standard deviation calculations."""

    def test_variance_empty_list(self):
        """Should return 0 for empty list."""
        assert calculate_variance([]) == 0.0

    def test_variance_single_value(self):
        """Should return 0 for single value."""
        assert calculate_variance([100]) == 0.0

    def test_variance_identical_values(self):
        """Should return 0 for identical values."""
        assert calculate_variance([50, 50, 50, 50]) == 0.0

    def test_variance_simple_case(self):
        """Should calculate variance correctly."""
        # Values: [2, 4, 4, 4, 5, 5, 7, 9], Mean = 5
        # Variance = sum((x-5)^2) / (n-1)
        profits = [2, 4, 4, 4, 5, 5, 7, 9]
        variance = calculate_variance(profits)
        # Expected: (9+1+1+1+0+0+4+16) / 7 = 32/7 = 4.57
        assert variance == pytest.approx(4.57, rel=0.1)

    def test_std_deviation(self):
        """Should calculate standard deviation correctly."""
        profits = [2, 4, 4, 4, 5, 5, 7, 9]
        std = calculate_standard_deviation(profits)
        # sqrt(4.57) = ~2.14
        assert std == pytest.approx(2.14, rel=0.1)

    def test_std_deviation_empty(self):
        """Should return 0 for empty list."""
        assert calculate_standard_deviation([]) == 0.0


class TestSharpeRatio:
    """Tests for Sharpe ratio calculation."""

    def test_sharpe_ratio_empty(self):
        """Should return 0 for insufficient data."""
        assert calculate_sharpe_ratio([]) == 0.0
        assert calculate_sharpe_ratio([100]) == 0.0

    def test_sharpe_ratio_no_variance(self):
        """Should return 0 when standard deviation is 0."""
        assert calculate_sharpe_ratio([50, 50, 50]) == 0.0

    def test_sharpe_ratio_positive(self):
        """Should calculate positive Sharpe ratio."""
        # Mean = 100, StdDev = some value
        profits = [80, 100, 120, 90, 110]
        sharpe = calculate_sharpe_ratio(profits)
        assert sharpe > 0  # Positive mean, positive Sharpe


class TestMaxDrawdown:
    """Tests for maximum drawdown calculation."""

    def test_drawdown_empty(self):
        """Should return zeros for empty data."""
        result = calculate_max_drawdown([])
        assert result["max_drawdown"] == 0.0
        assert result["max_drawdown_pct"] == 0.0

    def test_drawdown_no_decline(self):
        """Should return 0 when bankroll only goes up."""
        result = calculate_max_drawdown([100, 200, 300, 400])
        assert result["max_drawdown"] == 0.0

    def test_drawdown_simple_case(self):
        """Should calculate drawdown correctly."""
        # Peak at 500, drops to 300, then recovers
        result = calculate_max_drawdown([100, 300, 500, 400, 300, 450])
        assert result["max_drawdown"] == 200.0  # 500 - 300
        assert result["peak"] == 500.0
        assert result["trough"] == 300.0

    def test_drawdown_percentage(self):
        """Should calculate drawdown percentage correctly."""
        # Peak at 1000, drops to 700
        result = calculate_max_drawdown([500, 1000, 700, 800])
        assert result["max_drawdown_pct"] == pytest.approx(30.0, rel=0.1)


class TestBankrollHealth:
    """Tests for bankroll health analysis."""

    def test_health_zero_bankroll(self):
        """Should return critical status for zero bankroll."""
        result = analyze_bankroll_health(
            current_bankroll=0,
            stake_big_blind=2,
            sessions=[],
        )
        assert result["health_status"] == "critical"
        assert result["risk_of_ruin"] == 100.0

    def test_health_excellent_bankroll(self):
        """Should return excellent status for large bankroll."""
        # 50 buyins at 1/2 ($100 buyin)
        result = analyze_bankroll_health(
            current_bankroll=5000,
            stake_big_blind=2,
            sessions=[
                {"profit_loss": 100},
                {"profit_loss": 50},
                {"profit_loss": -30},
                {"profit_loss": 80},
                {"profit_loss": 40},
            ],
        )
        assert result["buyins_available"] == 25.0  # 5000 / 200
        assert result["health_status"] in ["excellent", "good"]

    def test_health_recommendations(self):
        """Should provide recommendations."""
        result = analyze_bankroll_health(
            current_bankroll=1000,
            stake_big_blind=5,  # 2/5 game, $500 buyin
            sessions=[],
        )
        assert len(result["recommendations"]) > 0

    def test_health_recommended_stakes(self):
        """Should recommend appropriate stakes."""
        result = analyze_bankroll_health(
            current_bankroll=5000,
            stake_big_blind=2,
            sessions=[],
        )
        # Should recommend some stakes
        assert len(result["recommended_stakes"]) > 0


class TestStreakInfo:
    """Tests for streak calculation."""

    def test_streak_empty(self):
        """Should return zeros for empty data."""
        result = calculate_streak_info([])
        assert result["current_streak"] == 0
        assert result["current_streak_type"] == "none"
        assert result["longest_win_streak"] == 0
        assert result["longest_loss_streak"] == 0

    def test_streak_all_wins(self):
        """Should track all wins correctly."""
        result = calculate_streak_info([100, 50, 25, 75])
        assert result["current_streak"] == 4
        assert result["current_streak_type"] == "win"
        assert result["longest_win_streak"] == 4
        assert result["longest_loss_streak"] == 0

    def test_streak_all_losses(self):
        """Should track all losses correctly."""
        result = calculate_streak_info([-100, -50, -25, -75])
        assert result["current_streak"] == 4
        assert result["current_streak_type"] == "loss"
        assert result["longest_loss_streak"] == 4
        assert result["longest_win_streak"] == 0

    def test_streak_mixed(self):
        """Should track mixed streaks correctly."""
        # W, W, W, L, L, W, W
        result = calculate_streak_info([100, 50, 25, -50, -25, 75, 30])
        assert result["current_streak"] == 2
        assert result["current_streak_type"] == "win"
        assert result["longest_win_streak"] == 3
        assert result["longest_loss_streak"] == 2

    def test_streak_ends_with_loss(self):
        """Should track current losing streak."""
        result = calculate_streak_info([100, 50, -25, -50, -75])
        assert result["current_streak"] == 3
        assert result["current_streak_type"] == "loss"


class TestFormatFunctions:
    """Tests for formatting utility functions."""

    def test_format_currency_positive(self):
        """Should format positive currency correctly."""
        assert format_currency(100) == "+$100.00"
        assert format_currency(1234.56) == "+$1,234.56"

    def test_format_currency_negative(self):
        """Should format negative currency correctly."""
        assert format_currency(-100) == "-$100.00"
        assert format_currency(-1234.56) == "-$1,234.56"

    def test_format_currency_zero(self):
        """Should format zero correctly."""
        assert format_currency(0) == "+$0.00"

    def test_format_duration_minutes(self):
        """Should format short durations correctly."""
        assert format_duration(30) == "30m"
        assert format_duration(45) == "45m"

    def test_format_duration_hours(self):
        """Should format hour durations correctly."""
        assert format_duration(60) == "1h"
        assert format_duration(120) == "2h"

    def test_format_duration_hours_minutes(self):
        """Should format mixed durations correctly."""
        assert format_duration(90) == "1h 30m"
        assert format_duration(135) == "2h 15m"


class TestAsciiGraph:
    """Tests for ASCII graph generation."""

    def test_graph_empty(self):
        """Should handle empty data."""
        result = generate_ascii_graph([])
        assert result == ["No data to display"]

    def test_graph_single_point(self):
        """Should handle single data point."""
        data = [{"date": "2025-01-15", "cumulative": 100}]
        result = generate_ascii_graph(data, width=10, height=5)
        assert len(result) > 0
        assert any("$" in line for line in result)

    def test_graph_multiple_points(self):
        """Should generate graph with multiple points."""
        data = [
            {"date": "2025-01-15", "cumulative": 100},
            {"date": "2025-01-16", "cumulative": 200},
            {"date": "2025-01-17", "cumulative": 150},
            {"date": "2025-01-18", "cumulative": 300},
        ]
        result = generate_ascii_graph(data, width=40, height=10)
        assert len(result) > 5  # Should have multiple lines
        # Should contain plotext graph elements (title or axis labels)
        full_output = "\n".join(result)
        assert "Bankroll" in full_output or "Session" in full_output

    def test_graph_negative_values(self):
        """Should handle negative values."""
        data = [
            {"date": "2025-01-15", "cumulative": -100},
            {"date": "2025-01-16", "cumulative": -50},
            {"date": "2025-01-17", "cumulative": 0},
        ]
        result = generate_ascii_graph(data, width=15, height=6)
        assert len(result) > 0
