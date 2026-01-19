"""Tests for range notation parser."""

import pytest
from src.core.range_parser import RangeParser, RANKS, RANK_VALUES


class TestRangeParser:
    """Tests for RangeParser class."""

    @pytest.fixture
    def parser(self):
        """Create RangeParser instance for tests."""
        return RangeParser()

    # Single hand parsing tests
    def test_parse_single_pair(self, parser):
        """Should parse a single pair."""
        result = parser.parse("AA")
        assert "AA" in result["hands"]
        assert result["combos"]["pairs"] == 6
        assert result["total_combos"] == 6

    def test_parse_single_suited(self, parser):
        """Should parse a single suited hand."""
        result = parser.parse("AKs")
        assert "AKs" in result["hands"]
        assert result["combos"]["suited"] == 4
        assert result["total_combos"] == 4

    def test_parse_single_offsuit(self, parser):
        """Should parse a single offsuit hand."""
        result = parser.parse("AKo")
        assert "AKo" in result["hands"]
        assert result["combos"]["offsuit"] == 12
        assert result["total_combos"] == 12

    # Plus notation tests
    def test_parse_pair_plus(self, parser):
        """Should expand pair plus notation (QQ+ -> QQ, KK, AA)."""
        result = parser.parse("QQ+")
        assert "QQ" in result["hands"]
        assert "KK" in result["hands"]
        assert "AA" in result["hands"]
        assert len(result["hands"]) == 3
        assert result["combos"]["pairs"] == 18  # 3 pairs * 6 combos

    def test_parse_suited_plus(self, parser):
        """Should expand suited plus notation (ATs+ -> ATs, AJs, AQs, AKs)."""
        result = parser.parse("ATs+")
        assert "ATs" in result["hands"]
        assert "AJs" in result["hands"]
        assert "AQs" in result["hands"]
        assert "AKs" in result["hands"]
        assert len(result["hands"]) == 4
        assert result["combos"]["suited"] == 16  # 4 hands * 4 combos

    def test_parse_offsuit_plus(self, parser):
        """Should expand offsuit plus notation."""
        result = parser.parse("ATo+")
        assert "ATo" in result["hands"]
        assert "AJo" in result["hands"]
        assert "AQo" in result["hands"]
        assert "AKo" in result["hands"]
        assert len(result["hands"]) == 4
        assert result["combos"]["offsuit"] == 48  # 4 hands * 12 combos

    def test_parse_low_pair_plus(self, parser):
        """Should expand 22+ to all pairs."""
        result = parser.parse("22+")
        assert len(result["hands"]) == 13  # All 13 pairs
        assert "22" in result["hands"]
        assert "AA" in result["hands"]
        assert result["combos"]["pairs"] == 78  # 13 * 6

    # Range notation tests
    def test_parse_pair_range(self, parser):
        """Should expand pair range notation (QQ-88)."""
        result = parser.parse("QQ-88")
        assert "QQ" in result["hands"]
        assert "JJ" in result["hands"]
        assert "TT" in result["hands"]
        assert "99" in result["hands"]
        assert "88" in result["hands"]
        assert len(result["hands"]) == 5
        assert "KK" not in result["hands"]
        assert "77" not in result["hands"]

    def test_parse_suited_range(self, parser):
        """Should expand suited range notation (A5s-A2s)."""
        result = parser.parse("A5s-A2s")
        assert "A5s" in result["hands"]
        assert "A4s" in result["hands"]
        assert "A3s" in result["hands"]
        assert "A2s" in result["hands"]
        assert len(result["hands"]) == 4
        assert "A6s" not in result["hands"]

    def test_parse_offsuit_range(self, parser):
        """Should expand offsuit range notation."""
        result = parser.parse("KTo-K8o")
        assert "KTo" in result["hands"]
        assert "K9o" in result["hands"]
        assert "K8o" in result["hands"]
        assert len(result["hands"]) == 3

    # Complex notation tests
    def test_parse_complex_notation(self, parser):
        """Should parse complex combined notation."""
        result = parser.parse("77+, ATs+, AKo")
        # Check pairs
        assert "77" in result["hands"]
        assert "88" in result["hands"]
        assert "AA" in result["hands"]
        # Check suited
        assert "ATs" in result["hands"]
        assert "AKs" in result["hands"]
        # Check offsuit
        assert "AKo" in result["hands"]

    def test_parse_with_whitespace(self, parser):
        """Should handle extra whitespace."""
        result = parser.parse("  AA  ,  KK  ,  QQ  ")
        assert "AA" in result["hands"]
        assert "KK" in result["hands"]
        assert "QQ" in result["hands"]

    def test_parse_case_insensitive(self, parser):
        """Should handle lowercase notation."""
        result = parser.parse("aa, aks, ako")
        assert "AA" in result["hands"]
        assert "AKs" in result["hands"]
        assert "AKo" in result["hands"]

    # Combo counting tests
    def test_combo_counts_mixed(self, parser):
        """Should correctly count combos for mixed range."""
        result = parser.parse("AA, AKs, AKo")
        assert result["combos"]["pairs"] == 6
        assert result["combos"]["suited"] == 4
        assert result["combos"]["offsuit"] == 12
        assert result["total_combos"] == 22

    def test_percentage_calculation(self, parser):
        """Should calculate correct percentage of total hands."""
        # AA alone = 6/1326 = 0.45%
        result = parser.parse("AA")
        assert result["percentage"] == pytest.approx(0.5, abs=0.1)

        # All pairs = 78/1326 = 5.88%
        result = parser.parse("22+")
        assert result["percentage"] == pytest.approx(5.9, abs=0.1)

    # Empty/edge cases
    def test_parse_empty_string(self, parser):
        """Should handle empty string."""
        result = parser.parse("")
        assert result["hands"] == []
        assert result["total_combos"] == 0
        assert result["percentage"] == 0.0

    def test_parse_whitespace_only(self, parser):
        """Should handle whitespace-only string."""
        result = parser.parse("   ")
        assert result["hands"] == []
        assert result["total_combos"] == 0

    # Error handling tests
    def test_invalid_rank_raises_error(self, parser):
        """Should raise error for invalid rank."""
        with pytest.raises(ValueError):
            parser.parse("XX+")

    def test_invalid_range_notation(self, parser):
        """Should raise error for invalid range notation."""
        with pytest.raises(ValueError):
            parser.parse("AA-KK-QQ")  # Too many parts

    def test_mismatched_range_types(self, parser):
        """Should raise error for mismatched range types."""
        with pytest.raises(ValueError):
            parser.parse("AKs-JTo")  # Different suit types

    # Sorting tests
    def test_hands_sorted_correctly(self, parser):
        """Should return hands sorted by strength (pairs first, then suited/offsuit)."""
        result = parser.parse("22, AKs, AA")
        # Pairs come first (AA, then 22), then suited (AKs)
        assert result["hands"][0] == "AA"
        assert result["hands"][1] == "22"
        assert result["hands"][2] == "AKs"


class TestRankConstants:
    """Tests for rank constants."""

    def test_ranks_order(self):
        """Ranks should be in correct order (A high to 2 low)."""
        assert RANKS[0] == "A"
        assert RANKS[-1] == "2"
        assert len(RANKS) == 13

    def test_rank_values(self):
        """Rank values should map correctly."""
        assert RANK_VALUES["A"] == 0
        assert RANK_VALUES["K"] == 1
        assert RANK_VALUES["2"] == 12
