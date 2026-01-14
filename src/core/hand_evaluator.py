"""
Hand evaluation and equity calculation using Monte Carlo simulation.

This module provides core poker logic for:
- Hand strength evaluation (pair, flush, straight, etc.)
- Equity calculation via Monte Carlo simulation
"""

from typing import Dict, List
from treys import Card, Evaluator, Deck


class HandEvaluator:
    """Evaluate poker hand strength using treys library."""

    def __init__(self):
        """Initialize the hand evaluator."""
        self.evaluator = Evaluator()

    def evaluate(self, hero_hand: str, board: str) -> Dict:
        """
        Evaluate poker hand strength.

        Args:
            hero_hand: Two cards (e.g., "As Kh")
            board: 3-5 board cards (e.g., "Qh Jh 2c")

        Returns:
            Dictionary with:
                - hand_class: Hand type (e.g., "Flush", "Pair")
                - rank: Numeric rank (lower is better, 1 = royal flush)
                - description: Human-readable description

        Raises:
            ValueError: If card format is invalid

        Example:
            >>> evaluator = HandEvaluator()
            >>> result = evaluator.evaluate("As Ks", "Qs Js Ts")
            >>> print(result['hand_class'])
            'Straight Flush'
        """
        try:
            # Parse cards
            hero = self._parse_cards(hero_hand)
            board_cards = self._parse_cards(board)

            if len(hero) != 2:
                raise ValueError(f"Hero hand must have exactly 2 cards, got {len(hero)}")

            if len(board_cards) < 3 or len(board_cards) > 5:
                raise ValueError(f"Board must have 3-5 cards, got {len(board_cards)}")

            # Evaluate hand
            rank = self.evaluator.evaluate(board_cards, hero)
            rank_class = self.evaluator.get_rank_class(rank)
            hand_class = self.evaluator.class_to_string(rank_class)

            return {
                "hand_class": hand_class,
                "rank": rank,
                "description": f"{hand_class} (rank: {rank})",
            }

        except Exception as e:
            raise ValueError(f"Error evaluating hand: {str(e)}")

    def _parse_cards(self, card_string: str) -> List[int]:
        """
        Parse space-separated card string into treys card integers.

        Args:
            card_string: Cards like "As Kh" or "Qh Jh 2c"

        Returns:
            List of treys card integers

        Raises:
            ValueError: If card format is invalid
        """
        if not card_string or not card_string.strip():
            raise ValueError("Card string cannot be empty")

        cards = []
        for card_str in card_string.strip().split():
            try:
                card = Card.new(card_str)
                cards.append(card)
            except Exception as e:
                raise ValueError(
                    f"Invalid card '{card_str}'. Expected format: rank (2-9, T, J, Q, K, A) "
                    f"+ suit (s, h, d, c). Example: 'As' for Ace of spades."
                )

        return cards


class EquityCalculator:
    """Calculate poker equity using Monte Carlo simulation."""

    def __init__(self):
        """Initialize equity calculator."""
        self.evaluator = Evaluator()

    def calculate(
        self,
        hero_hand: str,
        villain_hand: str,
        board: str = "",
        iterations: int = 10000,
    ) -> Dict:
        """
        Calculate equity via Monte Carlo simulation.

        Args:
            hero_hand: Hero's cards (e.g., "As Kh")
            villain_hand: Villain's cards (e.g., "Qd Qc")
            board: Current board (e.g., "Ah 7s 2c"), empty string for preflop
            iterations: Number of simulations (default: 10000)

        Returns:
            Dictionary with:
                - hero_equity: Hero's win probability (0-100)
                - villain_equity: Villain's win probability (0-100)
                - hero_wins: Number of wins for hero
                - villain_wins: Number of wins for villain
                - ties: Number of ties
                - iterations: Number of simulations run

        Example:
            >>> calc = EquityCalculator()
            >>> result = calc.calculate("As Ad", "Kh Kd", "", 10000)
            >>> print(f"AA vs KK: {result['hero_equity']:.1f}%")
            AA vs KK: 80.2%
        """
        try:
            # Parse cards
            hero = self._parse_cards(hero_hand)
            villain = self._parse_cards(villain_hand)
            board_cards = self._parse_cards(board) if board else []

            # Validate
            if len(hero) != 2:
                raise ValueError(f"Hero hand must have 2 cards, got {len(hero)}")
            if len(villain) != 2:
                raise ValueError(f"Villain hand must have 2 cards, got {len(villain)}")
            if len(board_cards) > 5:
                raise ValueError(f"Board can have max 5 cards, got {len(board_cards)}")

            # Check for duplicate cards
            all_cards = hero + villain + board_cards
            if len(all_cards) != len(set(all_cards)):
                raise ValueError("Duplicate cards detected")

            # Run simulations
            hero_wins = 0
            villain_wins = 0
            ties = 0

            for _ in range(iterations):
                # Create fresh deck
                deck = Deck()

                # Remove known cards
                for card in all_cards:
                    deck.cards.remove(card)

                # Deal remaining board cards
                remaining_cards = 5 - len(board_cards)
                simulated_board = board_cards + deck.draw(remaining_cards)

                # Evaluate both hands
                hero_score = self.evaluator.evaluate(simulated_board, hero)
                villain_score = self.evaluator.evaluate(simulated_board, villain)

                # Lower score wins in treys
                if hero_score < villain_score:
                    hero_wins += 1
                elif villain_score < hero_score:
                    villain_wins += 1
                else:
                    ties += 1

            # Calculate equity
            total = iterations
            hero_equity = (hero_wins + ties / 2) / total * 100
            villain_equity = (villain_wins + ties / 2) / total * 100

            return {
                "hero_equity": round(hero_equity, 2),
                "villain_equity": round(villain_equity, 2),
                "hero_wins": hero_wins,
                "villain_wins": villain_wins,
                "ties": ties,
                "iterations": iterations,
            }

        except Exception as e:
            raise ValueError(f"Error calculating equity: {str(e)}")

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


# Convenience functions for quick access
def evaluate_hand_simple(hero_hand: str, board: str) -> str:
    """
    Simple hand evaluation returning just the hand class.

    Args:
        hero_hand: Hero's cards (e.g., "As Kh")
        board: Board cards (e.g., "Qh Jh 2c")

    Returns:
        Hand class string (e.g., "Flush", "Two Pair")

    Example:
        >>> evaluate_hand_simple("Ah Kh", "Qh Jh Th")
        'Royal Flush'
    """
    evaluator = HandEvaluator()
    result = evaluator.evaluate(hero_hand, board)
    return result["hand_class"]


def calculate_equity_simple(
    hero_hand: str,
    villain_hand: str,
    board: str = "",
    iterations: int = 10000,
) -> float:
    """
    Simple equity calculation returning just hero's equity percentage.

    Args:
        hero_hand: Hero's cards
        villain_hand: Villain's cards
        board: Board cards (optional)
        iterations: Number of simulations

    Returns:
        Hero's equity as percentage (0-100)

    Example:
        >>> calculate_equity_simple("As Ad", "Kh Kd")
        80.2
    """
    calc = EquityCalculator()
    result = calc.calculate(hero_hand, villain_hand, board, iterations)
    return result["hero_equity"]
