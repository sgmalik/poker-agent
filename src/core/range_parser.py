"""Range notation parser for poker hand ranges."""

from typing import Dict, List, Set, Tuple


# Standard rank order (highest to lowest)
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}


class RangeParser:
    """Parse poker range notation into hand lists."""

    def parse(self, notation: str) -> Dict:
        """
        Parse range notation into a structured result.

        Args:
            notation: Range string like "QQ+, AKs, 98s+"

        Returns:
            Dict with keys:
                - hands: List of hand strings (e.g., ["AA", "KK", "AKs"])
                - combos: Dict with combo counts by type
                - total_combos: Total number of combinations
                - percentage: Percentage of all possible hands
        """
        if not notation or not notation.strip():
            return {
                "hands": [],
                "combos": {"pairs": 0, "suited": 0, "offsuit": 0},
                "total_combos": 0,
                "percentage": 0.0,
            }

        hands: Set[str] = set()
        elements = [e.strip() for e in notation.split(",")]

        for element in elements:
            if not element:
                continue
            expanded = self.expand_notation(element)
            hands.update(expanded)

        hands_list = self._sort_hands(list(hands))
        combos = self.count_combos(hands_list)

        return {
            "hands": hands_list,
            "combos": combos,
            "total_combos": combos["total"],
            "percentage": round((combos["total"] / 1326) * 100, 1),
        }

    def expand_notation(self, element: str) -> List[str]:
        """
        Expand a single notation element into a list of hands.

        Supported formats:
            - Single hand: AA, AKs, AKo
            - Plus notation: QQ+ (QQ and better), ATs+ (ATs through AKs)
            - Range notation: QQ-88, A5s-A2s
        """
        element = element.strip().upper()

        # Handle range notation (e.g., QQ-88, A5s-A2s)
        if "-" in element:
            return self._expand_range(element)

        # Handle plus notation (e.g., QQ+, ATs+)
        if element.endswith("+"):
            return self._expand_plus(element[:-1])

        # Single hand
        return [self._normalize_hand(element)]

    def _expand_plus(self, base: str) -> List[str]:
        """Expand plus notation (e.g., QQ+ -> [QQ, KK, AA])."""
        hands = []

        if len(base) == 2 and base[0] == base[1]:
            # Pair plus (e.g., QQ+ -> QQ, KK, AA)
            rank = base[0]
            rank_idx = RANK_VALUES.get(rank, -1)
            if rank_idx == -1:
                raise ValueError(f"Invalid rank in notation: {base}")

            for i in range(rank_idx + 1):
                hands.append(RANKS[i] + RANKS[i])

        elif len(base) == 3:
            # Suited/offsuit plus (e.g., ATs+ -> ATs, AJs, AQs, AKs)
            high_rank = base[0]
            low_rank = base[1]
            suit_type = base[2].lower()

            if suit_type not in ("s", "o"):
                raise ValueError(f"Invalid suit type in notation: {base}")

            high_idx = RANK_VALUES.get(high_rank, -1)
            low_idx = RANK_VALUES.get(low_rank, -1)

            if high_idx == -1 or low_idx == -1:
                raise ValueError(f"Invalid ranks in notation: {base}")

            # Expand from low_rank up to high_rank-1
            for i in range(high_idx + 1, low_idx + 1):
                hands.append(high_rank + RANKS[i] + suit_type)

        elif len(base) == 2:
            # Unpaired without suit (e.g., AT+ means both ATs+ and ATo+)
            high_rank = base[0]
            low_rank = base[1]

            high_idx = RANK_VALUES.get(high_rank, -1)
            low_idx = RANK_VALUES.get(low_rank, -1)

            if high_idx == -1 or low_idx == -1:
                raise ValueError(f"Invalid ranks in notation: {base}")

            for i in range(high_idx + 1, low_idx + 1):
                hands.append(high_rank + RANKS[i] + "s")
                hands.append(high_rank + RANKS[i] + "o")

        return hands

    def _expand_range(self, notation: str) -> List[str]:
        """Expand range notation (e.g., QQ-88 -> [QQ, JJ, TT, 99, 88])."""
        parts = notation.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid range notation: {notation}")

        start = parts[0].strip().upper()
        end = parts[1].strip().upper()
        hands = []

        # Pair range (e.g., QQ-88)
        if (
            len(start) == 2
            and start[0] == start[1]
            and len(end) == 2
            and end[0] == end[1]
        ):
            start_idx = RANK_VALUES.get(start[0], -1)
            end_idx = RANK_VALUES.get(end[0], -1)

            if start_idx == -1 or end_idx == -1:
                raise ValueError(f"Invalid pair range: {notation}")

            # Ensure start is higher than end
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx

            for i in range(start_idx, end_idx + 1):
                hands.append(RANKS[i] + RANKS[i])

        # Suited/offsuit range (e.g., A5s-A2s)
        elif len(start) == 3 and len(end) == 3:
            if start[0] != end[0]:
                raise ValueError(f"Range must have same high card: {notation}")

            high_rank = start[0]
            suit_type = start[2].lower()

            if suit_type != end[2].lower():
                raise ValueError(f"Range must have same suit type: {notation}")

            start_low_idx = RANK_VALUES.get(start[1], -1)
            end_low_idx = RANK_VALUES.get(end[1], -1)

            if start_low_idx == -1 or end_low_idx == -1:
                raise ValueError(f"Invalid ranks in range: {notation}")

            # Ensure start is higher (lower index) than end
            if start_low_idx > end_low_idx:
                start_low_idx, end_low_idx = end_low_idx, start_low_idx

            for i in range(start_low_idx, end_low_idx + 1):
                hands.append(high_rank + RANKS[i] + suit_type)

        else:
            raise ValueError(f"Unsupported range notation: {notation}")

        return hands

    def _normalize_hand(self, hand: str) -> str:
        """Normalize a hand string (ensure high card first)."""
        hand = hand.upper()

        if len(hand) == 2:
            # Pair or unpaired without suit marker
            r1, r2 = hand[0], hand[1]
            if RANK_VALUES.get(r1, 99) > RANK_VALUES.get(r2, 99):
                return r2 + r1
            return hand

        elif len(hand) == 3:
            # Suited or offsuit
            r1, r2, suit = hand[0], hand[1], hand[2].lower()
            if RANK_VALUES.get(r1, 99) > RANK_VALUES.get(r2, 99):
                return r2 + r1 + suit
            return r1 + r2 + suit

        return hand

    def count_combos(self, hands: List[str]) -> Dict[str, int]:
        """
        Count combinations for a list of hands.

        Returns:
            Dict with keys: pairs, suited, offsuit, total
        """
        pairs = 0
        suited = 0
        offsuit = 0

        for hand in hands:
            if len(hand) == 2:
                # Pair (e.g., AA) = 6 combos
                pairs += 6
            elif len(hand) == 3:
                if hand[2].lower() == "s":
                    # Suited (e.g., AKs) = 4 combos
                    suited += 4
                else:
                    # Offsuit (e.g., AKo) = 12 combos
                    offsuit += 12

        return {
            "pairs": pairs,
            "suited": suited,
            "offsuit": offsuit,
            "total": pairs + suited + offsuit,
        }

    def _sort_hands(self, hands: List[str]) -> List[str]:
        """Sort hands by strength (pairs first, then by rank)."""

        def sort_key(hand: str) -> Tuple[int, int, int, int]:
            if len(hand) == 2:
                # Pairs: sort by rank (AA first)
                return (0, RANK_VALUES.get(hand[0], 99), 0, 0)
            elif len(hand) == 3:
                r1_val = RANK_VALUES.get(hand[0], 99)
                r2_val = RANK_VALUES.get(hand[1], 99)
                suit_val = 0 if hand[2].lower() == "s" else 1
                # Suited/offsuit: sort by high card, then low card, then suit
                return (1, r1_val, r2_val, suit_val)
            return (99, 99, 99, 99)

        return sorted(hands, key=sort_key)

    def hands_to_notation(self, hands: List[str]) -> str:
        """
        Convert a list of hands back to compact notation.

        This is a simplified version that doesn't fully compress ranges.
        """
        if not hands:
            return ""

        # For now, just return comma-separated hands
        # A full implementation would compress into ranges
        return ", ".join(hands)


def parse_range(notation: str) -> Dict:
    """Convenience function to parse a range notation."""
    parser = RangeParser()
    return parser.parse(notation)
