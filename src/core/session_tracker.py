"""Session tracker core logic for bankroll and performance analysis."""

import math
from typing import Any, Dict, List

import plotext as plt


def calculate_variance(profits: List[float]) -> float:
    """
    Calculate the variance of session profits.

    Args:
        profits: List of session profit/loss values

    Returns:
        Variance value (0 if insufficient data)
    """
    if len(profits) < 2:
        return 0.0

    mean = sum(profits) / len(profits)
    squared_diffs = [(p - mean) ** 2 for p in profits]
    return sum(squared_diffs) / (len(profits) - 1)


def calculate_standard_deviation(profits: List[float]) -> float:
    """
    Calculate standard deviation of session profits.

    Args:
        profits: List of session profit/loss values

    Returns:
        Standard deviation (0 if insufficient data)
    """
    variance = calculate_variance(profits)
    return math.sqrt(variance) if variance > 0 else 0.0


def calculate_sharpe_ratio(
    profits: List[float],
    risk_free_rate: float = 0.0,
) -> float:
    """
    Calculate Sharpe ratio for risk-adjusted returns.

    Args:
        profits: List of session profit/loss values
        risk_free_rate: Risk-free rate (default 0)

    Returns:
        Sharpe ratio (0 if insufficient data)
    """
    if len(profits) < 2:
        return 0.0

    mean_profit = sum(profits) / len(profits)
    std_dev = calculate_standard_deviation(profits)

    if std_dev == 0:
        return 0.0

    return (mean_profit - risk_free_rate) / std_dev


def calculate_max_drawdown(cumulative_profits: List[float]) -> Dict[str, float]:
    """
    Calculate maximum drawdown from peak.

    Args:
        cumulative_profits: List of cumulative profit values over time

    Returns:
        Dict with max_drawdown, max_drawdown_pct, peak, trough
    """
    if not cumulative_profits:
        return {
            "max_drawdown": 0.0,
            "max_drawdown_pct": 0.0,
            "peak": 0.0,
            "trough": 0.0,
        }

    peak = cumulative_profits[0]
    max_drawdown = 0.0
    trough = cumulative_profits[0]
    peak_at_max_dd = peak
    trough_at_max_dd = trough

    for value in cumulative_profits:
        if value > peak:
            peak = value
        drawdown = peak - value
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            peak_at_max_dd = peak
            trough_at_max_dd = value

    max_drawdown_pct = (
        (max_drawdown / peak_at_max_dd * 100) if peak_at_max_dd > 0 else 0
    )

    return {
        "max_drawdown": max_drawdown,
        "max_drawdown_pct": max_drawdown_pct,
        "peak": peak_at_max_dd,
        "trough": trough_at_max_dd,
    }


def analyze_bankroll_health(
    current_bankroll: float,
    stake_big_blind: float,
    sessions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze bankroll health and provide recommendations.

    Args:
        current_bankroll: Current total bankroll
        stake_big_blind: Big blind for the stake being played
        sessions: List of session data dicts

    Returns:
        Dict with health metrics and recommendations
    """
    if current_bankroll <= 0 or stake_big_blind <= 0:
        return {
            "buyins_available": 0,
            "risk_of_ruin": 100.0,
            "recommended_stake": "N/A",
            "health_status": "critical",
            "recommendations": ["Deposit more funds or take a break"],
        }

    # Calculate buyins available (assuming 100bb buyin)
    buyin_amount = stake_big_blind * 100
    buyins_available = current_bankroll / buyin_amount

    # Extract profits for variance calculation
    profits = [
        s.get("profit_loss", 0) for s in sessions if s.get("profit_loss") is not None
    ]

    # Calculate win rate
    if profits:
        winning_sessions = sum(1 for p in profits if p > 0)
        win_rate = winning_sessions / len(profits) * 100
    else:
        win_rate = 50.0

    # Simplified risk of ruin calculation
    # Based on win rate and bankroll in buyins
    if win_rate >= 55 and buyins_available >= 30:
        risk_of_ruin = max(0.0, 5 - (buyins_available - 30) * 0.1)
    elif win_rate >= 50:
        risk_of_ruin = max(0.0, 20 - buyins_available * 0.5)
    else:
        risk_of_ruin = min(100.0, 50 + (50 - win_rate) * 2)

    # Health status
    if buyins_available >= 30 and risk_of_ruin < 10:
        health_status = "excellent"
    elif buyins_available >= 20 and risk_of_ruin < 25:
        health_status = "good"
    elif buyins_available >= 10:
        health_status = "caution"
    else:
        health_status = "critical"

    # Recommendations
    recommendations = []

    if buyins_available < 20:
        recommendations.append(
            f"Consider moving down in stakes. You have only {buyins_available:.0f} buyins."
        )

    if buyins_available >= 50:
        recommendations.append(
            "You have enough buyins to consider moving up in stakes."
        )

    if win_rate < 45 and len(profits) >= 10:
        recommendations.append(
            f"Your win rate ({win_rate:.1f}%) suggests reviewing your strategy."
        )

    std_dev = calculate_standard_deviation(profits) if profits else 0
    if std_dev > buyin_amount * 2:
        recommendations.append("High variance detected. Consider tightening your game.")

    if not recommendations:
        recommendations.append("Bankroll looks healthy. Keep up the good work!")

    # Recommend stakes based on bankroll
    recommended_stakes = []
    common_stakes = [
        (0.01, 0.02, "NL2"),
        (0.02, 0.05, "NL5"),
        (0.05, 0.10, "NL10"),
        (0.10, 0.25, "NL25"),
        (0.25, 0.50, "NL50"),
        (0.50, 1.00, "NL100"),
        (1.00, 2.00, "1/2"),
        (2.00, 5.00, "2/5"),
        (5.00, 10.00, "5/10"),
    ]

    for sb, bb, name in common_stakes:
        stake_buyin = bb * 100
        if current_bankroll >= stake_buyin * 20:
            recommended_stakes.append(name)

    return {
        "buyins_available": buyins_available,
        "risk_of_ruin": risk_of_ruin,
        "recommended_stakes": (
            recommended_stakes[-3:] if recommended_stakes else ["Move down"]
        ),
        "health_status": health_status,
        "win_rate": win_rate if profits else None,
        "variance": calculate_variance(profits) if profits else 0,
        "std_deviation": std_dev,
        "recommendations": recommendations,
    }


def calculate_streak_info(profits: List[float]) -> Dict[str, Any]:
    """
    Calculate winning/losing streak information.

    Args:
        profits: List of session profit/loss values (in chronological order)

    Returns:
        Dict with current_streak, longest_win_streak, longest_loss_streak
    """
    if not profits:
        return {
            "current_streak": 0,
            "current_streak_type": "none",
            "longest_win_streak": 0,
            "longest_loss_streak": 0,
        }

    current_streak = 0
    current_type = "none"
    longest_win = 0
    longest_loss = 0
    temp_win = 0
    temp_loss = 0

    for profit in profits:
        if profit > 0:
            temp_win += 1
            temp_loss = 0
            longest_win = max(longest_win, temp_win)
        elif profit < 0:
            temp_loss += 1
            temp_win = 0
            longest_loss = max(longest_loss, temp_loss)
        else:
            temp_win = 0
            temp_loss = 0

    # Current streak (from the end)
    for profit in reversed(profits):
        if current_type == "none":
            if profit > 0:
                current_type = "win"
                current_streak = 1
            elif profit < 0:
                current_type = "loss"
                current_streak = 1
        elif current_type == "win" and profit > 0:
            current_streak += 1
        elif current_type == "loss" and profit < 0:
            current_streak += 1
        else:
            break

    return {
        "current_streak": current_streak,
        "current_streak_type": current_type,
        "longest_win_streak": longest_win,
        "longest_loss_streak": longest_loss,
    }


def format_currency(amount: float) -> str:
    """Format a currency amount with sign and proper formatting."""
    if amount >= 0:
        return f"+${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"


def format_duration(minutes: int) -> str:
    """Format duration in minutes to hours:minutes string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def generate_ascii_graph(
    data_points: List[Dict[str, Any]],
    width: int = 80,
    height: int = 15,
) -> List[str]:
    """
    Generate a graph for bankroll progression using plotext.

    Args:
        data_points: List of dicts with 'date' and 'cumulative' keys
        width: Width of the graph in characters
        height: Height of the graph in characters

    Returns:
        List of strings representing the graph lines
    """
    if not data_points:
        return ["No data to display"]

    values = [dp["cumulative"] for dp in data_points]
    num_sessions = len(values)
    min_val, max_val = min(values), max(values)
    current_val = values[-1]

    # Clear any previous plot
    plt.clear_figure()

    # Configure the plot
    plt.plot_size(width, height)
    plt.theme("clear")  # Use clear theme for no background colors

    # Plot the bankroll line with braille markers for smooth curves
    plt.plot(
        list(range(1, num_sessions + 1)),
        values,
        marker="braille",
    )

    # Add a zero reference line if values cross zero
    if min_val < 0 < max_val:
        plt.hline(0)

    # Labels
    plt.title(f"{num_sessions} Sessions")
    plt.xlabel("Session #")
    plt.ylabel("$")

    # Set y-axis limits with some padding
    y_range = max_val - min_val
    padding = y_range * 0.1 if y_range > 0 else 50
    plt.ylim(min_val - padding, max_val + padding)

    # Build the graph as string and remove ANSI color codes for Textual compatibility
    graph_str = plt.build()
    graph_str = plt.uncolorize(graph_str)
    lines = graph_str.split("\n")

    # Add summary with Rich markup colors (Textual compatible)
    lines.append("")
    if current_val >= 0:
        current_str = f"[green]+${current_val:,.2f}[/green]"
    else:
        current_str = f"[red]-${abs(current_val):,.2f}[/red]"

    lines.append(
        f"  Current: {current_str}  |  Peak: [green]${max_val:,.2f}[/green]  |  Low: [red]${min_val:,.2f}[/red]"
    )

    return lines


def generate_ascii_graph_simple(
    data_points: List[Dict[str, Any]],
    width: int = 50,
    height: int = 10,
) -> List[str]:
    """
    Generate simple ASCII graph for bankroll progression (fallback).

    Args:
        data_points: List of dicts with 'date' and 'cumulative' keys
        width: Width of the graph in characters
        height: Height of the graph in characters

    Returns:
        List of strings representing the graph lines
    """
    if not data_points:
        return ["No data to display"]

    values = [dp["cumulative"] for dp in data_points]
    min_val = min(values)
    max_val = max(values)
    value_range = max_val - min_val

    if value_range == 0:
        value_range = 1  # Avoid division by zero

    # Normalize values to graph height
    normalized = []
    for val in values:
        norm = int((val - min_val) / value_range * (height - 1))
        normalized.append(norm)

    # Sample points to fit width
    if len(normalized) > width:
        step = len(normalized) / width
        sampled = [normalized[int(i * step)] for i in range(width)]
    else:
        sampled = normalized

    # Build graph lines
    lines = []

    # Y-axis label
    lines.append(f"${max_val:>8,.0f} |")

    for row in range(height - 1, -1, -1):
        line = "         |"
        for col, val in enumerate(sampled):
            if val == row:
                line += "*"
            elif val > row:
                line += "|"
            else:
                line += " "
        lines.append(line)

    lines.append(f"${min_val:>8,.0f} |" + "-" * len(sampled))

    # X-axis labels
    if data_points:
        start_date = data_points[0]["date"][:10] if data_points else ""
        end_date = data_points[-1]["date"][:10] if data_points else ""
        lines.append(f"          {start_date}" + " " * (len(sampled) - 20) + end_date)

    return lines
