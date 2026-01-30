"""LangChain tools for hand evaluation and spot analysis (Mode 1)."""

from typing import Any, Optional

from langchain_core.tools import tool

from ..core.hand_evaluator import HandEvaluator, EquityCalculator
from ..core.spot_analyzer import SpotAnalyzer


@tool
def evaluate_hand(hero_hand: str, board: str) -> dict[str, Any]:
    """
    Evaluate the strength of a poker hand.

    Args:
        hero_hand: The player's two hole cards (e.g., "As Kh" for Ace of spades, King of hearts)
        board: The community cards, 3-5 cards (e.g., "Qh Jh 2c" for flop or "Qh Jh 2c 5d 9s" for river)

    Returns:
        Dictionary containing:
        - hand_class: The hand type (e.g., "Flush", "Two Pair", "High Card")
        - rank: Numeric rank (lower is better, 1 = royal flush)
        - description: Human-readable description of the hand

    Example:
        evaluate_hand("As Ks", "Qs Js Ts") -> {"hand_class": "Straight Flush", ...}
    """
    try:
        evaluator = HandEvaluator()
        result = evaluator.evaluate(hero_hand, board)
        return {
            "success": True,
            "hand_class": result["hand_class"],
            "rank": result["rank"],
            "description": result["description"],
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@tool
def calculate_equity(
    hero_hand: str,
    villain_hand: str,
    board: str = "",
    iterations: int = 10000,
) -> dict[str, Any]:
    """
    Calculate equity (win probability) between two hands using Monte Carlo simulation.

    Args:
        hero_hand: Your two hole cards (e.g., "As Ad" for pocket aces)
        villain_hand: Opponent's two hole cards (e.g., "Kh Kd" for pocket kings)
        board: Current community cards, empty string for preflop (e.g., "" or "Ah 7s 2c")
        iterations: Number of simulations to run (default 10000, higher = more accurate)

    Returns:
        Dictionary containing:
        - hero_equity: Your win probability as percentage (0-100)
        - villain_equity: Opponent's win probability as percentage (0-100)
        - hero_wins: Number of simulated wins for hero
        - villain_wins: Number of simulated wins for villain
        - ties: Number of ties

    Example:
        calculate_equity("As Ad", "Kh Kd", "") -> {"hero_equity": 81.5, "villain_equity": 18.5, ...}
    """
    try:
        calculator = EquityCalculator()
        result = calculator.calculate(hero_hand, villain_hand, board, iterations)
        return {
            "success": True,
            "hero_equity": result["hero_equity"],
            "villain_equity": result["villain_equity"],
            "hero_wins": result["hero_wins"],
            "villain_wins": result["villain_wins"],
            "ties": result["ties"],
            "iterations": result["iterations"],
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@tool
def analyze_spot(
    hero_hand: str,
    board: str,
    pot_size: Optional[float] = None,
    bet_to_call: Optional[float] = None,
    effective_stack: Optional[float] = None,
) -> dict[str, Any]:
    """
    Perform comprehensive analysis of a poker spot including hand strength, equity, outs, pot odds, and EV.

    Args:
        hero_hand: Your two hole cards (e.g., "Ah Kh" for suited ace-king)
        board: Community cards, 3-5 cards (e.g., "Qh Jh 2c" for a flush draw board)
        pot_size: Current pot size in chips/dollars (optional, needed for pot odds)
        bet_to_call: Amount you need to call (optional, needed for pot odds)
        effective_stack: Your remaining stack size (optional, for SPR and implied odds)

    Returns:
        Dictionary containing:
        - hand_strength: Hand type and description
        - equity: Estimated win probability
        - outs: Breakdown of drawing outs (flush draw, straight draw, overcards)
        - pot_odds: Required equity to call profitably (if pot_size and bet_to_call provided)
        - implied_odds: Estimated implied odds (if all bet info provided)
        - spr: Stack-to-pot ratio (if pot_size and effective_stack provided)
        - ev: Expected value of call vs fold (if bet info provided)
        - recommendation: Suggested action (CALL, FOLD, or ANALYZE) with reasoning

    Example:
        analyze_spot("Ah Kh", "Qh Jh 2c", pot_size=100, bet_to_call=50, effective_stack=500)
        -> {"recommendation": {"action": "CALL", "reasoning": ["Flush draw with 9 outs", ...]}, ...}
    """
    try:
        analyzer = SpotAnalyzer()
        result = analyzer.analyze(
            hero_hand=hero_hand,
            board=board,
            pot_size=pot_size,
            bet_to_call=bet_to_call,
            effective_stack=effective_stack,
        )

        # Simplify the result for the AI agent
        return {
            "success": True,
            "hand_strength": result["hand_strength"],
            "equity": result["equity"],
            "equity_method": result.get("equity_method", "outs_estimation"),
            "out_count": result["out_count"],
            "outs": result["outs"],
            "pot_odds": result.get("pot_odds"),
            "implied_odds": result.get("implied_odds"),
            "spr": result.get("spr"),
            "spr_category": result.get("spr_category"),
            "ev": result.get("ev"),
            "recommendation": result["recommendation"],
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# Export all tools
HAND_EVAL_TOOLS = [evaluate_hand, calculate_equity, analyze_spot]
