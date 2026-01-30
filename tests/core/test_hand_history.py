"""Tests for hand history core logic."""

import pytest

from src.core.hand_history import (
    POSITIONS,
    RESULTS,
    COMMON_TAGS,
    format_cards,
    validate_card,
    validate_cards,
    validate_hero_hand,
    validate_board,
    validate_hand_and_board,
    parse_position,
    suggest_tags,
    analyze_hand_patterns,
    format_board_by_street,
    get_hand_summary,
)


class TestFormatCards:
    """Tests for format_cards function."""

    def test_format_single_card(self):
        """Should format a single card with suit symbol."""
        assert format_cards("As") == "A♠"
        assert format_cards("Kh") == "K♥"
        assert format_cards("Qd") == "Q♦"
        assert format_cards("Jc") == "J♣"

    def test_format_multiple_cards(self):
        """Should format multiple cards."""
        assert format_cards("As Kh") == "A♠ K♥"
        assert format_cards("Qh Jh 2c") == "Q♥ J♥ 2♣"

    def test_format_full_board(self):
        """Should format a full board."""
        result = format_cards("Qh Jh 2c 5d 9s")
        assert result == "Q♥ J♥ 2♣ 5♦ 9♠"

    def test_format_ten(self):
        """Should handle 10/T correctly."""
        assert format_cards("Ts") == "T♠"
        assert format_cards("10s") == "10♠"

    def test_format_empty(self):
        """Should handle empty input."""
        assert format_cards("") == ""
        assert format_cards(None) == ""

    def test_format_preserves_unknown(self):
        """Should preserve unknown cards."""
        assert format_cards("X") == "X"


class TestValidateCard:
    """Tests for validate_card function."""

    def test_valid_cards(self):
        """Should validate correct cards."""
        assert validate_card("As")[0] is True
        assert validate_card("Kh")[0] is True
        assert validate_card("2c")[0] is True
        assert validate_card("Td")[0] is True

    def test_invalid_rank(self):
        """Should reject invalid ranks."""
        is_valid, error = validate_card("Xs")
        assert is_valid is False
        assert "rank" in error.lower()

    def test_invalid_suit(self):
        """Should reject invalid suits."""
        is_valid, error = validate_card("Ax")
        assert is_valid is False
        assert "suit" in error.lower()

    def test_empty_card(self):
        """Should reject empty cards."""
        is_valid, error = validate_card("")
        assert is_valid is False

    def test_too_short(self):
        """Should reject cards that are too short."""
        is_valid, error = validate_card("A")
        assert is_valid is False


class TestValidateCards:
    """Tests for validate_cards function."""

    def test_valid_cards(self):
        """Should validate correct card strings."""
        assert validate_cards("As Kh")[0] is True
        assert validate_cards("Qh Jh 2c")[0] is True
        assert validate_cards("Qh Jh 2c 5d 9s")[0] is True

    def test_empty_string(self):
        """Should accept empty string."""
        assert validate_cards("")[0] is True
        assert validate_cards("   ")[0] is True

    def test_duplicate_cards(self):
        """Should reject duplicate cards."""
        is_valid, error = validate_cards("As As")
        assert is_valid is False
        assert "duplicate" in error.lower()

    def test_case_insensitive_duplicates(self):
        """Should detect duplicates regardless of case."""
        is_valid, error = validate_cards("As as")
        assert is_valid is False
        assert "duplicate" in error.lower()


class TestValidateHeroHand:
    """Tests for validate_hero_hand function."""

    def test_valid_hands(self):
        """Should validate correct hero hands."""
        assert validate_hero_hand("As Kh")[0] is True
        assert validate_hero_hand("2c 2d")[0] is True

    def test_requires_two_cards(self):
        """Should require exactly 2 cards."""
        is_valid, error = validate_hero_hand("As")
        assert is_valid is False
        assert "2 cards" in error.lower()

        is_valid, error = validate_hero_hand("As Kh Qd")
        assert is_valid is False
        assert "2 cards" in error.lower()

    def test_required_field(self):
        """Should require a hand."""
        is_valid, error = validate_hero_hand("")
        assert is_valid is False
        assert "required" in error.lower()


class TestValidateBoard:
    """Tests for validate_board function."""

    def test_valid_boards(self):
        """Should validate correct boards."""
        assert validate_board("")[0] is True  # Empty (preflop)
        assert validate_board("Qh Jh 2c")[0] is True  # Flop
        assert validate_board("Qh Jh 2c 5d")[0] is True  # Turn
        assert validate_board("Qh Jh 2c 5d 9s")[0] is True  # River

    def test_invalid_card_count(self):
        """Should reject invalid card counts."""
        is_valid, error = validate_board("Qh Jh")  # 2 cards
        assert is_valid is False
        assert "3, 4, or 5" in error

        is_valid, error = validate_board("Qh Jh 2c 5d 9s Tc")  # 6 cards
        assert is_valid is False


class TestValidateHandAndBoard:
    """Tests for validate_hand_and_board function."""

    def test_valid_combination(self):
        """Should validate hand and board together."""
        assert validate_hand_and_board("As Kh", "Qh Jh 2c")[0] is True
        assert validate_hand_and_board("As Kh", "")[0] is True

    def test_duplicate_between_hand_and_board(self):
        """Should reject cards appearing in both hand and board."""
        is_valid, error = validate_hand_and_board("As Kh", "As Jh 2c")
        assert is_valid is False
        assert "duplicate" in error.lower()

    def test_validates_individual_components(self):
        """Should validate individual components."""
        # Invalid hand
        is_valid, error = validate_hand_and_board("As", "Qh Jh 2c")
        assert is_valid is False

        # Invalid board
        is_valid, error = validate_hand_and_board("As Kh", "Qh Jh")
        assert is_valid is False


class TestParsePosition:
    """Tests for parse_position function."""

    def test_standard_positions(self):
        """Should parse standard position abbreviations."""
        assert parse_position("BTN") == "BTN"
        assert parse_position("CO") == "CO"
        assert parse_position("BB") == "BB"
        assert parse_position("SB") == "SB"

    def test_case_insensitive(self):
        """Should be case insensitive."""
        assert parse_position("btn") == "BTN"
        assert parse_position("Btn") == "BTN"

    def test_aliases(self):
        """Should handle common aliases."""
        assert parse_position("button") == "BTN"
        assert parse_position("cutoff") == "CO"
        assert parse_position("small blind") == "SB"
        assert parse_position("big blind") == "BB"

    def test_invalid_position(self):
        """Should return None for invalid positions."""
        assert parse_position("xyz") is None
        assert parse_position("") is None


class TestSuggestTags:
    """Tests for suggest_tags function."""

    def test_bluff_detection(self):
        """Should suggest bluff tag."""
        tags = suggest_tags(action_summary="Made a big bluff on the river")
        assert "bluff" in tags

    def test_value_detection(self):
        """Should suggest value tag."""
        tags = suggest_tags(action_summary="Value bet on the river")
        assert "value" in tags

    def test_cbet_detection(self):
        """Should suggest c-bet tag."""
        tags = suggest_tags(action_summary="Made a c-bet on the flop")
        assert "c-bet" in tags

        tags = suggest_tags(action_summary="Continuation bet")
        assert "c-bet" in tags

    def test_pocket_pair_detection(self):
        """Should suggest pocket pair tag."""
        tags = suggest_tags(hero_hand="As Ad")
        assert "pocket_pair" in tags

    def test_suited_connector_detection(self):
        """Should suggest suited connector tag."""
        tags = suggest_tags(hero_hand="7s 8s")
        assert "suited_connector" in tags

    def test_set_mining_suggestion(self):
        """Should suggest set mining for small pairs."""
        tags = suggest_tags(hero_hand="5s 5h")
        assert "pocket_pair" in tags
        assert "set_mining" in tags

    def test_no_duplicates(self):
        """Should not return duplicate tags."""
        tags = suggest_tags(action_summary="Bluff bluff bluff", hero_hand="As Kh")
        assert tags.count("bluff") == 1


class TestAnalyzeHandPatterns:
    """Tests for analyze_hand_patterns function."""

    def test_empty_hands(self):
        """Should handle empty hand list."""
        result = analyze_hand_patterns([])
        assert result["total_hands"] == 0
        assert result["position_win_rates"] == {}

    def test_calculates_win_rate(self):
        """Should calculate overall win rate."""
        hands = [
            {"result": "won", "position": "BTN"},
            {"result": "won", "position": "BTN"},
            {"result": "lost", "position": "BTN"},
        ]
        result = analyze_hand_patterns(hands)
        assert result["total_hands"] == 3
        assert result["overall_win_rate"] == pytest.approx(66.67, rel=0.1)

    def test_position_win_rates(self):
        """Should calculate win rates by position."""
        hands = [
            {"result": "won", "position": "BTN"},
            {"result": "lost", "position": "BB"},
            {"result": "won", "position": "BTN"},
        ]
        result = analyze_hand_patterns(hands)
        assert result["position_win_rates"]["BTN"] == 100.0
        assert result["position_win_rates"]["BB"] == 0.0

    def test_tag_win_rates(self):
        """Should calculate win rates by tag."""
        hands = [
            {"result": "won", "position": "BTN", "tags": ["value"]},
            {"result": "lost", "position": "BTN", "tags": ["bluff"]},
        ]
        result = analyze_hand_patterns(hands)
        assert result["tag_win_rates"]["value"] == 100.0
        assert result["tag_win_rates"]["bluff"] == 0.0

    def test_bluff_success_rate(self):
        """Should calculate bluff success rate."""
        hands = [
            {"result": "won", "position": "BTN", "tags": ["bluff"]},
            {"result": "won", "position": "BTN", "tags": ["bluff"]},
            {"result": "lost", "position": "BTN", "tags": ["bluff"]},
            {"result": "won", "position": "BTN", "tags": ["value"]},
        ]
        result = analyze_hand_patterns(hands)
        assert result["bluff_success_rate"] == pytest.approx(66.67, rel=0.1)

    def test_street_distribution(self):
        """Should calculate street distribution."""
        hands = [
            {"result": "won", "position": "BTN", "street": "flop"},
            {"result": "won", "position": "BTN", "street": "river"},
            {"result": "won", "position": "BTN", "street": "river"},
        ]
        result = analyze_hand_patterns(hands)
        assert result["street_distribution"]["flop"] == pytest.approx(33.33, rel=0.1)
        assert result["street_distribution"]["river"] == pytest.approx(66.67, rel=0.1)


class TestFormatBoardByStreet:
    """Tests for format_board_by_street function."""

    def test_full_board(self):
        """Should split full board into streets."""
        result = format_board_by_street("Qh Jh 2c 5d 9s")
        assert result["flop"] == "Q♥ J♥ 2♣"
        assert result["turn"] == "5♦"
        assert result["river"] == "9♠"

    def test_flop_only(self):
        """Should handle flop only."""
        result = format_board_by_street("Qh Jh 2c")
        assert result["flop"] == "Q♥ J♥ 2♣"
        assert result["turn"] == ""
        assert result["river"] == ""

    def test_through_turn(self):
        """Should handle through turn."""
        result = format_board_by_street("Qh Jh 2c 5d")
        assert result["flop"] == "Q♥ J♥ 2♣"
        assert result["turn"] == "5♦"
        assert result["river"] == ""

    def test_empty_board(self):
        """Should handle empty board."""
        result = format_board_by_street("")
        assert result["flop"] == ""
        assert result["turn"] == ""
        assert result["river"] == ""


class TestGetHandSummary:
    """Tests for get_hand_summary function."""

    def test_basic_summary(self):
        """Should generate basic summary."""
        hand = {
            "hero_hand": "As Kh",
            "position": "BTN",
            "result": "won",
            "street": "river",
        }
        summary = get_hand_summary(hand)
        assert "A♠ K♥" in summary
        assert "BTN" in summary
        assert "Won" in summary
        assert "river" in summary

    def test_lost_hand(self):
        """Should show Lost for losing hands."""
        hand = {
            "hero_hand": "7c 2s",
            "position": "BB",
            "result": "lost",
            "street": "flop",
        }
        summary = get_hand_summary(hand)
        assert "Lost" in summary

    def test_split_pot(self):
        """Should show Split for split pots."""
        hand = {
            "hero_hand": "As Kh",
            "position": "SB",
            "result": "split",
            "street": "river",
        }
        summary = get_hand_summary(hand)
        assert "Split" in summary


class TestConstants:
    """Tests for module constants."""

    def test_positions(self):
        """Should have all standard positions."""
        assert "UTG" in POSITIONS
        assert "BTN" in POSITIONS
        assert "SB" in POSITIONS
        assert "BB" in POSITIONS
        assert "CO" in POSITIONS
        assert "HJ" in POSITIONS

    def test_results(self):
        """Should have all result types."""
        assert "won" in RESULTS
        assert "lost" in RESULTS
        assert "split" in RESULTS

    def test_common_tags(self):
        """Should have common tags."""
        assert "bluff" in COMMON_TAGS
        assert "value" in COMMON_TAGS
        assert "c-bet" in COMMON_TAGS
        assert "3bet" in COMMON_TAGS
