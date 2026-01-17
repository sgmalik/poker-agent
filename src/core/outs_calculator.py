"""Outs calculation for poker hand analysis."""

from typing import Any, Dict, List, Set, Tuple
from collections import Counter
from treys import Card


class OutsCalculator:
    """Calculate outs (cards that improve a hand) for poker situations."""

    def __init__(self):
        """Initialize outs calculator."""
        pass

    def calculate_outs(
        self, hero_cards: List[int], board_cards: List[int]
    ) -> Dict[str, Any]:
        """
        Calculate outs - cards that improve the hand.

        Uses deterministic math based on:
        - Remaining deck cards (52 - known cards)
        - Hand patterns (flush draws, straight draws, overcards, etc.)
        - Removes overlapping outs (cards that count for multiple improvements)

        Returns categorized outs showing all improvement paths with correct total.

        Args:
            hero_cards: List of treys card integers for hero's hand
            board_cards: List of treys card integers for the board

        Returns:
            Dict with total outs, breakdown by category, and unknown cards
        """
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
        }

        # Track specific out cards to avoid double-counting
        # Each out card is represented as (rank, suit) tuple
        flush_out_cards: Set[Tuple[int, int]] = set()
        straight_out_ranks: Set[int] = set()
        overcard_out_ranks: Set[int] = set()

        # 1. FLUSH DRAW ANALYSIS
        flush_outs = self.count_flush_outs(
            hero_suits, board_suits, known_ranks, all_cards
        )
        outs_breakdown["flush_draw"] = flush_outs

        # If we have a REAL flush draw (not backdoor), track the specific cards
        if (
            flush_outs["count"] > 0
            and flush_outs.get("type") == "flush_draw"
            and "suit_int" in flush_outs
        ):
            flush_suit = flush_outs["suit_int"]
            # Add all unknown cards of this suit to flush_out_cards
            for rank in range(13):  # treys ranks 0-12
                card = self._create_card_from_rank_suit(rank, flush_suit)
                if card not in all_cards:
                    flush_out_cards.add((rank, flush_suit))

        # 2. STRAIGHT DRAW ANALYSIS
        straight_outs = self.count_straight_outs(hero_ranks, board_ranks, known_ranks)
        outs_breakdown["straight_draw"] = straight_outs

        # If we have straight draw, track the ranks that complete it
        if straight_outs["count"] > 0 and "missing_ranks" in straight_outs:
            for poker_rank in straight_outs["missing_ranks"]:
                treys_rank = 12 if poker_rank == 14 else poker_rank - 2
                straight_out_ranks.add(treys_rank)

        # 3. OVERCARD ANALYSIS (unpaired cards higher than board)
        overcard_outs = self.count_overcard_outs(hero_ranks, board_ranks, known_ranks)
        outs_breakdown["overcards"] = overcard_outs

        if overcard_outs["count"] > 0 and "cards" in overcard_outs:
            overcard_out_ranks = set(overcard_outs["cards"])

        # 4. PAIR IMPROVEMENT (pair to trips/two pair, trips to boat)
        pair_outs = self.count_pair_improvement_outs(
            hero_ranks, board_ranks, known_ranks
        )
        outs_breakdown["pair_outs"] = pair_outs

        # CALCULATE TOTAL OUTS (removing overlaps)
        total_unique_outs: Set[Tuple[int, int]] = set()

        # Add flush outs (specific rank+suit combinations)
        total_unique_outs.update(flush_out_cards)

        # Add straight outs (any suit of the needed ranks, except those already in flush)
        for rank in straight_out_ranks:
            for suit_int in [1, 2, 4, 8]:  # spades, hearts, diamonds, clubs
                if (rank, suit_int) not in flush_out_cards:
                    card = self._create_card_from_rank_suit(rank, suit_int)
                    if card not in all_cards:
                        total_unique_outs.add((rank, suit_int))

        # Add overcard outs (any suit of the needed ranks, except flush/straight outs)
        for rank in overcard_out_ranks:
            for suit_int in [1, 2, 4, 8]:
                if (rank, suit_int) not in total_unique_outs:
                    card = self._create_card_from_rank_suit(rank, suit_int)
                    if card not in all_cards:
                        total_unique_outs.add((rank, suit_int))

        # Add pair improvement outs
        pair_out_count = pair_outs.get("count", 0)

        # Calculate final total
        total_outs = len(total_unique_outs) + pair_out_count

        # Add backdoor flush equity if present (not specific cards, just equity bonus)
        if flush_outs.get("type") == "backdoor_flush":
            backdoor_flush_outs = flush_outs.get("count", 0)
            total_outs += backdoor_flush_outs

        return {
            "count": total_outs,
            "breakdown": outs_breakdown,
            "unknown_cards": unknown_cards,
            "unique_out_cards": total_unique_outs,  # For debugging
        }

    def count_flush_outs(
        self, hero_suits, board_suits, known_ranks, all_cards
    ) -> Dict[str, Any]:
        """
        Count outs to make a flush.

        Flush Draw Rules:
        - On FLOP: Need 4 cards of same suit = 9 outs
        - On FLOP: 3 cards of same suit = Backdoor flush (1.0 equivalent outs)
        - On TURN: Need 4 cards of same suit = 9 outs

        Args:
            hero_suits: List of hero card suits (treys suit ints)
            board_suits: List of board card suits (treys suit ints)
            known_ranks: All known ranks
            all_cards: All known cards

        Returns:
            Dict with flush out count and details
        """
        all_suits = hero_suits + board_suits
        suit_counts = Counter(all_suits)

        # Map treys suit ints to names
        suit_names = {1: "spades", 2: "hearts", 4: "diamonds", 8: "clubs"}

        # Check for flush draw (4 cards of same suit)
        for suit_int, count in suit_counts.items():
            if count == 4:
                # Real flush draw - 9 outs
                return {
                    "count": 9,
                    "cards_needed": 1,
                    "type": "flush_draw",
                    "suit": suit_names.get(suit_int, "unknown"),
                    "suit_int": suit_int,
                }
            elif count == 3:
                # Backdoor flush - needs runner-runner
                # Probability: (10/47) × (9/46) ≈ 4.16% ≈ 1.0 outs
                return {
                    "count": 1.0,
                    "cards_needed": 2,
                    "type": "backdoor_flush",
                    "suit": suit_names.get(suit_int, "unknown"),
                    "suit_int": suit_int,
                }

        return {"count": 0, "cards_needed": 0}

    def count_straight_outs(
        self, hero_ranks, board_ranks, known_ranks
    ) -> Dict[str, Any]:
        """
        Count outs to make a straight.

        Properly detects:
        - Open-ended straight draws (OESD): 8 outs
        - Gutshot straight draws: 4 outs
        - Double gutshots: 8 outs

        Args:
            hero_ranks: Hero card ranks (treys rank ints)
            board_ranks: Board card ranks (treys rank ints)
            known_ranks: All known ranks

        Returns:
            Dict with straight out count and type
        """
        all_ranks = hero_ranks + board_ranks
        unique_ranks = sorted(set(all_ranks), reverse=True)

        # Convert to standard poker values (A=14, K=13, ..., 2=2)
        # treys uses 0=2, 1=3, ..., 11=K, 12=A
        poker_ranks = sorted(
            [14 if r == 12 else r + 2 for r in unique_ranks], reverse=True
        )

        # Need at least 4 cards for a straight draw
        if len(poker_ranks) < 4:
            return {"count": 0, "type": None}

        # Track all possible straight draws
        possible_draws = []

        # Check regular straights (A-high down to 5-high)
        for high_rank in range(14, 4, -1):
            window = [
                high_rank,
                high_rank - 1,
                high_rank - 2,
                high_rank - 3,
                high_rank - 4,
            ]

            cards_we_have = [r for r in poker_ranks if r in window]

            # If we have exactly 4 of the 5 needed cards, this is a draw
            if len(cards_we_have) == 4:
                missing_rank = [r for r in window if r not in cards_we_have][0]

                # Determine draw type based on the pattern
                sorted_cards = sorted(cards_we_have, reverse=True)

                # Check if our 4 cards are consecutive (no gaps)
                is_consecutive = all(
                    sorted_cards[i] - sorted_cards[i + 1] == 1
                    for i in range(len(sorted_cards) - 1)
                )

                if is_consecutive:
                    # 4 consecutive cards - check which end is missing
                    highest_card = sorted_cards[0]
                    lowest_card = sorted_cards[3]

                    if missing_rank == highest_card + 1:
                        possible_draws.append(
                            {
                                "missing_rank": missing_rank,
                                "type": "top_end",
                                "window": window,
                            }
                        )
                    elif missing_rank == lowest_card - 1:
                        possible_draws.append(
                            {
                                "missing_rank": missing_rank,
                                "type": "bottom_end",
                                "window": window,
                            }
                        )
                    else:
                        possible_draws.append(
                            {
                                "missing_rank": missing_rank,
                                "type": "gutshot",
                                "window": window,
                            }
                        )
                else:
                    # 4 cards with a gap - this is a gutshot
                    possible_draws.append(
                        {
                            "missing_rank": missing_rank,
                            "type": "gutshot",
                            "window": window,
                        }
                    )

        # Special case: Wheel (A-2-3-4-5)
        wheel_window = [5, 4, 3, 2, 14]
        wheel_cards = [r for r in poker_ranks if r in wheel_window]
        if len(wheel_cards) == 4:
            missing_rank = [r for r in wheel_window if r not in wheel_cards][0]
            possible_draws.append(
                {"missing_rank": missing_rank, "type": "wheel", "window": wheel_window}
            )

        # Now determine overall draw type and outs
        if not possible_draws:
            return {"count": 0, "type": None}

        # Count unique missing ranks
        unique_missing_ranks = set(draw["missing_rank"] for draw in possible_draws)

        draw_types = [draw["type"] for draw in possible_draws]

        # Check for OESD
        has_top_end = "top_end" in draw_types
        has_bottom_end = "bottom_end" in draw_types

        if has_top_end and has_bottom_end:
            # Check if any bottom_end and top_end pair are adjacent windows
            for draw1 in possible_draws:
                if draw1["type"] == "bottom_end":
                    for draw2 in possible_draws:
                        if draw2["type"] == "top_end":
                            if abs(draw1["window"][0] - draw2["window"][0]) == 1:
                                return {
                                    "count": 8,
                                    "type": "open_ended",
                                    "missing_ranks": sorted(
                                        [draw1["missing_rank"], draw2["missing_rank"]]
                                    ),
                                }

        # If we have multiple draws with different missing ranks, it's double gutshot
        if len(unique_missing_ranks) >= 2:
            return {
                "count": 8,
                "type": "double_gutshot",
                "missing_ranks": sorted(list(unique_missing_ranks)),
            }

        # Otherwise, single gutshot or wheel draw
        return {
            "count": 4,
            "type": "gutshot" if possible_draws[0]["type"] != "wheel" else "wheel",
            "missing_ranks": [possible_draws[0]["missing_rank"]],
        }

    def count_overcard_outs(
        self, hero_ranks, board_ranks, known_ranks
    ) -> Dict[str, Any]:
        """
        Count outs to pair an overcard.

        Args:
            hero_ranks: Hero card ranks
            board_ranks: Board card ranks
            known_ranks: All known ranks

        Returns:
            Dict with overcard out count and cards
        """
        if not board_ranks:
            return {"count": 0, "cards": []}

        max_board_rank = max(board_ranks)
        overcards = [r for r in hero_ranks if r > max_board_rank]

        if not overcards:
            return {"count": 0, "cards": []}

        # Check if we already have a pair in hand (pocket pair)
        # If so, don't count those as overcard outs since they're counted in pair_outs
        hero_rank_counts = Counter(hero_ranks)
        paired_ranks = {rank for rank, count in hero_rank_counts.items() if count == 2}

        # Each overcard has 3 outs (4 in deck - 1 in hand)
        # But exclude any that are already paired
        unique_overcards = [r for r in set(overcards) if r not in paired_ranks]
        total_outs = len(unique_overcards) * 3

        return {
            "count": total_outs,
            "cards": unique_overcards,
            "note": f"{len(unique_overcards)} overcard(s) with 3 outs each",
        }

    def count_pair_improvement_outs(
        self, hero_ranks, board_ranks, known_ranks
    ) -> Dict[str, Any]:
        """
        Count outs to improve a pair to trips or two pair.

        Args:
            hero_ranks: Hero card ranks
            board_ranks: Board card ranks
            known_ranks: All known ranks

        Returns:
            Dict with pair improvement out count
        """
        all_ranks = hero_ranks + board_ranks
        rank_counts = Counter(all_ranks)

        # Check if we have a pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]

        if not pairs:
            return {"count": 0, "to_trips": 0, "to_two_pair": 0}

        # If we have a pair:
        # - 2 outs to make trips (2 remaining cards of that rank)
        # - Outs to make two pair (3 outs for each unpaired card in hand)
        to_trips = 2

        # Two pair outs: if we have one unpaired card in hand
        unpaired_hero = [r for r in hero_ranks if rank_counts[r] == 1]
        to_two_pair = len(unpaired_hero) * 3 if unpaired_hero else 0

        total = to_trips + to_two_pair

        return {"count": total, "to_trips": to_trips, "to_two_pair": to_two_pair}

    def _create_card_from_rank_suit(self, rank: int, suit_int: int) -> int:
        """
        Create a treys card integer from rank and suit integers.

        Args:
            rank: treys rank (0=2, 1=3, ..., 11=K, 12=A)
            suit_int: treys suit bit flag (1=spades, 2=hearts, 4=diamonds, 8=clubs)

        Returns:
            treys card integer
        """
        rank_chars = "23456789TJQKA"
        suit_chars = {1: "s", 2: "h", 4: "d", 8: "c"}

        rank_char = rank_chars[rank]
        suit_char = suit_chars.get(suit_int, "s")

        return Card.new(f"{rank_char}{suit_char}")
