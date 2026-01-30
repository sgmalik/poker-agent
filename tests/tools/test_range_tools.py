"""Tests for range LangChain tools."""

from src.tools.range_tools import (
    get_gto_range,
    list_available_ranges,
    parse_range,
    check_hand_in_range,
)


class TestGetGtoRange:
    """Tests for the get_gto_range tool."""

    def test_btn_open_range(self):
        """Test getting BTN opening range."""
        result = get_gto_range.invoke({"position": "BTN", "action": "open"})
        assert result["success"] is True
        assert result["position"] == "BTN"
        assert result["action"] == "open"
        assert len(result["hands"]) > 0
        assert result["percentage"] > 25  # BTN opens wide

    def test_utg_open_range(self):
        """Test getting UTG opening range."""
        result = get_gto_range.invoke({"position": "UTG", "action": "open"})
        assert result["success"] is True
        assert result["position"] == "UTG"
        assert result["percentage"] < 20  # UTG opens tight

    def test_position_case_insensitive(self):
        """Test that position is case-insensitive."""
        result = get_gto_range.invoke({"position": "btn", "action": "open"})
        assert result["success"] is True
        assert result["position"] == "BTN"

    def test_invalid_position(self):
        """Test error for invalid position."""
        result = get_gto_range.invoke({"position": "INVALID", "action": "open"})
        assert result["success"] is False
        assert "error" in result

    def test_invalid_action(self):
        """Test error for invalid action."""
        result = get_gto_range.invoke({"position": "BTN", "action": "invalid_action"})
        assert result["success"] is False
        assert "error" in result


class TestListAvailableRanges:
    """Tests for the list_available_ranges tool."""

    def test_list_ranges(self):
        """Test listing available ranges."""
        result = list_available_ranges.invoke({})
        assert result["success"] is True
        assert "positions" in result
        # Should have common positions
        assert "BTN" in result["positions"]
        assert "UTG" in result["positions"]
        assert "BB" in result["positions"]

    def test_positions_have_actions(self):
        """Test that positions have action lists."""
        result = list_available_ranges.invoke({})
        assert result["success"] is True
        # BTN should have open action
        assert "open" in result["positions"]["BTN"]


class TestParseRange:
    """Tests for the parse_range tool."""

    def test_parse_premium_range(self):
        """Test parsing a premium range."""
        result = parse_range.invoke({"range_notation": "AA, KK, QQ"})
        assert result["success"] is True
        assert "AA" in result["hands"]
        assert "KK" in result["hands"]
        assert "QQ" in result["hands"]
        assert len(result["hands"]) == 3
        # 3 pairs x 6 combos = 18 combos
        assert result["total_combos"] == 18

    def test_parse_plus_notation(self):
        """Test parsing plus notation."""
        result = parse_range.invoke({"range_notation": "QQ+"})
        assert result["success"] is True
        assert "AA" in result["hands"]
        assert "KK" in result["hands"]
        assert "QQ" in result["hands"]
        assert "JJ" not in result["hands"]

    def test_parse_suited_range(self):
        """Test parsing suited hands."""
        result = parse_range.invoke({"range_notation": "ATs+"})
        assert result["success"] is True
        assert "AKs" in result["hands"]
        assert "AQs" in result["hands"]
        assert "AJs" in result["hands"]
        assert "ATs" in result["hands"]
        assert "A9s" not in result["hands"]

    def test_parse_mixed_range(self):
        """Test parsing a mixed range."""
        result = parse_range.invoke({"range_notation": "QQ+, AKs, ATs+"})
        assert result["success"] is True
        assert "AA" in result["hands"]
        assert "AKs" in result["hands"]
        assert "ATs" in result["hands"]
        assert result["percentage"] > 0

    def test_parse_range_percentage(self):
        """Test that percentage is calculated correctly."""
        result = parse_range.invoke({"range_notation": "AA"})
        assert result["success"] is True
        # AA = 6 combos out of 1326 total = 0.45%
        assert 0.4 <= result["percentage"] <= 0.5

    def test_parse_empty_range(self):
        """Test parsing empty range."""
        result = parse_range.invoke({"range_notation": ""})
        assert result["success"] is True
        assert len(result["hands"]) == 0
        assert result["total_combos"] == 0


class TestCheckHandInRange:
    """Tests for the check_hand_in_range tool."""

    def test_hand_in_range(self):
        """Test checking a hand that's in range."""
        result = check_hand_in_range.invoke(
            {"hand": "AA", "position": "BTN", "action": "open"}
        )
        assert result["success"] is True
        assert result["in_range"] is True

    def test_hand_not_in_range(self):
        """Test checking a hand that's not in range."""
        # 72o should never be in UTG open range
        result = check_hand_in_range.invoke(
            {"hand": "72o", "position": "UTG", "action": "open"}
        )
        assert result["success"] is True
        assert result["in_range"] is False

    def test_hand_case_insensitive(self):
        """Test that hand is case-insensitive."""
        result = check_hand_in_range.invoke(
            {"hand": "aks", "position": "BTN", "action": "open"}
        )
        assert result["success"] is True
        assert result["hand"] == "AKS"

    def test_invalid_position(self):
        """Test error for invalid position."""
        result = check_hand_in_range.invoke(
            {"hand": "AA", "position": "INVALID", "action": "open"}
        )
        assert result["success"] is False
        assert "error" in result
