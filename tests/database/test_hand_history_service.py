"""Tests for hand history service functions."""

import json
import pytest

from src.database.db import init_db, SessionLocal
from src.database.models import HandHistory
from src.database.service import (
    save_hand_history,
    get_hand_histories,
    get_hand_history_by_id,
    update_hand_history,
    delete_hand_history,
    get_hand_history_stats,
    get_all_tags,
    export_hand_histories,
    import_hand_histories,
)

# Use a dedicated user_id for tests to avoid affecting real user data
TEST_USER_ID = 99998


@pytest.fixture(autouse=True)
def setup_and_cleanup_db():
    """Ensure database tables exist and clean up test data after each test."""
    init_db()
    yield
    # Clean up only test user's hand histories after each test
    db = SessionLocal()
    try:
        db.query(HandHistory).filter(HandHistory.user_id == TEST_USER_ID).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def sample_hand():
    """Create a sample hand history data dict."""
    return {
        "hero_hand": "As Kh",
        "board": "Qh Jh 2c",
        "position": "BTN",
        "action_summary": "Raised pre, c-bet flop",
        "result": "won",
        "stake_level": "1/2",
        "pot_size": 150.0,
        "tags": ["value", "c-bet"],
        "notes": "Opponent folded to c-bet",
        "hand_text": "Hero opens BTN with AKo, BB calls. Flop QJ2r, Hero c-bets...",
    }


class TestSaveHandHistory:
    """Tests for save_hand_history function."""

    def test_save_basic_hand(self, sample_hand):
        """Should save a hand with all fields."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)
        assert hand_id > 0

    def test_save_minimal_hand(self):
        """Should save with only required fields."""
        hand_data = {
            "hero_hand": "Ah Ad",
            "position": "UTG",
            "result": "won",
        }
        hand_id = save_hand_history(hand_data, user_id=TEST_USER_ID)
        assert hand_id > 0

    def test_save_converts_tag_list(self, sample_hand):
        """Should convert tag list to comma-separated string."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)
        hand = get_hand_history_by_id(hand_id, user_id=TEST_USER_ID)
        assert "value" in hand["tags"]
        assert "c-bet" in hand["tags"]

    def test_save_without_board(self):
        """Should save preflop hand without board."""
        hand_data = {
            "hero_hand": "Ks Qs",
            "position": "CO",
            "result": "won",
            "action_summary": "Raised pre, everyone folded",
        }
        hand_id = save_hand_history(hand_data, user_id=TEST_USER_ID)
        assert hand_id > 0

        hand = get_hand_history_by_id(hand_id, user_id=TEST_USER_ID)
        assert hand["street"] == "preflop"


class TestGetHandHistories:
    """Tests for get_hand_histories function."""

    def test_get_empty_histories(self):
        """Should return empty list when no hands."""
        hands = get_hand_histories(user_id=TEST_USER_ID)
        assert hands == []

    def test_get_histories_returns_all_fields(self, sample_hand):
        """Should return hands with all fields."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)
        hands = get_hand_histories(user_id=TEST_USER_ID)

        assert len(hands) == 1
        hand = hands[0]
        assert "id" in hand
        assert "hero_hand" in hand
        assert "board" in hand
        assert "position" in hand
        assert "result" in hand
        assert "tags" in hand
        assert "street" in hand
        assert "created_at" in hand

    def test_get_histories_filter_by_result(self, sample_hand):
        """Should filter hands by result."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)  # won

        losing_hand = sample_hand.copy()
        losing_hand["result"] = "lost"
        save_hand_history(losing_hand, user_id=TEST_USER_ID)

        hands = get_hand_histories(result="won", user_id=TEST_USER_ID)
        assert len(hands) == 1
        assert hands[0]["result"] == "won"

    def test_get_histories_filter_by_position(self, sample_hand):
        """Should filter hands by position."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)  # BTN

        bb_hand = sample_hand.copy()
        bb_hand["position"] = "BB"
        save_hand_history(bb_hand, user_id=TEST_USER_ID)

        hands = get_hand_histories(position="BTN", user_id=TEST_USER_ID)
        assert len(hands) == 1
        assert hands[0]["position"] == "BTN"

    def test_get_histories_filter_by_tags(self, sample_hand):
        """Should filter hands by tags."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)  # value, c-bet

        bluff_hand = sample_hand.copy()
        bluff_hand["tags"] = ["bluff"]
        save_hand_history(bluff_hand, user_id=TEST_USER_ID)

        hands = get_hand_histories(tags=["bluff"], user_id=TEST_USER_ID)
        assert len(hands) == 1
        assert "bluff" in hands[0]["tags"]

    def test_get_histories_determines_street(self, sample_hand):
        """Should determine street based on board cards."""
        # Flop (3 cards)
        save_hand_history(sample_hand, user_id=TEST_USER_ID)

        # Turn (4 cards)
        turn_hand = sample_hand.copy()
        turn_hand["board"] = "Qh Jh 2c 5d"
        save_hand_history(turn_hand, user_id=TEST_USER_ID)

        # River (5 cards)
        river_hand = sample_hand.copy()
        river_hand["board"] = "Qh Jh 2c 5d 9s"
        save_hand_history(river_hand, user_id=TEST_USER_ID)

        hands = get_hand_histories(user_id=TEST_USER_ID)
        streets = {h["street"] for h in hands}
        assert "flop" in streets
        assert "turn" in streets
        assert "river" in streets


class TestGetHandHistoryById:
    """Tests for get_hand_history_by_id function."""

    def test_get_existing_hand(self, sample_hand):
        """Should return hand by ID."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)
        hand = get_hand_history_by_id(hand_id, user_id=TEST_USER_ID)

        assert hand is not None
        assert hand["id"] == hand_id
        assert hand["hero_hand"] == sample_hand["hero_hand"]

    def test_get_nonexistent_hand(self):
        """Should return None for non-existent hand."""
        hand = get_hand_history_by_id(99999, user_id=TEST_USER_ID)
        assert hand is None

    def test_get_wrong_user(self, sample_hand):
        """Should not return hand belonging to different user."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)
        hand = get_hand_history_by_id(hand_id, user_id=TEST_USER_ID + 1)
        assert hand is None


class TestUpdateHandHistory:
    """Tests for update_hand_history function."""

    def test_update_hand_fields(self, sample_hand):
        """Should update allowed fields."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)

        updates = {
            "notes": "Updated notes",
            "result": "lost",
        }
        result = update_hand_history(hand_id, updates, user_id=TEST_USER_ID)

        assert result is True
        hand = get_hand_history_by_id(hand_id, user_id=TEST_USER_ID)
        assert hand["notes"] == "Updated notes"
        assert hand["result"] == "lost"

    def test_update_tags(self, sample_hand):
        """Should update tags correctly."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)

        updates = {"tags": ["bluff", "hero_call"]}
        update_hand_history(hand_id, updates, user_id=TEST_USER_ID)

        hand = get_hand_history_by_id(hand_id, user_id=TEST_USER_ID)
        assert "bluff" in hand["tags"]
        assert "hero_call" in hand["tags"]

    def test_update_nonexistent_hand(self):
        """Should return False for non-existent hand."""
        result = update_hand_history(99999, {"notes": "test"}, user_id=TEST_USER_ID)
        assert result is False


class TestDeleteHandHistory:
    """Tests for delete_hand_history function."""

    def test_delete_existing_hand(self, sample_hand):
        """Should delete an existing hand."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)
        result = delete_hand_history(hand_id, user_id=TEST_USER_ID)

        assert result is True
        hands = get_hand_histories(user_id=TEST_USER_ID)
        assert len(hands) == 0

    def test_delete_nonexistent_hand(self):
        """Should return False for non-existent hand."""
        result = delete_hand_history(99999, user_id=TEST_USER_ID)
        assert result is False

    def test_delete_wrong_user(self, sample_hand):
        """Should not delete hand belonging to different user."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)
        result = delete_hand_history(hand_id, user_id=TEST_USER_ID + 1)
        assert result is False


class TestGetHandHistoryStats:
    """Tests for get_hand_history_stats function."""

    def test_stats_empty_hands(self):
        """Should return zeros when no hands."""
        stats = get_hand_history_stats(user_id=TEST_USER_ID)
        assert stats["total_hands"] == 0
        assert stats["wins"] == 0
        assert stats["win_rate"] == 0.0

    def test_stats_calculates_totals(self, sample_hand):
        """Should calculate total stats correctly."""
        # Win
        save_hand_history(sample_hand, user_id=TEST_USER_ID)

        # Loss
        losing_hand = sample_hand.copy()
        losing_hand["result"] = "lost"
        save_hand_history(losing_hand, user_id=TEST_USER_ID)

        # Split
        split_hand = sample_hand.copy()
        split_hand["result"] = "split"
        save_hand_history(split_hand, user_id=TEST_USER_ID)

        stats = get_hand_history_stats(user_id=TEST_USER_ID)
        assert stats["total_hands"] == 3
        assert stats["wins"] == 1
        assert stats["losses"] == 1
        assert stats["splits"] == 1
        assert stats["win_rate"] == pytest.approx(33.33, rel=0.1)

    def test_stats_by_position(self, sample_hand):
        """Should break down stats by position."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)  # BTN, won

        bb_hand = sample_hand.copy()
        bb_hand["position"] = "BB"
        bb_hand["result"] = "lost"
        save_hand_history(bb_hand, user_id=TEST_USER_ID)

        stats = get_hand_history_stats(user_id=TEST_USER_ID)
        by_position = stats["by_position"]

        assert "BTN" in by_position
        assert by_position["BTN"]["won"] == 1
        assert "BB" in by_position
        assert by_position["BB"]["lost"] == 1

    def test_stats_by_tag(self, sample_hand):
        """Should break down stats by tag."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)  # value, c-bet, won

        bluff_hand = sample_hand.copy()
        bluff_hand["tags"] = ["bluff"]
        bluff_hand["result"] = "lost"
        save_hand_history(bluff_hand, user_id=TEST_USER_ID)

        stats = get_hand_history_stats(user_id=TEST_USER_ID)
        by_tag = stats["by_tag"]

        assert "value" in by_tag
        assert by_tag["value"]["won"] == 1
        assert "bluff" in by_tag
        assert by_tag["bluff"]["lost"] == 1


class TestGetAllTags:
    """Tests for get_all_tags function."""

    def test_get_empty_tags(self):
        """Should return empty list when no hands."""
        tags = get_all_tags(user_id=TEST_USER_ID)
        assert tags == []

    def test_get_unique_tags(self, sample_hand):
        """Should return unique tags."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)  # value, c-bet

        bluff_hand = sample_hand.copy()
        bluff_hand["tags"] = ["bluff", "value"]  # value is duplicate
        save_hand_history(bluff_hand, user_id=TEST_USER_ID)

        tags = get_all_tags(user_id=TEST_USER_ID)
        assert "value" in tags
        assert "c-bet" in tags
        assert "bluff" in tags
        assert len([t for t in tags if t == "value"]) == 1  # No duplicates


class TestExportImport:
    """Tests for export/import functions."""

    def test_export_json(self, sample_hand):
        """Should export hands as JSON."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)
        exported = export_hand_histories(user_id=TEST_USER_ID, format="json")

        data = json.loads(exported)
        assert len(data) == 1
        assert data[0]["hero_hand"] == sample_hand["hero_hand"]

    def test_export_csv(self, sample_hand):
        """Should export hands as CSV."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)
        exported = export_hand_histories(user_id=TEST_USER_ID, format="csv")

        lines = exported.strip().split("\n")
        assert len(lines) == 2  # Header + 1 row
        assert "hero_hand" in lines[0]  # Header contains field names

    def test_import_json(self):
        """Should import hands from JSON."""
        data = json.dumps(
            [
                {
                    "hero_hand": "Kc Qc",
                    "position": "CO",
                    "result": "won",
                }
            ]
        )
        count = import_hand_histories(data, format="json", user_id=TEST_USER_ID)

        assert count == 1
        hands = get_hand_histories(user_id=TEST_USER_ID)
        assert len(hands) == 1
        assert hands[0]["hero_hand"] == "Kc Qc"

    def test_import_csv(self):
        """Should import hands from CSV."""
        csv_data = """hero_hand,position,result,tags
Jd Td,BTN,won,"bluff, semi-bluff"
"""
        count = import_hand_histories(csv_data, format="csv", user_id=TEST_USER_ID)

        assert count == 1
        hands = get_hand_histories(user_id=TEST_USER_ID)
        assert len(hands) == 1
        assert hands[0]["hero_hand"] == "Jd Td"
        assert "bluff" in hands[0]["tags"]

    def test_round_trip_json(self, sample_hand):
        """Should export and import JSON without data loss."""
        save_hand_history(sample_hand, user_id=TEST_USER_ID)
        exported = export_hand_histories(user_id=TEST_USER_ID, format="json")

        # Clean up and reimport
        db = SessionLocal()
        db.query(HandHistory).filter(HandHistory.user_id == TEST_USER_ID).delete()
        db.commit()
        db.close()

        import_hand_histories(exported, format="json", user_id=TEST_USER_ID)
        hands = get_hand_histories(user_id=TEST_USER_ID)

        assert len(hands) == 1
        assert hands[0]["hero_hand"] == sample_hand["hero_hand"]
        assert hands[0]["position"] == sample_hand["position"]


class TestHandHistoryModel:
    """Tests for HandHistory model properties."""

    def test_tag_list_property(self, sample_hand):
        """Should parse tags correctly."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            hand = db.query(HandHistory).filter(HandHistory.id == hand_id).first()
            assert "value" in hand.tag_list
            assert "c-bet" in hand.tag_list
        finally:
            db.close()

    def test_tag_list_empty(self):
        """Should return empty list for no tags."""
        hand_data = {
            "hero_hand": "Ah Ad",
            "position": "UTG",
            "result": "won",
        }
        hand_id = save_hand_history(hand_data, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            hand = db.query(HandHistory).filter(HandHistory.id == hand_id).first()
            assert hand.tag_list == []
        finally:
            db.close()

    def test_street_property_flop(self, sample_hand):
        """Should detect flop street."""
        hand_id = save_hand_history(sample_hand, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            hand = db.query(HandHistory).filter(HandHistory.id == hand_id).first()
            assert hand.street == "flop"
        finally:
            db.close()

    def test_street_property_preflop(self):
        """Should detect preflop street."""
        hand_data = {
            "hero_hand": "Ah Ad",
            "position": "UTG",
            "result": "won",
        }
        hand_id = save_hand_history(hand_data, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            hand = db.query(HandHistory).filter(HandHistory.id == hand_id).first()
            assert hand.street == "preflop"
        finally:
            db.close()
