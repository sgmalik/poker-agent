"""Hand history core logic for card formatting, validation, and pattern analysis."""

from typing import Any, Dict, List, Optional, Tuple

# Position constants
POSITIONS = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]

# Result constants
RESULTS = ["won", "lost", "split"]

# Common tags for hand histories
COMMON_TAGS = [
    "bluff",
    "value",
    "mistake",
    "hero_call",
    "3bet",
    "4bet",
    "c-bet",
    "check-raise",
    "slow_play",
    "squeeze",
    "float",
    "probe",
    "donk",
    "overbet",
    "thin_value",
    "set_mining",
    "suited_connector",
    "pocket_pair",
    "cooler",
    "bad_beat",
    "river_bluff",
    "turn_barrel",
    "fold_equity",
]

# Suit symbols for display
SUIT_SYMBOLS = {
    "s": "\u2660",  # Spade
    "h": "\u2665",  # Heart
    "d": "\u2666",  # Diamond
    "c": "\u2663",  # Club
}

# Valid ranks and suits
VALID_RANKS = set("23456789TJQKA")
VALID_SUITS = set("shdc")


def format_cards(card_string: str) -> str:
    """
    Format a card string with Unicode suit symbols.

    Args:
        card_string: Cards like "As Kh" or "Qh Jh 2c"

    Returns:
        Formatted string like "A♠ K♥" or "Q♥ J♥ 2♣"
    """
    if not card_string:
        return ""

    cards = card_string.strip().split()
    formatted: List[str] = []

    for card in cards:
        if len(card) >= 2:
            rank = card[:-1].upper()
            suit = card[-1].lower()
            symbol = SUIT_SYMBOLS.get(suit, suit)
            formatted.append(f"{rank}{symbol}")
        else:
            formatted.append(card)

    return " ".join(formatted)


def validate_card(card: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a single card.

    Args:
        card: Card string like "As" or "Kh"

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not card:
        return False, "Card cannot be empty"

    if len(card) < 2:
        return False, f"Card '{card}' is too short"

    rank = card[:-1].upper()
    suit = card[-1].lower()

    if rank not in VALID_RANKS:
        return False, f"Invalid rank '{rank}' in card '{card}'"

    if suit not in VALID_SUITS:
        return False, f"Invalid suit '{suit}' in card '{card}'"

    return True, None


def validate_cards(card_string: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a string of cards.

    Args:
        card_string: Space-separated cards like "As Kh"

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not card_string or not card_string.strip():
        return True, None  # Empty is valid (optional field)

    cards = card_string.strip().split()
    seen_cards: set[str] = set()

    for card in cards:
        is_valid, error = validate_card(card)
        if not is_valid:
            return False, error

        # Normalize card for duplicate check
        normalized = card[:-1].upper() + card[-1].lower()
        if normalized in seen_cards:
            return False, f"Duplicate card: {card}"
        seen_cards.add(normalized)

    return True, None


def validate_hero_hand(hand: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a hero hand (must be exactly 2 cards).

    Args:
        hand: Hero hand like "As Kh"

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not hand or not hand.strip():
        return False, "Hero hand is required"

    cards = hand.strip().split()

    if len(cards) != 2:
        return False, f"Hero hand must have exactly 2 cards, got {len(cards)}"

    return validate_cards(hand)


def validate_board(board: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a board (must be 0, 3, 4, or 5 cards).

    Args:
        board: Board cards like "Qh Jh 2c"

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not board or not board.strip():
        return True, None  # Empty board is valid (preflop)

    cards = board.strip().split()
    num_cards = len(cards)

    if num_cards not in (3, 4, 5):
        return False, f"Board must have 3, 4, or 5 cards, got {num_cards}"

    return validate_cards(board)


def validate_hand_and_board(hero_hand: str, board: str) -> Tuple[bool, Optional[str]]:
    """
    Validate hero hand and board together (no duplicate cards).

    Args:
        hero_hand: Hero hand like "As Kh"
        board: Board cards like "Qh Jh 2c"

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate individual components
    is_valid, error = validate_hero_hand(hero_hand)
    if not is_valid:
        return False, error

    is_valid, error = validate_board(board)
    if not is_valid:
        return False, error

    # Check for duplicates between hand and board
    if board and board.strip():
        all_cards = hero_hand.strip() + " " + board.strip()
        cards = all_cards.split()
        seen: set[str] = set()

        for card in cards:
            normalized = card[:-1].upper() + card[-1].lower()
            if normalized in seen:
                return False, f"Duplicate card between hand and board: {card}"
            seen.add(normalized)

    return True, None


def parse_position(position: str) -> Optional[str]:
    """
    Parse and normalize a position string.

    Args:
        position: Position like "btn", "BTN", "button", etc.

    Returns:
        Normalized position or None if invalid
    """
    if not position:
        return None

    pos = position.strip().upper()

    # Handle common aliases
    aliases = {
        "BUTTON": "BTN",
        "CUTOFF": "CO",
        "HIJACK": "HJ",
        "LOJACK": "LJ",
        "MIDDLE": "MP",
        "UNDER": "UTG",
        "SMALL": "SB",
        "BIG": "BB",
    }

    for alias, standard in aliases.items():
        if alias in pos:
            return standard

    if pos in POSITIONS:
        return pos

    return None


def suggest_tags(
    action_summary: Optional[str] = None,
    result: Optional[str] = None,
    hero_hand: Optional[str] = None,
) -> List[str]:
    """
    Suggest tags based on action summary and result.

    Args:
        action_summary: Description of the action
        result: Hand result (won, lost, split)
        hero_hand: Hero's hole cards

    Returns:
        List of suggested tags
    """
    suggestions: List[str] = []

    if action_summary:
        action = action_summary.lower()

        # Action-based suggestions
        if "bluff" in action:
            suggestions.append("bluff")
        if "value" in action:
            suggestions.append("value")
        if "c-bet" in action or "cbet" in action or "continuation" in action:
            suggestions.append("c-bet")
        if "3bet" in action or "3-bet" in action or "three bet" in action:
            suggestions.append("3bet")
        if "4bet" in action or "4-bet" in action or "four bet" in action:
            suggestions.append("4bet")
        if "check-raise" in action or "check raise" in action:
            suggestions.append("check-raise")
        if "slow" in action or "trap" in action:
            suggestions.append("slow_play")
        if "squeeze" in action:
            suggestions.append("squeeze")
        if "float" in action:
            suggestions.append("float")
        if "overbet" in action or "over bet" in action:
            suggestions.append("overbet")
        if "hero call" in action or "hero-call" in action:
            suggestions.append("hero_call")
        if "mistake" in action or "error" in action or "bad" in action:
            suggestions.append("mistake")
        if "cooler" in action:
            suggestions.append("cooler")

    # Hand-based suggestions
    if hero_hand:
        hand = hero_hand.upper()
        ranks = [card[:-1] for card in hand.split()]
        suits = [card[-1].lower() for card in hand.split()]

        # Pocket pair
        if len(ranks) == 2 and ranks[0] == ranks[1]:
            suggestions.append("pocket_pair")
            if ranks[0] in ["2", "3", "4", "5", "6", "7", "8"]:
                suggestions.append("set_mining")

        # Suited
        if len(suits) == 2 and suits[0] == suits[1]:
            # Suited connector check
            rank_order = "23456789TJQKA"
            if len(ranks) == 2:
                try:
                    i1 = rank_order.index(ranks[0])
                    i2 = rank_order.index(ranks[1])
                    if abs(i1 - i2) == 1:
                        suggestions.append("suited_connector")
                except ValueError:
                    pass

    # Result-based suggestions
    if result == "lost" and action_summary:
        action = action_summary.lower()
        if "cooler" not in action and "bad beat" not in action:
            if "all in" in action or "allin" in action:
                if "called" in action:
                    suggestions.append("bad_beat")

    return list(set(suggestions))  # Remove duplicates


def analyze_hand_patterns(hands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze patterns in a list of hands.

    Args:
        hands: List of hand history dicts

    Returns:
        Dict with pattern analysis including win rates by position/tag,
        bluff success rate, etc.
    """
    if not hands:
        return {
            "total_hands": 0,
            "position_win_rates": {},
            "tag_win_rates": {},
            "bluff_success_rate": 0.0,
            "value_bet_win_rate": 0.0,
            "street_distribution": {},
            "insights": [],
        }

    total = len(hands)
    wins = sum(1 for h in hands if h.get("result") == "won")

    # Win rate by position
    position_stats: Dict[str, Dict[str, int]] = {}
    for h in hands:
        pos = h.get("position", "Unknown")
        if pos not in position_stats:
            position_stats[pos] = {"total": 0, "won": 0}
        position_stats[pos]["total"] += 1
        if h.get("result") == "won":
            position_stats[pos]["won"] += 1

    position_win_rates = {
        pos: (stats["won"] / stats["total"] * 100) if stats["total"] > 0 else 0
        for pos, stats in position_stats.items()
    }

    # Win rate by tag
    tag_stats: Dict[str, Dict[str, int]] = {}
    for h in hands:
        tags = h.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        for tag in tags:
            if tag not in tag_stats:
                tag_stats[tag] = {"total": 0, "won": 0}
            tag_stats[tag]["total"] += 1
            if h.get("result") == "won":
                tag_stats[tag]["won"] += 1

    tag_win_rates = {
        tag: (stats["won"] / stats["total"] * 100) if stats["total"] > 0 else 0
        for tag, stats in tag_stats.items()
    }

    # Bluff success rate
    bluff_hands = [h for h in hands if "bluff" in (h.get("tags") or [])]
    bluff_wins = sum(1 for h in bluff_hands if h.get("result") == "won")
    bluff_success = (bluff_wins / len(bluff_hands) * 100) if bluff_hands else 0.0

    # Value bet win rate
    value_hands = [h for h in hands if "value" in (h.get("tags") or [])]
    value_wins = sum(1 for h in value_hands if h.get("result") == "won")
    value_win_rate = (value_wins / len(value_hands) * 100) if value_hands else 0.0

    # Street distribution
    street_counts: Dict[str, int] = {}
    for h in hands:
        street = h.get("street", "unknown")
        street_counts[street] = street_counts.get(street, 0) + 1

    street_distribution = {
        street: (count / total * 100) if total > 0 else 0
        for street, count in street_counts.items()
    }

    # Generate insights
    insights = []

    # Best position
    if position_win_rates:
        best_pos = max(position_win_rates.items(), key=lambda x: x[1])
        if position_stats[best_pos[0]]["total"] >= 5:
            insights.append(
                f"Best position: {best_pos[0]} ({best_pos[1]:.1f}% win rate)"
            )

    # Worst position
    if position_win_rates:
        positions_with_data = {
            k: v
            for k, v in position_win_rates.items()
            if position_stats[k]["total"] >= 5
        }
        if positions_with_data:
            worst_pos = min(positions_with_data.items(), key=lambda x: x[1])
            insights.append(
                f"Weakest position: {worst_pos[0]} ({worst_pos[1]:.1f}% win rate)"
            )

    # Bluff analysis
    if len(bluff_hands) >= 5:
        if bluff_success < 30:
            insights.append(
                f"Low bluff success rate ({bluff_success:.1f}%). Consider tightening."
            )
        elif bluff_success > 60:
            insights.append(
                f"High bluff success ({bluff_success:.1f}%). May be underbluffing."
            )

    # Tag analysis
    for tag, stats in tag_stats.items():
        if stats["total"] >= 5:
            win_rate = tag_win_rates[tag]
            if win_rate < 30:
                insights.append(f"Losing with '{tag}' hands ({win_rate:.1f}% win rate)")

    return {
        "total_hands": total,
        "overall_win_rate": (wins / total * 100) if total > 0 else 0.0,
        "position_win_rates": position_win_rates,
        "tag_win_rates": tag_win_rates,
        "bluff_success_rate": bluff_success,
        "value_bet_win_rate": value_win_rate,
        "street_distribution": street_distribution,
        "insights": insights,
    }


def format_board_by_street(board: str) -> Dict[str, str]:
    """
    Format a board by street (flop, turn, river).

    Args:
        board: Full board like "Qh Jh 2c 5d 9s"

    Returns:
        Dict with formatted cards for each street
    """
    if not board or not board.strip():
        return {"flop": "", "turn": "", "river": ""}

    cards = board.strip().split()

    result = {
        "flop": "",
        "turn": "",
        "river": "",
    }

    if len(cards) >= 3:
        result["flop"] = format_cards(" ".join(cards[:3]))
    if len(cards) >= 4:
        result["turn"] = format_cards(cards[3])
    if len(cards) >= 5:
        result["river"] = format_cards(cards[4])

    return result


def get_hand_summary(hand: Dict[str, Any]) -> str:
    """
    Generate a brief summary of a hand.

    Args:
        hand: Hand history dict

    Returns:
        Brief summary string
    """
    hero = format_cards(hand.get("hero_hand", ""))
    position = hand.get("position", "")
    result = hand.get("result", "")
    street = hand.get("street", "preflop")

    result_text = "Won" if result == "won" else "Lost" if result == "lost" else "Split"

    return f"{hero} from {position} - {result_text} on {street}"
