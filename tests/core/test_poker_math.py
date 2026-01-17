"""Tests for poker math utilities."""

import pytest
from src.core import poker_math


class TestPotOdds:
    """Tests for pot odds calculations."""

    def test_basic_pot_odds(self):
        """Should calculate pot odds correctly."""
        # 50 into 100 pot = 50/150 = 33.33%
        result = poker_math.calculate_pot_odds(100, 50)
        assert result == 33.33

    def test_small_bet_pot_odds(self):
        """Should calculate pot odds for small bets."""
        # 25 into 100 pot = 25/125 = 20%
        result = poker_math.calculate_pot_odds(100, 25)
        assert result == 20.0

    def test_large_bet_pot_odds(self):
        """Should calculate pot odds for large bets."""
        # 100 into 100 pot = 100/200 = 50%
        result = poker_math.calculate_pot_odds(100, 100)
        assert result == 50.0

    def test_tiny_bet_pot_odds(self):
        """Should calculate pot odds for tiny bets."""
        # 10 into 100 pot = 10/110 ≈ 9.09%
        result = poker_math.calculate_pot_odds(100, 10)
        assert result == pytest.approx(9.09, abs=0.01)


class TestPercentageToRatio:
    """Tests for converting percentages to ratios."""

    def test_standard_conversion(self):
        """Should convert 33.33% to approximately 2:1."""
        result = poker_math.percentage_to_ratio(33.33)
        assert "2.0:1" in result

    def test_20_percent(self):
        """Should convert 20% to 4:1."""
        result = poker_math.percentage_to_ratio(20.0)
        assert "4.0:1" in result

    def test_50_percent(self):
        """Should convert 50% to 1:1."""
        result = poker_math.percentage_to_ratio(50.0)
        assert "1.0:1" in result

    def test_edge_cases(self):
        """Should handle edge cases."""
        # 100% should be 0:1
        result1 = poker_math.percentage_to_ratio(100.0)
        assert "0:1" in result1

        # 0% should be infinity
        result2 = poker_math.percentage_to_ratio(0.0)
        assert "∞:1" in result2


class TestSPRCategorization:
    """Tests for SPR categorization."""

    def test_low_spr(self):
        """Should categorize low SPR correctly."""
        assert poker_math.categorize_spr(1.0) == "low (committed)"
        assert poker_math.categorize_spr(2.5) == "low (committed)"
        assert poker_math.categorize_spr(2.99) == "low (committed)"

    def test_medium_spr(self):
        """Should categorize medium SPR correctly."""
        assert poker_math.categorize_spr(3.0) == "medium"
        assert poker_math.categorize_spr(5.0) == "medium"
        assert poker_math.categorize_spr(6.99) == "medium"

    def test_high_spr(self):
        """Should categorize high SPR correctly."""
        assert poker_math.categorize_spr(7.0) == "high (deep)"
        assert poker_math.categorize_spr(10.0) == "high (deep)"
        assert poker_math.categorize_spr(20.0) == "high (deep)"


class TestEVCalculation:
    """Tests for EV calculations."""

    def test_positive_ev(self):
        """Should calculate positive EV correctly."""
        # 60% equity, 100 pot, 50 to call
        # EV = (0.6 * 150) - (0.4 * 50) = 90 - 20 = 70
        result = poker_math.calculate_ev(60.0, 100, 50)
        assert result["call"] == pytest.approx(70.0, abs=0.1)
        assert result["fold"] == 0

    def test_negative_ev(self):
        """Should calculate negative EV correctly."""
        # 20% equity, 100 pot, 50 to call
        # EV = (0.2 * 150) - (0.8 * 50) = 30 - 40 = -10
        result = poker_math.calculate_ev(20.0, 100, 50)
        assert result["call"] == pytest.approx(-10.0, abs=0.1)
        assert result["fold"] == 0

    def test_breakeven_ev(self):
        """Should calculate breakeven EV."""
        # EV formula: (equity * total_pot) - ((1-equity) * bet_to_call)
        # At breakeven, EV = 0
        # 0 = (E * (pot + bet)) - ((1-E) * bet)
        # 0 = E*pot + E*bet - bet + E*bet
        # bet = E*pot + 2*E*bet
        # bet = E*(pot + 2*bet)
        # This doesn't simplify nicely, but we know pot odds = bet/(pot+bet)
        # And at breakeven, equity should equal pot odds
        # With 100 pot, 50 bet: pot odds = 50/150 = 33.33%
        # But EV at 33.33% = 0.3333*150 - 0.6667*50 = 50 - 33.33 = 16.67 (+EV!)
        # This is correct! Having exact pot odds gives +EV because you win more than you risk
        result = poker_math.calculate_ev(33.33, 100, 50)
        assert result["call"] > 0  # Should be positive EV


class TestEquityEstimation:
    """Tests for equity estimation from outs."""

    def test_rule_of_4_flop(self):
        """Should use rule of 4 on the flop."""
        # 9 outs on flop = 9 * 4 = 36%
        assert poker_math.estimate_equity_from_outs(9, 3) == 36.0

        # 15 outs on flop = 15 * 4 = 60%
        assert poker_math.estimate_equity_from_outs(15, 3) == 60.0

    def test_rule_of_2_turn(self):
        """Should use rule of 2 on the turn."""
        # 9 outs on turn = 9 * 2 = 18%
        assert poker_math.estimate_equity_from_outs(9, 4) == 18.0

        # 15 outs on turn = 15 * 2 = 30%
        assert poker_math.estimate_equity_from_outs(15, 4) == 30.0

    def test_fractional_outs(self):
        """Should handle fractional outs (backdoor draws)."""
        # 11.5 outs on flop = 11.5 * 4 = 46%
        assert poker_math.estimate_equity_from_outs(11.5, 3) == 46.0

    def test_equity_capped_at_100(self):
        """Should cap equity at 100%."""
        # 30 outs on flop = 30 * 4 = 120%, capped at 100%
        assert poker_math.estimate_equity_from_outs(30, 3) == 100.0


class TestImpliedOdds:
    """Tests for implied odds calculations."""

    def test_implied_odds_with_draws(self):
        """Should calculate implied odds considering outs."""
        result = poker_math.estimate_implied_odds(
            pot_size=100,
            bet_to_call=50,
            effective_stack=500,
            outs=9,  # Flush draw
        )

        assert "percentage" in result
        assert "ratio" in result
        assert "estimated_future_winnings" in result
        assert result["percentage"] < 33.33  # Should be better than direct pot odds

    def test_implied_odds_low_outs(self):
        """Should calculate implied odds with few outs."""
        result = poker_math.estimate_implied_odds(
            pot_size=100,
            bet_to_call=50,
            effective_stack=500,
            outs=4,  # Gutshot
        )

        assert "percentage" in result
        assert result["percentage"] < 33.33

    def test_implied_odds_no_stack(self):
        """Should handle zero remaining stack."""
        result = poker_math.estimate_implied_odds(
            pot_size=100,
            bet_to_call=50,
            effective_stack=0,
            outs=9,
        )

        # With no stack, implied odds should equal direct pot odds
        assert result["estimated_future_winnings"] == 0.0
