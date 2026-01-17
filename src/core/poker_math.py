"""Poker math utilities for pot odds, SPR, EV, and equity calculations."""

from typing import Dict, Any, Optional


def calculate_pot_odds(pot_size: float, bet_to_call: float) -> float:
    """
    Calculate pot odds as a percentage.

    Args:
        pot_size: Current pot size
        bet_to_call: Amount required to call

    Returns:
        Required equity percentage to call profitably
    """
    total_pot = pot_size + bet_to_call
    pot_odds_percentage = (bet_to_call / total_pot) * 100
    return round(pot_odds_percentage, 2)


def percentage_to_ratio(percentage: float) -> str:
    """
    Convert percentage to odds ratio format.

    Args:
        percentage: Pot odds as percentage (e.g., 33.33)

    Returns:
        Ratio string (e.g., "2.0:1")
    """
    if percentage >= 100:
        return "0:1"
    if percentage <= 0:
        return "∞:1"

    odds_against = (100 - percentage) / percentage
    return f"{odds_against:.1f}:1"


def estimate_implied_odds(
    pot_size: float,
    bet_to_call: float,
    effective_stack: float,
    outs: float,
) -> Dict[str, Any]:
    """
    Estimate implied odds based on remaining stack and drawing potential.

    Args:
        pot_size: Current pot size
        bet_to_call: Amount to call
        effective_stack: Remaining effective stack after call
        outs: Number of outs

    Returns:
        Dict with implied odds percentage, ratio, and estimated future winnings
    """
    # Estimate future winnings based on outs and remaining stack
    # More outs = higher implied odds (more likely to win big pot)
    out_multiplier = min(outs / 15.0, 1.0)  # Cap at 15 outs
    estimated_future_winnings = effective_stack * out_multiplier * 0.5

    total_pot_with_implied = pot_size + bet_to_call + estimated_future_winnings
    implied_odds_percentage = (bet_to_call / total_pot_with_implied) * 100

    return {
        "percentage": round(implied_odds_percentage, 2),
        "ratio": percentage_to_ratio(implied_odds_percentage),
        "estimated_future_winnings": estimated_future_winnings,
    }


def categorize_spr(spr: float) -> str:
    """
    Categorize stack-to-pot ratio into commitment levels.

    Args:
        spr: Stack-to-pot ratio

    Returns:
        SPR category string
    """
    if spr < 3:
        return "low (committed)"
    elif spr < 7:
        return "medium"
    else:
        return "high (deep)"


def calculate_ev(
    equity: float,
    pot_size: float,
    bet_to_call: float,
    effective_stack: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate expected value of calling vs folding.

    Args:
        equity: Win equity percentage (0-100)
        pot_size: Current pot size
        bet_to_call: Amount to call
        effective_stack: Remaining stack (optional)

    Returns:
        Dict with EV calculations for call and fold
    """
    total_pot_after_call = pot_size + bet_to_call

    # EV of calling = (equity% * pot_after_call) - ((1-equity%) * bet_to_call)
    ev_call = (equity / 100 * total_pot_after_call) - ((1 - equity / 100) * bet_to_call)

    # EV of folding is always 0
    ev_fold = 0

    return {
        "call": round(ev_call, 2),
        "fold": ev_fold,
        "note": "Raise EV requires opponent modeling",
    }


def estimate_equity_from_outs(outs: float, board_size: int) -> float:
    """
    Estimate equity percentage using the rule of 2 and 4.

    Args:
        outs: Number of outs (can be fractional for backdoor draws)
        board_size: Number of cards on board (3=flop, 4=turn, 5=river)

    Returns:
        Estimated equity percentage
    """
    if board_size == 3:  # Flop - two cards to come
        equity = outs * 4
    elif board_size == 4:  # Turn - one card to come
        equity = outs * 2
    else:  # River or invalid
        equity = 0

    # Cap at 100%
    return min(round(equity, 1), 100.0)
