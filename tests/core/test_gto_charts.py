"""Tests for GTO charts and range queries."""

import pytest
from src.core.gto_charts import GTOCharts, get_gto_range, get_range_matrix


class TestGTOCharts:
    """Tests for GTOCharts class."""

    @pytest.fixture
    def charts(self):
        """Create GTOCharts instance for tests."""
        return GTOCharts()

    # Position tests
    def test_get_positions(self, charts):
        """Should return list of positions."""
        positions = charts.get_positions()
        assert isinstance(positions, list)
        assert len(positions) >= 5
        assert "UTG" in positions
        assert "BTN" in positions
        assert "BB" in positions

    def test_get_positions_9_handed(self, charts):
        """Should have 9-handed positions."""
        positions = charts.get_positions()
        expected = ["UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
        assert len(positions) == 9
        for pos in expected:
            assert pos in positions

    # Action tests
    def test_get_actions_for_utg(self, charts):
        """Should return actions for UTG."""
        actions = charts.get_actions("UTG")
        assert "open" in actions

    def test_get_actions_for_bb(self, charts):
        """BB should have call and 3bet actions."""
        actions = charts.get_actions("BB")
        assert "call_vs_BTN" in actions
        assert "3bet_vs_BTN" in actions

    def test_get_actions_invalid_position(self, charts):
        """Should return empty list for invalid position."""
        actions = charts.get_actions("INVALID")
        assert actions == []

    # Range query tests
    def test_get_range_utg_open(self, charts):
        """Should get UTG open range."""
        range_data = charts.get_range("UTG", "open")
        assert range_data is not None
        assert "hands" in range_data
        assert "notation" in range_data
        assert "total_combos" in range_data
        assert "percentage" in range_data

    def test_get_range_btn_open(self, charts):
        """BTN should have wider range than UTG."""
        utg_range = charts.get_range("UTG", "open")
        btn_range = charts.get_range("BTN", "open")
        assert btn_range["total_combos"] > utg_range["total_combos"]
        assert btn_range["percentage"] > utg_range["percentage"]

    def test_get_range_invalid_position(self, charts):
        """Should return None for invalid position."""
        range_data = charts.get_range("INVALID", "open")
        assert range_data is None

    def test_get_range_invalid_action(self, charts):
        """Should return None for invalid action."""
        range_data = charts.get_range("UTG", "INVALID")
        assert range_data is None

    # Hand in range tests
    def test_is_hand_in_range_premium(self, charts):
        """Premium hands should be in UTG range."""
        assert charts.is_hand_in_range("AA", "UTG", "open") is True
        assert charts.is_hand_in_range("KK", "UTG", "open") is True
        assert charts.is_hand_in_range("AKs", "UTG", "open") is True

    def test_is_hand_in_range_weak(self, charts):
        """Weak hands should not be in UTG range."""
        assert charts.is_hand_in_range("72o", "UTG", "open") is False
        assert charts.is_hand_in_range("32s", "UTG", "open") is False

    def test_is_hand_in_range_case_insensitive(self, charts):
        """Hand lookup should be case insensitive."""
        assert charts.is_hand_in_range("aa", "UTG", "open") is True
        assert charts.is_hand_in_range("aks", "UTG", "open") is True

    # Matrix tests
    def test_hands_to_matrix_dimensions(self, charts):
        """Matrix should be 13x13."""
        matrix = charts.hands_to_matrix(["AA", "KK"])
        assert len(matrix) == 13
        assert all(len(row) == 13 for row in matrix)

    def test_hands_to_matrix_pairs(self, charts):
        """Pairs should be on diagonal."""
        matrix = charts.hands_to_matrix(["AA", "KK", "QQ"])
        # AA at [0][0], KK at [1][1], QQ at [2][2]
        assert matrix[0][0] is True  # AA
        assert matrix[1][1] is True  # KK
        assert matrix[2][2] is True  # QQ
        assert matrix[3][3] is False  # JJ not included

    def test_hands_to_matrix_suited(self, charts):
        """Suited hands should be above diagonal."""
        matrix = charts.hands_to_matrix(["AKs", "AQs"])
        # AKs: A=0, K=1, suited -> row 0, col 1
        assert matrix[0][1] is True
        # AQs: A=0, Q=2, suited -> row 0, col 2
        assert matrix[0][2] is True

    def test_hands_to_matrix_offsuit(self, charts):
        """Offsuit hands should be below diagonal."""
        matrix = charts.hands_to_matrix(["AKo", "AQo"])
        # AKo: A=0, K=1, offsuit -> row 1, col 0
        assert matrix[1][0] is True
        # AQo: A=0, Q=2, offsuit -> row 2, col 0
        assert matrix[2][0] is True

    def test_hands_to_matrix_empty(self, charts):
        """Empty hand list should give all-false matrix."""
        matrix = charts.hands_to_matrix([])
        assert all(cell is False for row in matrix for cell in row)

    # Matrix hand lookup tests
    def test_get_matrix_hand_pair(self, charts):
        """Should return pair for diagonal."""
        assert charts.get_matrix_hand(0, 0) == "AA"
        assert charts.get_matrix_hand(1, 1) == "KK"
        assert charts.get_matrix_hand(12, 12) == "22"

    def test_get_matrix_hand_suited(self, charts):
        """Should return suited hand for above diagonal."""
        assert charts.get_matrix_hand(0, 1) == "AKs"
        assert charts.get_matrix_hand(0, 2) == "AQs"

    def test_get_matrix_hand_offsuit(self, charts):
        """Should return offsuit hand for below diagonal."""
        assert charts.get_matrix_hand(1, 0) == "AKo"
        assert charts.get_matrix_hand(2, 0) == "AQo"

    def test_get_matrix_hand_invalid(self, charts):
        """Should return empty string for invalid indices."""
        assert charts.get_matrix_hand(-1, 0) == ""
        assert charts.get_matrix_hand(13, 0) == ""

    # Combo count tests
    def test_get_combo_count_pair(self, charts):
        """Pairs should have 6 combos."""
        assert charts.get_combo_count(0, 0) == 6
        assert charts.get_combo_count(5, 5) == 6

    def test_get_combo_count_suited(self, charts):
        """Suited should have 4 combos."""
        assert charts.get_combo_count(0, 1) == 4
        assert charts.get_combo_count(0, 5) == 4

    def test_get_combo_count_offsuit(self, charts):
        """Offsuit should have 12 combos."""
        assert charts.get_combo_count(1, 0) == 12
        assert charts.get_combo_count(5, 0) == 12

    # Custom range parsing tests
    def test_parse_custom_range(self, charts):
        """Should parse custom range notation."""
        result = charts.parse_custom_range("AA, KK, QQ")
        assert "AA" in result["hands"]
        assert "KK" in result["hands"]
        assert "QQ" in result["hands"]
        assert result["total_combos"] == 18

    def test_parse_custom_range_with_plus(self, charts):
        """Should handle plus notation in custom range."""
        result = charts.parse_custom_range("QQ+")
        assert "QQ" in result["hands"]
        assert "KK" in result["hands"]
        assert "AA" in result["hands"]


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_gto_range(self):
        """Test get_gto_range convenience function."""
        result = get_gto_range("BTN", "open")
        assert result is not None
        assert "hands" in result

    def test_get_gto_range_invalid(self):
        """Should return None for invalid query."""
        result = get_gto_range("INVALID", "open")
        assert result is None

    def test_get_range_matrix(self):
        """Test get_range_matrix convenience function."""
        matrix = get_range_matrix("UTG", "open")
        assert matrix is not None
        assert len(matrix) == 13
        assert len(matrix[0]) == 13
        # UTG should have AA
        assert matrix[0][0] is True

    def test_get_range_matrix_invalid(self):
        """Should return None for invalid query."""
        matrix = get_range_matrix("INVALID", "open")
        assert matrix is None


class TestRangeRealism:
    """Tests to verify GTO ranges are realistic."""

    @pytest.fixture
    def charts(self):
        """Create GTOCharts instance for tests."""
        return GTOCharts()

    def test_utg_is_tightest(self, charts):
        """UTG should have tightest open range."""
        utg = charts.get_range("UTG", "open")
        btn = charts.get_range("BTN", "open")
        assert utg["percentage"] < btn["percentage"]

    def test_btn_has_many_combos(self, charts):
        """BTN should have 25-35% opening range."""
        btn = charts.get_range("BTN", "open")
        assert 20 <= btn["percentage"] <= 40

    def test_utg_has_premium_only(self, charts):
        """UTG should only have premium hands."""
        utg = charts.get_range("UTG", "open")
        # Should have premiums
        assert "AA" in utg["hands"]
        assert "KK" in utg["hands"]
        # Should NOT have weak hands
        assert "72o" not in utg["hands"]
        assert "32s" not in utg["hands"]

    def test_bb_has_wider_defense_range(self, charts):
        """BB should defend wider than UTG opens."""
        utg = charts.get_range("UTG", "open")
        bb_call = charts.get_range("BB", "call_vs_BTN")
        assert bb_call["percentage"] > utg["percentage"]
