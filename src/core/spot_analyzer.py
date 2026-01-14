"""
Comprehensive poker spot analysis with pot odds, SPR, EV, and outs calculation.

This module provides detailed analysis of poker situations including:
- Pot odds and implied odds
- Stack-to-pot ratio (SPR)
- Expected value (EV) calculations
- Out counting and equity
- Decision recommendations
"""

from typing import Dict, List, Optional
from treys import Card, Evaluator
from .hand_evaluator import HandEvaluator, EquityCalculator


class SpotAnalyzer:
    """Comprehensive poker spot analysis with all poker math."""

    def __init__(self):
        """Initialize spot analyzer with hand evaluator and equity calculator."""
        self.hand_evaluator = HandEvaluator()
        self.equity_calculator = EquityCalculator()
        self.evaluator = Evaluator()

    def analyze(
        self,
        hero_hand: str,
        board: str,
        pot_size: Optional[float] = None,
        bet_to_call: Optional[float] = None,
        effective_stack: Optional[float] = None,
        villain_range: Optional[str] = None,
    ) -> Dict:
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

        result = {}

        # 1. Hand strength evaluation
        hand_eval = self.hand_evaluator.evaluate(hero_hand, board)
        result["hand_strength"] = {
            "class": hand_eval["hand_class"],
            "rank": hand_eval["rank"],
            "description": hand_eval["description"],
        }

        # 2. Calculate outs and equity
        outs_data = self._calculate_outs(hero_cards, board_cards)
        result["outs"] = outs_data["breakdown"]
        result["out_count"] = outs_data["count"]
        result["unknown_cards"] = outs_data["unknown_cards"]

        # Calculate equity (estimate based on outs if no villain hand specified)
        # NOTE: Outs-based equity is best for DRAWING hands (flush draws, straight draws, overcards)
        # For MADE hands (sets, two pair, top pair), you need villain's range to calculate proper equity
        # Without villain range, a made hand will show low equity since it has few "outs to improve"
        if villain_range:
            # TODO: Implement range-based equity calculation using Monte Carlo vs range
            # This would simulate hero hand vs all hands in villain's range
            result["equity"] = self._estimate_equity_from_outs(
                outs_data["count"], len(board_cards)
            )
            result["equity_method"] = "outs_estimation"
        else:
            # Outs-based estimation (accurate for draws, not for made hands)
            result["equity"] = self._estimate_equity_from_outs(
                outs_data["count"], len(board_cards)
            )
            result["equity_method"] = "outs_estimation"

            # TODO: For made hands, could return alternative metrics:
            # - "hand_percentile": Where hand ranks vs all possible holdings (e.g., "top 5%")
            # - "board_texture_strength": How vulnerable hand is to draws
            # - "minimum_defense_frequency": GTO concept for facing bets

        # 3. Pot odds calculation
        if pot_size is not None and bet_to_call is not None:
            pot_odds = self._calculate_pot_odds(pot_size, bet_to_call)
            result["pot_odds"] = {
                "percentage": pot_odds,
                "ratio": self._percentage_to_ratio(pot_odds),
                "required_equity": pot_odds,
            }
        else:
            result["pot_odds"] = None

        # 4. Implied odds estimation
        if pot_size is not None and bet_to_call is not None and effective_stack is not None:
            implied_odds = self._estimate_implied_odds(
                pot_size, bet_to_call, effective_stack, outs_data["count"]
            )
            result["implied_odds"] = implied_odds
        else:
            result["implied_odds"] = None

        # 5. SPR calculation
        if pot_size is not None and effective_stack is not None:
            spr = effective_stack / pot_size if pot_size > 0 else float("inf")
            result["spr"] = round(spr, 2)
            result["spr_category"] = self._categorize_spr(spr)
        else:
            result["spr"] = None
            result["spr_category"] = None

        # 6. EV calculations
        if pot_size is not None and bet_to_call is not None:
            ev_analysis = self._calculate_ev(
                result["equity"], pot_size, bet_to_call, effective_stack
            )
            result["ev"] = ev_analysis
        else:
            result["ev"] = None

        # 7. Generate recommendation
        result["recommendation"] = self._generate_recommendation(result)

        return result

    def _parse_cards(self, card_string: str) -> List[int]:
        """Parse card string into treys card integers."""
        if not card_string or not card_string.strip():
            return []

        cards = []
        for card_str in card_string.strip().split():
            try:
                card = Card.new(card_str)
                cards.append(card)
            except Exception:
                raise ValueError(
                    f"Invalid card '{card_str}'. Expected format: rank (2-9, T, J, Q, K, A) "
                    f"+ suit (s, h, d, c)."
                )

        return cards

    def _calculate_outs(self, hero_cards: List[int], board_cards: List[int]) -> Dict:
        """
        Calculate outs - cards that improve the hand.

        Uses deterministic math based on:
        - Remaining deck cards (52 - known cards)
        - Hand patterns (flush draws, straight draws, overcards, etc.)
        - Current hand strength

        Returns categorized outs showing all improvement paths.
        """
        from treys import Card

        # Get card details
        hero_ranks = [Card.get_rank_int(c) for c in hero_cards]
        hero_suits = [Card.get_suit_int(c) for c in hero_cards]
        board_ranks = [Card.get_rank_int(c) for c in board_cards]
        board_suits = [Card.get_suit_int(c) for c in board_cards]

        all_cards = hero_cards + board_cards
        known_ranks = hero_ranks + board_ranks
        known_suits = hero_suits + board_suits

        # Calculate remaining cards in deck
        unknown_cards = 52 - len(all_cards)

        # Initialize outs tracking
        outs_breakdown = {
            "flush_draw": {"count": 0, "cards_needed": 0},
            "straight_draw": {"count": 0, "type": None},
            "overcards": {"count": 0, "cards": []},
            "pair_outs": {"count": 0, "to_trips": 0, "to_two_pair": 0},
            "set_to_boat": {"count": 0},
            "backdoor_flush": {"count": 0},
            "backdoor_straight": {"count": 0},
        }

        total_outs = 0

        # 1. FLUSH DRAW ANALYSIS
        flush_outs = self._count_flush_outs(hero_suits, board_suits, known_ranks, all_cards)
        outs_breakdown["flush_draw"] = flush_outs
        if flush_outs["count"] > 0:
            total_outs += flush_outs["count"]

        # 2. STRAIGHT DRAW ANALYSIS
        straight_outs = self._count_straight_outs(hero_ranks, board_ranks, known_ranks)
        outs_breakdown["straight_draw"] = straight_outs
        if straight_outs["count"] > 0:
            total_outs += straight_outs["count"]

        # 3. OVERCARD ANALYSIS (unpaired cards higher than board)
        overcard_outs = self._count_overcard_outs(hero_ranks, board_ranks, known_ranks)
        outs_breakdown["overcards"] = overcard_outs
        if overcard_outs["count"] > 0:
            total_outs += overcard_outs["count"]

        # 4. PAIR IMPROVEMENT (pair to trips/two pair, trips to boat)
        pair_outs = self._count_pair_improvement_outs(hero_ranks, board_ranks, known_ranks)
        outs_breakdown["pair_outs"] = pair_outs
        if pair_outs["count"] > 0:
            total_outs += pair_outs["count"]

        # 5. BACKDOOR DRAWS (need 2 cards)
        if len(board_cards) == 3:  # Only relevant on flop
            backdoor_flush = self._count_backdoor_flush(hero_suits, board_suits)
            outs_breakdown["backdoor_flush"] = backdoor_flush

        return {
            "count": total_outs,
            "breakdown": outs_breakdown,
            "unknown_cards": unknown_cards,
        }

    def _count_flush_outs(self, hero_suits, board_suits, known_ranks, all_cards) -> Dict:
        """Count outs to make a flush."""
        from collections import Counter

        all_suits = hero_suits + board_suits
        suit_counts = Counter(all_suits)

        # Check for flush draw (4 cards of same suit)
        for suit, count in suit_counts.items():
            if count == 4:
                # 13 cards of this suit - 4 we can see = 9 outs
                return {
                    "count": 9,
                    "cards_needed": 1,
                    "type": "flush_draw",
                    "suit": ["spades", "hearts", "diamonds", "clubs"][suit],
                }
            elif count == 3 and len(board_suits + hero_suits) == 5:  # Backdoor on turn
                return {
                    "count": 9,
                    "cards_needed": 1,
                    "type": "backdoor_flush_turn",
                    "suit": ["spades", "hearts", "diamonds", "clubs"][suit],
                }

        return {"count": 0, "cards_needed": 0}

    def _count_straight_outs(self, hero_ranks, board_ranks, known_ranks) -> Dict:
        """Count outs to make a straight."""
        from collections import Counter

        all_ranks = hero_ranks + board_ranks
        unique_ranks = sorted(set(all_ranks), reverse=True)

        # Convert to standard values (A=14, K=13, ..., 2=2)
        # treys uses 0-12 where 0=Deuce, 12=Ace
        # Convert: treys_rank -> poker_rank
        poker_ranks = [12 - r for r in unique_ranks]

        # Check for straight draws
        # OESD (Open-Ended Straight Draw): 8 outs
        # Gutshot: 4 outs
        # Double gutshot: 8 outs

        # For simplicity, check common patterns
        # This is a simplified version - full implementation would check all combinations
        if self._has_straight_draw_pattern(poker_ranks):
            # Count how many ranks would complete the straight
            # Simplified: assume 8 outs for OESD, 4 for gutshot
            return {"count": 8, "type": "open_ended"}

        return {"count": 0, "type": None}

    def _has_straight_draw_pattern(self, ranks) -> bool:
        """Check if ranks form a straight draw pattern."""
        # Simplified check for 4 cards in sequence
        if len(ranks) < 4:
            return False

        # Check for 4 cards within 5 rank span (OESD pattern)
        for i in range(len(ranks) - 3):
            if ranks[i] - ranks[i + 3] <= 4:
                return True

        return False

    def _count_overcard_outs(self, hero_ranks, board_ranks, known_ranks) -> Dict:
        """Count outs to pair an overcard."""
        if not board_ranks:
            return {"count": 0, "cards": []}

        max_board_rank = max(board_ranks)
        overcards = [r for r in hero_ranks if r > max_board_rank]

        if not overcards:
            return {"count": 0, "cards": []}

        # Each overcard has 3 outs (4 in deck - 1 in hand)
        # But need to account for duplicates in known cards
        unique_overcards = list(set(overcards))
        total_outs = len(unique_overcards) * 3

        return {
            "count": total_outs,
            "cards": unique_overcards,
            "note": f"{len(unique_overcards)} overcard(s) with 3 outs each",
        }

    def _count_pair_improvement_outs(self, hero_ranks, board_ranks, known_ranks) -> Dict:
        """Count outs to improve a pair to trips or two pair."""
        from collections import Counter

        all_ranks = hero_ranks + board_ranks
        rank_counts = Counter(all_ranks)

        # Check if we have a pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]

        if not pairs:
            return {"count": 0, "to_trips": 0, "to_two_pair": 0}

        # If we have a pair, we have:
        # - 2 outs to make trips (2 remaining cards of that rank)
        # - Outs to make two pair (3 outs for each unpaired card in hand)

        to_trips = 2  # Always 2 outs to trips if we have a pair

        # Two pair outs: if we have one unpaired card in hand
        unpaired_hero = [r for r in hero_ranks if rank_counts[r] == 1]
        to_two_pair = len(unpaired_hero) * 3 if unpaired_hero else 0

        total = to_trips + to_two_pair

        return {"count": total, "to_trips": to_trips, "to_two_pair": to_two_pair}

    def _count_backdoor_flush(self, hero_suits, board_suits) -> Dict:
        """Count backdoor flush draws (need runner-runner)."""
        from collections import Counter

        all_suits = hero_suits + board_suits
        suit_counts = Counter(all_suits)

        # Backdoor flush: 3 of same suit on flop, need 2 more
        for suit, count in suit_counts.items():
            if count == 3:
                return {
                    "count": 1,  # Represented as 1 draw, not outs
                    "type": "backdoor",
                    "suit": ["spades", "hearts", "diamonds", "clubs"][suit],
                    "note": "Need runner-runner (turn + river)",
                }

        return {"count": 0}

    def _estimate_equity_from_outs(self, outs: int, board_size: int) -> float:
        """
        Estimate equity using the rule of 2 and 4.

        - On flop (2 cards to come): outs * 4
        - On turn (1 card to come): outs * 2
        """
        if board_size == 3:  # Flop
            # Rule of 4: multiply outs by 4
            equity = min(outs * 4, 100)
        elif board_size == 4:  # Turn
            # Rule of 2: multiply outs by 2
            equity = min(outs * 2, 100)
        else:  # River
            equity = 0  # No cards to come

        return round(equity, 2)

    def _calculate_pot_odds(self, pot_size: float, bet_to_call: float) -> float:
        """
        Calculate pot odds as percentage.

        Formula: (bet_to_call / (pot + bet_to_call)) * 100
        """
        if bet_to_call == 0:
            return 0.0

        total_pot = pot_size + bet_to_call
        if total_pot == 0:
            return 0.0

        pot_odds = (bet_to_call / total_pot) * 100
        return round(pot_odds, 2)

    def _percentage_to_ratio(self, percentage: float) -> str:
        """
        Convert pot odds percentage to ratio format.

        Example: 33.33% -> "2:1"
        """
        if percentage >= 100:
            return "0:1"
        if percentage <= 0:
            return "∞:1"

        # Calculate ratio
        call_part = percentage
        pot_part = 100 - percentage

        # Simplify to X:1 format
        ratio = pot_part / call_part
        return f"{ratio:.1f}:1"

    def _estimate_implied_odds(
        self, pot_size: float, bet_to_call: float, effective_stack: float, outs: int
    ) -> Dict:
        """
        Estimate implied odds - potential future winnings.

        Implied odds account for money you can win on future streets.
        This is a conservative estimate.
        """
        # Estimate potential future bets (conservative: 50% of remaining stack)
        remaining_stack = effective_stack - bet_to_call
        estimated_future_winnings = remaining_stack * 0.5

        # Calculate implied pot odds
        implied_pot = pot_size + bet_to_call + estimated_future_winnings
        implied_odds_percentage = (bet_to_call / implied_pot) * 100

        return {
            "percentage": round(implied_odds_percentage, 2),
            "ratio": self._percentage_to_ratio(implied_odds_percentage),
            "estimated_future_winnings": round(estimated_future_winnings, 2),
            "note": "Conservative estimate assuming 50% of remaining stack",
        }

    def _categorize_spr(self, spr: float) -> str:
        """
        Categorize SPR into low/medium/high.

        - Low SPR (0-3): Strong commitment, play straightforward
        - Medium SPR (4-12): Standard play, flexible
        - High SPR (13+): Deep stacks, maximize value
        """
        if spr <= 3:
            return "low"
        elif spr <= 12:
            return "medium"
        else:
            return "high"

    def _calculate_ev(
        self,
        equity: float,
        pot_size: float,
        bet_to_call: float,
        effective_stack: Optional[float],
    ) -> Dict:
        """
        Calculate expected value for different actions.

        EV(call) = (equity * final_pot) - ((1 - equity) * bet_to_call)
        EV(fold) = 0 (baseline)
        """
        equity_decimal = equity / 100

        # EV of calling
        final_pot = pot_size + bet_to_call
        ev_call = (equity_decimal * final_pot) - ((1 - equity_decimal) * bet_to_call)

        # EV of folding (always 0)
        ev_fold = 0

        return {
            "call": round(ev_call, 2),
            "fold": ev_fold,
            "note": "Raise EV requires opponent modeling",
        }

    def _generate_recommendation(self, analysis: Dict) -> Dict:
        """
        Generate action recommendation based on analysis.

        Logic:
        1. Compare equity to pot odds
        2. Consider SPR for commitment
        3. Factor in implied odds for draws
        4. Consider hand strength
        """
        recommendation = {
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
                if hand_strength in ["Straight Flush", "Four of a Kind", "Full House", "Flush", "Straight"]:
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
    effective_stack: float = None,
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
