"""
Comprehensive poker spot analysis with pot odds, SPR, EV, and outs calculation.

This module provides detailed analysis of poker situations including:
- Pot odds and implied odds
- Stack-to-pot ratio (SPR)
- Expected value (EV) calculations
- Out counting and equity
- Decision recommendations
"""

from typing import Any, Dict, List, Optional
from treys import Card, Evaluator

from .hand_evaluator import HandEvaluator, EquityCalculator
from .outs_calculator import OutsCalculator
from . import poker_math


class SpotAnalyzer:
    """Comprehensive poker spot analysis with all poker math."""

    def __init__(self):
        """Initialize spot analyzer with required components."""
        self.hand_evaluator = HandEvaluator()
        self.equity_calculator = EquityCalculator()
        self.outs_calculator = OutsCalculator()
        self.evaluator = Evaluator()

    def analyze(
        self,
        hero_hand: str,
        board: str,
        pot_size: Optional[float] = None,
        bet_to_call: Optional[float] = None,
        effective_stack: Optional[float] = None,
        villain_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive spot analysis.

        Args:
            hero_hand: Hero's cards (e.g., "As Kh")
            board: Current board cards (e.g., "Ah 7s 2c")
            pot_size: Current pot size in chips/dollars
            bet_to_call: Amount hero needs to call
            effective_stack: Effective stack size remaining
            villain_range: Villain's estimated range (optional, for future)

        Returns:
            Dictionary containing:
                - hand_strength: Current hand evaluation
                - equity: Win probability estimate
                - outs: List of improving cards
                - pot_odds: Required equity to call (percentage)
                - implied_odds: Estimated implied odds
                - spr: Stack-to-pot ratio
                - ev: Expected value calculations (call/fold/raise)
                - recommendation: Action recommendation with reasoning

        Example:
            >>> analyzer = SpotAnalyzer()
            >>> result = analyzer.analyze(
            ...     "Ah Kh", "Qh Jh 2c",
            ...     pot_size=100, bet_to_call=50, effective_stack=500
            ... )
            >>> print(result['recommendation'])
        """
        # Basic validation
        hero_cards = self._parse_cards(hero_hand)
        board_cards = self._parse_cards(board) if board else []

        if len(hero_cards) != 2:
            raise ValueError("Hero hand must have exactly 2 cards")
        if len(board_cards) < 3 or len(board_cards) > 5:
            raise ValueError("Board must have 3-5 cards")

        result: Dict[str, Any] = {}

        # 1. Hand strength evaluation
        hand_eval = self.hand_evaluator.evaluate(hero_hand, board)
        result["hand_strength"] = {
            "class": hand_eval["hand_class"],
            "rank": hand_eval["rank"],
            "description": hand_eval["description"],
        }

        # 2. Calculate outs and equity
        outs_data = self.outs_calculator.calculate_outs(hero_cards, board_cards)
        result["outs"] = outs_data["breakdown"]
        result["out_count"] = outs_data["count"]
        result["unknown_cards"] = outs_data["unknown_cards"]

        # Calculate equity (estimate based on outs if no villain hand specified)
        if villain_range:
            result["equity"] = poker_math.estimate_equity_from_outs(
                outs_data["count"], len(board_cards)
            )
            result["equity_method"] = "outs_estimation"
        else:
            result["equity"] = poker_math.estimate_equity_from_outs(
                outs_data["count"], len(board_cards)
            )
            result["equity_method"] = "outs_estimation"

        # 3. Pot odds calculation
        if pot_size is not None and bet_to_call is not None:
            pot_odds = poker_math.calculate_pot_odds(pot_size, bet_to_call)
            result["pot_odds"] = {
                "percentage": pot_odds,
                "ratio": poker_math.percentage_to_ratio(pot_odds),
                "required_equity": pot_odds,
            }
        else:
            result["pot_odds"] = None

        # 4. Implied odds estimation
        if (
            pot_size is not None
            and bet_to_call is not None
            and effective_stack is not None
        ):
            implied_odds = poker_math.estimate_implied_odds(
                pot_size, bet_to_call, effective_stack, outs_data["count"]
            )
            result["implied_odds"] = implied_odds
        else:
            result["implied_odds"] = None

        # 5. SPR calculation
        if pot_size is not None and effective_stack is not None:
            spr = effective_stack / pot_size if pot_size > 0 else float("inf")
            result["spr"] = round(spr, 2)
            result["spr_category"] = poker_math.categorize_spr(spr)
        else:
            result["spr"] = None
            result["spr_category"] = None

        # 6. EV calculations
        if pot_size is not None and bet_to_call is not None:
            ev_analysis = poker_math.calculate_ev(
                result["equity"], pot_size, bet_to_call, effective_stack
            )
            result["ev"] = ev_analysis
        else:
            result["ev"] = None

        # 7. Enhance hand strength description with draw information
        result["hand_strength"]["description"] = self._enhance_hand_description(
            hand_eval["hand_class"], result["outs"]
        )

        # 8. Generate recommendation
        result["recommendation"] = self._generate_recommendation(result)

        return result

    def _enhance_hand_description(
        self, hand_class: str, outs_breakdown: Dict[str, Any]
    ) -> str:
        """
        Enhance hand description with draw information.

        Args:
            hand_class: Base hand class (e.g., "High Card", "Pair")
            outs_breakdown: Breakdown of outs by category

        Returns:
            Enhanced description string
        """
        draws = []

        # Check for flush draw
        flush = outs_breakdown.get("flush_draw", {})
        if flush.get("type") == "flush_draw" and flush.get("count", 0) > 0:
            draws.append("Flush Draw")
        elif flush.get("type") == "backdoor_flush" and flush.get("count", 0) > 0:
            draws.append("Backdoor Flush Draw")

        # Check for straight draw
        straight = outs_breakdown.get("straight_draw", {})
        if straight.get("type") == "open_ended":
            draws.append("Open-Ended Straight Draw")
        elif straight.get("type") == "gutshot":
            draws.append("Gutshot Straight Draw")
        elif straight.get("type") == "double_gutshot":
            draws.append("Double Gutshot Straight Draw")

        # Check for overcards
        overcards = outs_breakdown.get("overcards", {})
        if overcards.get("count", 0) > 0:
            num_cards = len(overcards.get("cards", []))
            if num_cards == 2:
                draws.append("Two Overcards")
            elif num_cards == 1:
                draws.append("One Overcard")

        # Combine
        if draws:
            return f"{hand_class} ({' + '.join(draws)})"
        return hand_class

    def _parse_cards(self, card_string: str) -> List[int]:
        """
        Parse card string into list of treys card integers.

        Args:
            card_string: Space-separated cards (e.g., "As Kh")

        Returns:
            List of treys card integers

        Raises:
            ValueError: If card format is invalid
        """
        cards = []
        for card in card_string.strip().split():
            try:
                cards.append(Card.new(card))
            except (KeyError, IndexError):
                raise ValueError(
                    f"Invalid card format: '{card}'. Expected format like 'As', 'Kh', etc."
                )
        return cards

    def _generate_recommendation(self, analysis: Dict) -> Dict[str, Any]:
        """
        Generate action recommendation based on analysis.

        Logic:
        1. Compare equity to pot odds
        2. Consider SPR for commitment
        3. Factor in implied odds for draws
        4. Consider hand strength

        Args:
            analysis: Full analysis dict

        Returns:
            Dict with action, confidence, and reasoning
        """
        recommendation: Dict[str, Any] = {
            "action": "UNKNOWN",
            "confidence": "low",
            "reasoning": [],
        }

        equity = analysis.get("equity", 0)
        pot_odds = analysis.get("pot_odds")
        implied_odds = analysis.get("implied_odds")
        spr = analysis.get("spr")
        ev_analysis = analysis.get("ev")
        hand_strength = analysis["hand_strength"]["class"]

        # If we don't have enough info, return conservative recommendation
        if pot_odds is None or ev_analysis is None:
            recommendation["action"] = "ANALYZE"
            recommendation["reasoning"].append(
                "Insufficient information for recommendation - need pot size and bet size"
            )
            return recommendation

        required_equity = pot_odds["required_equity"]

        # Decision logic
        if equity >= required_equity:
            # We have the odds to call
            if ev_analysis["call"] > 0:
                recommendation["action"] = "CALL"
                recommendation["confidence"] = "high"
                recommendation["reasoning"].append(
                    f"Equity ({equity}%) exceeds pot odds ({required_equity}%)"
                )
                recommendation["reasoning"].append(
                    f"Positive EV: +{ev_analysis['call']:.2f} chips"
                )

                # Check if we should raise instead
                if hand_strength in [
                    "Straight Flush",
                    "Four of a Kind",
                    "Full House",
                    "Flush",
                    "Straight",
                ]:
                    recommendation["reasoning"].append(
                        f"Strong hand ({hand_strength}) - consider raising for value"
                    )
            else:
                recommendation["action"] = "CALL"
                recommendation["confidence"] = "medium"
                recommendation["reasoning"].append(
                    f"Equity sufficient but EV marginal ({ev_analysis['call']:.2f})"
                )
        else:
            # We don't have direct pot odds
            if implied_odds and equity >= implied_odds["percentage"]:
                recommendation["action"] = "CALL"
                recommendation["confidence"] = "medium"
                recommendation["reasoning"].append(
                    f"Implied odds ({implied_odds['percentage']:.1f}%) justify call despite pot odds"
                )
                recommendation["reasoning"].append(
                    f"Expected future winnings: {implied_odds['estimated_future_winnings']:.0f} chips"
                )
            else:
                recommendation["action"] = "FOLD"
                recommendation["confidence"] = "high"
                recommendation["reasoning"].append(
                    f"Equity ({equity}%) below pot odds ({required_equity}%)"
                )
                recommendation["reasoning"].append(
                    f"Negative EV: {ev_analysis['call']:.2f} chips"
                )

        # SPR considerations
        if spr is not None:
            if spr <= 3 and hand_strength in ["Three of a Kind", "Two Pair", "Pair"]:
                recommendation["reasoning"].append(
                    f"Low SPR ({spr}) - committed to pot with {hand_strength}"
                )

        return recommendation


# Convenience function
def analyze_spot_simple(
    hero_hand: str,
    board: str,
    pot_size: float,
    bet_to_call: float,
    effective_stack: Optional[float] = None,
) -> str:
    """
    Simple spot analysis returning just the recommendation.

    Args:
        hero_hand: Hero's cards
        board: Board cards
        pot_size: Current pot
        bet_to_call: Amount to call
        effective_stack: Stack remaining (optional)

    Returns:
        Recommendation string (e.g., "CALL", "FOLD", "RAISE")

    Example:
        >>> analyze_spot_simple("Ah Kh", "Qh Jh 2c", 100, 50)
        'CALL'
    """
    analyzer = SpotAnalyzer()
    result = analyzer.analyze(hero_hand, board, pot_size, bet_to_call, effective_stack)
    return result["recommendation"]["action"]
