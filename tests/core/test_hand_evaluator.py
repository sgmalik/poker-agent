"""Tests for hand evaluation and equity calculation."""

import pytest
from src.core.hand_evaluator import (
    HandEvaluator,
    EquityCalculator,
    evaluate_hand_simple,
    calculate_equity_simple,
)


class TestHandEvaluator:
    """Tests for HandEvaluator class."""

    @pytest.fixture
    def evaluator(self):
        """Create HandEvaluator instance for tests."""
        return HandEvaluator()

    def test_royal_flush(self, evaluator):
        """Should correctly identify a royal flush."""
        result = evaluator.evaluate("As Ks", "Qs Js Ts")
        assert result["hand_class"] == "Royal Flush"  # treys does distinguish royal
        assert result["rank"] == 1  # Best possible hand

    def test_flush(self, evaluator):
        """Should correctly identify a flush."""
        result = evaluator.evaluate("Ah Kh", "Qh Jh 9h")
        assert result["hand_class"] == "Flush"

    def test_straight(self, evaluator):
        """Should correctly identify a straight."""
        result = evaluator.evaluate("9h 8d", "7s 6c 5h")
        assert result["hand_class"] == "Straight"

    def test_full_house(self, evaluator):
        """Should correctly identify a full house."""
        result = evaluator.evaluate("9h 9d", "9s 2c 2h")
        assert result["hand_class"] == "Full House"

    def test_four_of_a_kind(self, evaluator):
        """Should correctly identify quads."""
        result = evaluator.evaluate("9h 9d", "9s 9c 2h")
        assert result["hand_class"] == "Four of a Kind"

    def test_three_of_a_kind(self, evaluator):
        """Should correctly identify trips."""
        result = evaluator.evaluate("9h 9d", "9s 7c 2h")
        assert result["hand_class"] == "Three of a Kind"

    def test_two_pair(self, evaluator):
        """Should correctly identify two pair."""
        result = evaluator.evaluate("9h 9d", "7s 7c 2h")
        assert result["hand_class"] == "Two Pair"

    def test_one_pair(self, evaluator):
        """Should correctly identify a pair."""
        result = evaluator.evaluate("9h 9d", "7s 6c 2h")
        assert result["hand_class"] == "Pair"

    def test_high_card(self, evaluator):
        """Should correctly identify high card."""
        result = evaluator.evaluate("Ah Kd", "2s 7c 9h")
        assert result["hand_class"] == "High Card"

    def test_wheel_straight(self, evaluator):
        """Should correctly identify A-2-3-4-5 straight (wheel)."""
        result = evaluator.evaluate("Ah 2d", "3s 4c 5h")
        assert result["hand_class"] == "Straight"

    def test_invalid_hero_hand_too_few_cards(self, evaluator):
        """Should raise error if hero hand has wrong number of cards."""
        with pytest.raises(ValueError, match="exactly 2 cards"):
            evaluator.evaluate("As", "Qh Jh 2c")

    def test_invalid_hero_hand_too_many_cards(self, evaluator):
        """Should raise error if hero hand has too many cards."""
        with pytest.raises(ValueError, match="exactly 2 cards"):
            evaluator.evaluate("As Ks Qh", "Qh Jh 2c")

    def test_invalid_board_too_few_cards(self, evaluator):
        """Should raise error if board has too few cards."""
        with pytest.raises(ValueError, match="3-5 cards"):
            evaluator.evaluate("As Ks", "Qh Jh")

    def test_invalid_board_too_many_cards(self, evaluator):
        """Should raise error if board has too many cards."""
        with pytest.raises(ValueError, match="3-5 cards"):
            evaluator.evaluate("As Ks", "Qh Jh 2c 3d 4s 5h")

    def test_invalid_card_format(self, evaluator):
        """Should raise error for invalid card format."""
        with pytest.raises(ValueError, match="Invalid card"):
            evaluator.evaluate("XX YY", "Qh Jh 2c")

    def test_simple_evaluation(self):
        """Test convenience function."""
        result = evaluate_hand_simple("Ah Kh", "Qh Jh Th")
        assert result == "Royal Flush"


class TestEquityCalculator:
    """Tests for EquityCalculator class."""

    @pytest.fixture
    def calculator(self):
        """Create EquityCalculator instance for tests."""
        return EquityCalculator()

    def test_aces_vs_kings_preflop(self, calculator):
        """AA vs KK preflop should be ~80% for AA."""
        result = calculator.calculate("As Ad", "Kh Kd", "", iterations=5000)

        # Allow variance in Monte Carlo (±3%)
        assert 77 <= result["hero_equity"] <= 83
        assert 17 <= result["villain_equity"] <= 23

        # Check components
        assert result["iterations"] == 5000
        assert result["hero_wins"] + result["villain_wins"] + result["ties"] == 5000

    def test_equity_sums_to_100(self, calculator):
        """Hero equity + villain equity should equal 100%."""
        result = calculator.calculate("As Ks", "Qh Qd", "Ah 7s 2c", iterations=5000)
        total = result["hero_equity"] + result["villain_equity"]
        assert 99.9 <= total <= 100.1  # Account for rounding

    def test_dominated_hand(self, calculator):
        """AK vs AQ should heavily favor AK."""
        result = calculator.calculate("As Ks", "Ah Qd", "", iterations=5000)
        assert result["hero_equity"] > 65  # AK dominates AQ

    def test_made_hand_vs_draw(self, calculator):
        """Test equity with made hand vs draw."""
        # Top pair vs flush draw
        result = calculator.calculate(
            "Ah Kd",  # Top pair
            "Qh Jh",  # Flush draw
            "As 7h 2h",  # Board
            iterations=5000,
        )
        # Hero should be ahead (~55-65%)
        assert 50 <= result["hero_equity"] <= 70

    def test_duplicate_cards_error(self, calculator):
        """Should raise error if duplicate cards exist."""
        with pytest.raises(ValueError, match="Duplicate cards"):
            calculator.calculate("As Ks", "As Kd", "")  # As appears twice

    def test_invalid_hero_cards(self, calculator):
        """Should raise error for invalid hero hand."""
        with pytest.raises(ValueError, match="2 cards"):
            calculator.calculate("As", "Kh Kd", "")

    def test_invalid_villain_cards(self, calculator):
        """Should raise error for invalid villain hand."""
        with pytest.raises(ValueError, match="2 cards"):
            calculator.calculate("As Ad", "Kh", "")

    def test_invalid_board(self, calculator):
        """Should raise error for too many board cards."""
        with pytest.raises(ValueError, match="max 5 cards"):
            calculator.calculate("As Ad", "Kh Kd", "Qh Jh Th 9h 8h 7h")

    def test_preflop_equity(self, calculator):
        """Test preflop equity with no board."""
        result = calculator.calculate("9h 9d", "Ah Kh", "", iterations=5000)
        # 99 vs AK is roughly 50-50 (slight edge to 99)
        assert 48 <= result["hero_equity"] <= 58

    def test_flop_equity(self, calculator):
        """Test equity on the flop."""
        result = calculator.calculate("Ah Kh", "Qd Qc", "As 7s 2c", iterations=5000)
        # AK hit top pair, should be ahead of QQ
        assert result["hero_equity"] > 70

    def test_turn_equity(self, calculator):
        """Test equity on the turn."""
        result = calculator.calculate(
            "Ah Kh", "Qd Qc", "As 7s 2c 5d", iterations=5000
        )
        assert result["hero_equity"] > 70

    def test_river_equity(self, calculator):
        """Test equity on the river (deterministic)."""
        result = calculator.calculate(
            "Ah Kh", "Qd Qc", "As 7s 2c 5d 9h", iterations=100
        )
        # On river, equity should be 100 or 0 (no variance)
        assert result["hero_equity"] == 100.0 or result["hero_equity"] == 0.0

    def test_simple_equity(self):
        """Test convenience function."""
        equity = calculate_equity_simple("As Ad", "Kh Kd", "", iterations=5000)
        assert 77 <= equity <= 83  # AA vs KK ~80%


def test_integration_full_workflow():
    """Test complete workflow: evaluate hand and calculate equity."""
    # Evaluate hand
    hand_class = evaluate_hand_simple("Ah Kh", "Qh Jh 2c")
    assert hand_class == "High Card"  # No pair, just high card

    # Calculate equity
    equity = calculate_equity_simple("Ah Kh", "Qd Qc", "As 7s 2c", iterations=5000)
    assert equity > 70  # AK hit top pair vs QQ


def test_edge_case_same_hand():
    """Test equity when both players have the same hand (different suits)."""
    calc = EquityCalculator()
    result = calc.calculate("As Ks", "Ah Kh", "", iterations=5000)

    # Should be very close to 50-50
    assert 48 <= result["hero_equity"] <= 52
    assert 48 <= result["villain_equity"] <= 52
