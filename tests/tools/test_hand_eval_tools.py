"""Tests for hand evaluation LangChain tools."""

from src.tools.hand_eval_tools import evaluate_hand, calculate_equity, analyze_spot


class TestEvaluateHand:
    """Tests for the evaluate_hand tool."""

    def test_evaluate_flush(self):
        """Test evaluating a flush."""
        result = evaluate_hand.invoke({"hero_hand": "As Ks", "board": "Qs Js 2s"})
        assert result["success"] is True
        assert result["hand_class"] == "Flush"

    def test_evaluate_straight(self):
        """Test evaluating a straight."""
        result = evaluate_hand.invoke({"hero_hand": "Ah Kh", "board": "Qc Js Tc"})
        assert result["success"] is True
        assert result["hand_class"] == "Straight"

    def test_evaluate_pair(self):
        """Test evaluating a pair."""
        result = evaluate_hand.invoke({"hero_hand": "Ah Kh", "board": "Ad 7s 2c"})
        assert result["success"] is True
        assert result["hand_class"] == "Pair"

    def test_evaluate_two_pair(self):
        """Test evaluating two pair."""
        result = evaluate_hand.invoke({"hero_hand": "Ah Kh", "board": "Ad Kd 2c"})
        assert result["success"] is True
        assert result["hand_class"] == "Two Pair"

    def test_evaluate_high_card(self):
        """Test evaluating high card."""
        result = evaluate_hand.invoke({"hero_hand": "Ah Kh", "board": "Qc 7s 2d"})
        assert result["success"] is True
        assert result["hand_class"] == "High Card"

    def test_invalid_hand_format(self):
        """Test error handling for invalid card format."""
        result = evaluate_hand.invoke({"hero_hand": "XX YY", "board": "Qc 7s 2d"})
        assert result["success"] is False
        assert "error" in result

    def test_invalid_board_size(self):
        """Test error handling for invalid board size."""
        result = evaluate_hand.invoke({"hero_hand": "As Ks", "board": "Qc 7s"})
        assert result["success"] is False
        assert "error" in result


class TestCalculateEquity:
    """Tests for the calculate_equity tool."""

    def test_equity_aa_vs_kk(self):
        """Test equity calculation for AA vs KK preflop."""
        result = calculate_equity.invoke(
            {
                "hero_hand": "As Ad",
                "villain_hand": "Kh Kd",
                "board": "",
                "iterations": 1000,
            }
        )
        assert result["success"] is True
        # AA should win approximately 80% vs KK
        assert 70 < result["hero_equity"] < 90
        assert 10 < result["villain_equity"] < 30

    def test_equity_with_board(self):
        """Test equity calculation with a flop."""
        result = calculate_equity.invoke(
            {
                "hero_hand": "As Ks",
                "villain_hand": "Qh Qd",
                "board": "Ah 7s 2c",
                "iterations": 1000,
            }
        )
        assert result["success"] is True
        # AK should be ahead with pair of aces
        assert result["hero_equity"] > 70

    def test_equity_invalid_duplicate(self):
        """Test error handling for duplicate cards."""
        result = calculate_equity.invoke(
            {
                "hero_hand": "As Ad",
                "villain_hand": "As Kd",  # Duplicate As
                "board": "",
            }
        )
        assert result["success"] is False
        assert "error" in result


class TestAnalyzeSpot:
    """Tests for the analyze_spot tool."""

    def test_analyze_with_full_info(self):
        """Test full spot analysis with all parameters."""
        result = analyze_spot.invoke(
            {
                "hero_hand": "Ah Kh",
                "board": "Qh Jh 2c",
                "pot_size": 100.0,
                "bet_to_call": 50.0,
                "effective_stack": 500.0,
            }
        )
        assert result["success"] is True
        assert "hand_strength" in result
        assert "equity" in result
        assert "out_count" in result
        assert "pot_odds" in result
        assert "recommendation" in result
        # With a flush draw, should have significant outs
        assert result["out_count"] >= 9

    def test_analyze_basic(self):
        """Test basic spot analysis without bet info."""
        result = analyze_spot.invoke(
            {
                "hero_hand": "As Ad",
                "board": "Kh 7s 2c",
            }
        )
        assert result["success"] is True
        assert "hand_strength" in result
        assert result["hand_strength"]["class"] == "Pair"

    def test_analyze_invalid_input(self):
        """Test error handling for invalid input."""
        result = analyze_spot.invoke(
            {
                "hero_hand": "invalid",
                "board": "Qh Jh 2c",
            }
        )
        assert result["success"] is False
        assert "error" in result

    def test_analyze_recommendation(self):
        """Test that recommendation is generated."""
        result = analyze_spot.invoke(
            {
                "hero_hand": "Ah Kh",
                "board": "Qh Jh 2c",
                "pot_size": 100.0,
                "bet_to_call": 50.0,
            }
        )
        assert result["success"] is True
        assert "recommendation" in result
        assert "action" in result["recommendation"]
        assert result["recommendation"]["action"] in ["CALL", "FOLD", "ANALYZE"]
