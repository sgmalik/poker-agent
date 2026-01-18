"""GTO preflop range charts and queries."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from .range_parser import RANKS, RANK_VALUES, RangeParser


# Path to GTO ranges data file
DATA_DIR = Path(__file__).parent.parent.parent / "data"
GTO_RANGES_FILE = DATA_DIR / "gto_ranges.json"


class GTOCharts:
    """Load and query GTO preflop ranges."""

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize GTOCharts.

        Args:
            data_file: Path to GTO ranges JSON file (uses default if None)
        """
        self._data_file = data_file or GTO_RANGES_FILE
        self._data: Optional[Dict] = None
        self._parser = RangeParser()

    def _load_data(self) -> Dict:
        """Load GTO ranges data from file."""
        if self._data is None:
            if not self._data_file.exists():
                raise FileNotFoundError(f"GTO ranges file not found: {self._data_file}")

            with open(self._data_file, "r") as f:
                self._data = json.load(f)

        return self._data

    def get_positions(self) -> List[str]:
        """
        Get list of available positions.

        Returns:
            List of position names (e.g., ["UTG", "UTG1", "MP", ...])
        """
        data = self._load_data()
        return list(data.get("ranges", {}).keys())

    def get_actions(self, position: str) -> List[str]:
        """
        Get available actions for a position.

        Args:
            position: Position name (e.g., "UTG", "BTN")

        Returns:
            List of action names (e.g., ["open"], ["call_vs_BTN", "3bet_vs_BTN"])
        """
        data = self._load_data()
        pos_data = data.get("ranges", {}).get(position, {})
        return list(pos_data.keys())

    def get_range(self, position: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Get range data for a position and action.

        Args:
            position: Position name
            action: Action name (e.g., "open", "call_vs_BTN")

        Returns:
            Dict with keys: hands, notation, total_combos, percentage
            None if position/action not found
        """
        data = self._load_data()
        pos_data = data.get("ranges", {}).get(position, {})
        return pos_data.get(action)

    def is_hand_in_range(self, hand: str, position: str, action: str) -> bool:
        """
        Check if a hand is in a given range.

        Args:
            hand: Hand string (e.g., "AKs", "QQ")
            position: Position name
            action: Action name

        Returns:
            True if hand is in range, False otherwise
        """
        range_data = self.get_range(position, action)
        if not range_data:
            return False

        hand = hand.upper()
        hands = [h.upper() for h in range_data.get("hands", [])]

        # Normalize the hand for comparison
        if len(hand) == 3:
            r1, r2, suit = hand[0], hand[1], hand[2].lower()
            # Ensure high card first
            if RANK_VALUES.get(r1, 99) > RANK_VALUES.get(r2, 99):
                hand = r2 + r1 + suit
            else:
                hand = r1 + r2 + suit

        return hand.upper() in hands

    def hands_to_matrix(self, hands: List[str]) -> List[List[bool]]:
        """
        Convert a list of hands to a 13x13 matrix.

        Matrix layout:
            - Rows: First card rank (A=0, K=1, ..., 2=12)
            - Cols: Second card rank (A=0, K=1, ..., 2=12)
            - Diagonal (row==col): Pairs
            - Above diagonal (row<col): Suited hands
            - Below diagonal (row>col): Offsuit hands

        Args:
            hands: List of hand strings

        Returns:
            13x13 boolean matrix where True = hand in range
        """
        # Initialize 13x13 matrix with False
        matrix = [[False for _ in range(13)] for _ in range(13)]

        hands_upper = {h.upper() for h in hands}

        for hand in hands_upper:
            if len(hand) == 2:
                # Pair (e.g., AA, KK)
                rank = hand[0]
                idx = RANK_VALUES.get(rank, -1)
                if idx >= 0:
                    matrix[idx][idx] = True

            elif len(hand) == 3:
                r1, r2, suit = hand[0], hand[1], hand[2].lower()
                r1_idx = RANK_VALUES.get(r1, -1)
                r2_idx = RANK_VALUES.get(r2, -1)

                if r1_idx >= 0 and r2_idx >= 0:
                    # Ensure high card in row, low card in col for suited
                    # Swap for offsuit (below diagonal)
                    if suit == "s":
                        # Suited: row < col (above diagonal)
                        row = min(r1_idx, r2_idx)
                        col = max(r1_idx, r2_idx)
                    else:
                        # Offsuit: row > col (below diagonal)
                        row = max(r1_idx, r2_idx)
                        col = min(r1_idx, r2_idx)

                    matrix[row][col] = True

        return matrix

    def get_matrix_hand(self, row: int, col: int) -> str:
        """
        Get the hand string for a matrix position.

        Args:
            row: Row index (0-12)
            col: Column index (0-12)

        Returns:
            Hand string (e.g., "AA", "AKs", "AKo")
        """
        if row < 0 or row > 12 or col < 0 or col > 12:
            return ""

        r1 = RANKS[row]
        r2 = RANKS[col]

        if row == col:
            # Pair
            return r1 + r2
        elif row < col:
            # Suited (above diagonal)
            return r1 + r2 + "s"
        else:
            # Offsuit (below diagonal)
            return r2 + r1 + "o"

    def get_combo_count(self, row: int, col: int) -> int:
        """
        Get the number of combos for a matrix position.

        Args:
            row: Row index (0-12)
            col: Column index (0-12)

        Returns:
            Number of combinations (6 for pairs, 4 for suited, 12 for offsuit)
        """
        if row == col:
            return 6  # Pairs
        elif row < col:
            return 4  # Suited
        else:
            return 12  # Offsuit

    def parse_custom_range(self, notation: str) -> Dict:
        """
        Parse a custom range notation string.

        Args:
            notation: Range string (e.g., "QQ+, AKs, 98s+")

        Returns:
            Dict with parsed range data
        """
        return self._parser.parse(notation)


def get_gto_range(position: str, action: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get a GTO range."""
    charts = GTOCharts()
    return charts.get_range(position, action)


def get_range_matrix(position: str, action: str) -> Optional[List[List[bool]]]:
    """Convenience function to get a range as a 13x13 matrix."""
    charts = GTOCharts()
    range_data = charts.get_range(position, action)
    if not range_data:
        return None
    return charts.hands_to_matrix(range_data.get("hands", []))
