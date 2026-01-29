"""Tests for poker session service functions."""

import pytest
from datetime import datetime, timedelta, timezone

from src.database.db import init_db, SessionLocal
from src.database.models import PokerSession
from src.database.service import (
    save_poker_session,
    get_poker_sessions,
    get_session_stats,
    get_bankroll_data,
    delete_poker_session,
    update_poker_session,
)

# Use a dedicated user_id for tests to avoid affecting real user data
TEST_USER_ID = 99999


@pytest.fixture(autouse=True)
def setup_and_cleanup_db():
    """Ensure database tables exist and clean up test data after each test."""
    init_db()
    yield
    # Clean up only test user's sessions after each test
    db = SessionLocal()
    try:
        db.query(PokerSession).filter(PokerSession.user_id == TEST_USER_ID).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def sample_session():
    """Create a sample session data dict."""
    return {
        "date": datetime.now(timezone.utc),
        "stake_level": "1/2",
        "buy_in": 200.0,
        "cash_out": 350.0,
        "duration_minutes": 180,
        "hands_played": 250,
        "location": "Test Casino",
        "game_type": "cash",
        "notes": "Test session",
    }


class TestSavePokerSession:
    """Tests for save_poker_session function."""

    def test_save_basic_session(self, sample_session):
        """Should save a session with all fields."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)
        assert session_id > 0

    def test_save_calculates_profit(self, sample_session):
        """Should automatically calculate profit/loss."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)
        assert session_id

        sessions = get_poker_sessions(days=0, user_id=TEST_USER_ID)
        assert len(sessions) == 1
        assert sessions[0]["profit_loss"] == 150.0  # 350 - 200

    def test_save_session_with_loss(self):
        """Should handle negative profit correctly."""
        session_data = {
            "date": datetime.now(timezone.utc),
            "stake_level": "1/2",
            "buy_in": 200.0,
            "cash_out": 50.0,
        }
        session_id = save_poker_session(session_data, user_id=TEST_USER_ID)
        assert session_id

        sessions = get_poker_sessions(days=0, user_id=TEST_USER_ID)
        assert sessions[0]["profit_loss"] == -150.0

    def test_save_session_minimal_fields(self):
        """Should save with only required fields."""
        session_data = {
            "stake_level": "2/5",
            "buy_in": 500.0,
            "cash_out": 600.0,
        }
        session_id = save_poker_session(session_data, user_id=TEST_USER_ID)
        assert session_id > 0

    def test_save_session_with_string_date(self):
        """Should parse date from ISO string."""
        session_data = {
            "date": "2025-01-15T10:00:00+00:00",
            "stake_level": "1/2",
            "buy_in": 100.0,
            "cash_out": 200.0,
        }
        session_id = save_poker_session(session_data, user_id=TEST_USER_ID)
        assert session_id > 0


class TestGetPokerSessions:
    """Tests for get_poker_sessions function."""

    def test_get_empty_sessions(self):
        """Should return empty list when no sessions."""
        sessions = get_poker_sessions(days=30, user_id=TEST_USER_ID)
        assert sessions == []

    def test_get_sessions_returns_all_fields(self, sample_session):
        """Should return sessions with all fields."""
        save_poker_session(sample_session, user_id=TEST_USER_ID)
        sessions = get_poker_sessions(days=30, user_id=TEST_USER_ID)

        assert len(sessions) == 1
        session = sessions[0]
        assert "id" in session
        assert "date" in session
        assert "stake_level" in session
        assert "buy_in" in session
        assert "cash_out" in session
        assert "profit_loss" in session
        assert "duration_minutes" in session
        assert "hourly_rate" in session

    def test_get_sessions_filter_by_days(self, sample_session):
        """Should filter sessions by days."""
        # Save current session
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        # Save old session (35 days ago)
        old_session = sample_session.copy()
        old_session["date"] = datetime.now(timezone.utc) - timedelta(days=35)
        save_poker_session(old_session, user_id=TEST_USER_ID)

        # Should get only recent session
        sessions = get_poker_sessions(days=30, user_id=TEST_USER_ID)
        assert len(sessions) == 1

        # Should get all sessions with days=0
        sessions = get_poker_sessions(days=0, user_id=TEST_USER_ID)
        assert len(sessions) == 2

    def test_get_sessions_filter_by_stake(self, sample_session):
        """Should filter sessions by stake level."""
        save_poker_session(sample_session, user_id=TEST_USER_ID)  # 1/2

        other_session = sample_session.copy()
        other_session["stake_level"] = "2/5"
        save_poker_session(other_session, user_id=TEST_USER_ID)

        sessions = get_poker_sessions(stake_level="1/2", user_id=TEST_USER_ID)
        assert len(sessions) == 1
        assert sessions[0]["stake_level"] == "1/2"

    def test_get_sessions_calculates_hourly_rate(self, sample_session):
        """Should calculate hourly rate correctly."""
        save_poker_session(sample_session, user_id=TEST_USER_ID)
        sessions = get_poker_sessions(days=30, user_id=TEST_USER_ID)

        # Profit: 150, Duration: 180 min = 3 hours, Hourly: 50
        assert sessions[0]["hourly_rate"] == pytest.approx(50.0, rel=0.01)


class TestGetSessionStats:
    """Tests for get_session_stats function."""

    def test_stats_empty_sessions(self):
        """Should return zeros when no sessions."""
        stats = get_session_stats(days=30, user_id=TEST_USER_ID)
        assert stats["total_sessions"] == 0
        assert stats["total_profit"] == 0.0
        assert stats["hourly_rate"] == 0.0

    def test_stats_calculates_totals(self, sample_session):
        """Should calculate total stats correctly."""
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        # Save another winning session
        session2 = sample_session.copy()
        session2["buy_in"] = 100.0
        session2["cash_out"] = 200.0
        session2["duration_minutes"] = 120
        save_poker_session(session2, user_id=TEST_USER_ID)

        stats = get_session_stats(days=30, user_id=TEST_USER_ID)
        assert stats["total_sessions"] == 2
        assert stats["total_profit"] == 250.0  # 150 + 100
        assert stats["winning_sessions"] == 2
        assert stats["losing_sessions"] == 0

    def test_stats_calculates_hourly_rate(self, sample_session):
        """Should calculate correct hourly rate."""
        # Session 1: +150 in 3 hours
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        # Session 2: +100 in 2 hours
        session2 = sample_session.copy()
        session2["buy_in"] = 100.0
        session2["cash_out"] = 200.0
        session2["duration_minutes"] = 120
        save_poker_session(session2, user_id=TEST_USER_ID)

        stats = get_session_stats(days=30, user_id=TEST_USER_ID)
        # Total: +250 in 5 hours = 50/hr
        assert stats["hourly_rate"] == pytest.approx(50.0, rel=0.01)

    def test_stats_by_stake(self, sample_session):
        """Should break down stats by stake level."""
        save_poker_session(sample_session, user_id=TEST_USER_ID)  # 1/2, +150

        other_session = sample_session.copy()
        other_session["stake_level"] = "2/5"
        other_session["buy_in"] = 500.0
        other_session["cash_out"] = 400.0  # -100
        save_poker_session(other_session, user_id=TEST_USER_ID)

        stats = get_session_stats(days=30, user_id=TEST_USER_ID)
        by_stake = stats["by_stake"]

        assert "1/2" in by_stake
        assert by_stake["1/2"]["profit"] == 150.0
        assert "2/5" in by_stake
        assert by_stake["2/5"]["profit"] == -100.0

    def test_stats_win_rate(self, sample_session):
        """Should calculate win rate correctly."""
        # Win
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        # Loss
        losing = sample_session.copy()
        losing["buy_in"] = 200.0
        losing["cash_out"] = 100.0
        save_poker_session(losing, user_id=TEST_USER_ID)

        # Another win
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        stats = get_session_stats(days=30, user_id=TEST_USER_ID)
        assert stats["winning_sessions"] == 2
        assert stats["losing_sessions"] == 1
        assert stats["win_rate"] == pytest.approx(66.67, rel=0.1)


class TestGetBankrollData:
    """Tests for get_bankroll_data function."""

    def test_bankroll_empty(self):
        """Should return empty data when no sessions."""
        data = get_bankroll_data(days=30, user_id=TEST_USER_ID)
        assert data["data_points"] == []
        assert data["current_bankroll"] == 0.0

    def test_bankroll_cumulative(self, sample_session):
        """Should calculate cumulative bankroll correctly."""
        # Session 1: +150
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        # Session 2: -50 (next day)
        session2 = sample_session.copy()
        session2["date"] = datetime.now(timezone.utc) + timedelta(days=1)
        session2["buy_in"] = 200.0
        session2["cash_out"] = 150.0
        save_poker_session(session2, user_id=TEST_USER_ID)

        data = get_bankroll_data(days=30, user_id=TEST_USER_ID)
        assert len(data["data_points"]) == 2
        assert data["current_bankroll"] == 100.0  # 150 - 50

    def test_bankroll_peak_trough(self, sample_session):
        """Should track peak and trough values."""
        # +150
        save_poker_session(sample_session, user_id=TEST_USER_ID)

        # -200 (loss session)
        loss_session = sample_session.copy()
        loss_session["date"] = datetime.now(timezone.utc) + timedelta(days=1)
        loss_session["buy_in"] = 300.0
        loss_session["cash_out"] = 100.0
        save_poker_session(loss_session, user_id=TEST_USER_ID)

        data = get_bankroll_data(days=30, user_id=TEST_USER_ID)
        assert data["peak"] == 150.0
        # Current: 150 - 200 = -50 which is the trough
        assert data["trough"] == -50.0


class TestDeletePokerSession:
    """Tests for delete_poker_session function."""

    def test_delete_existing_session(self, sample_session):
        """Should delete an existing session."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)
        result = delete_poker_session(session_id, user_id=TEST_USER_ID)

        assert result is True
        sessions = get_poker_sessions(days=0, user_id=TEST_USER_ID)
        assert len(sessions) == 0

    def test_delete_nonexistent_session(self):
        """Should return False for non-existent session."""
        result = delete_poker_session(99999, user_id=TEST_USER_ID)
        assert result is False

    def test_delete_wrong_user(self, sample_session):
        """Should not delete session belonging to different user."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)
        # Try to delete with a different user_id
        result = delete_poker_session(session_id, user_id=TEST_USER_ID + 1)
        assert result is False


class TestUpdatePokerSession:
    """Tests for update_poker_session function."""

    def test_update_session_fields(self, sample_session):
        """Should update allowed fields."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)

        updates = {
            "notes": "Updated notes",
            "location": "New Location",
        }
        result = update_poker_session(session_id, updates, user_id=TEST_USER_ID)

        assert result is True
        sessions = get_poker_sessions(days=0, user_id=TEST_USER_ID)
        assert sessions[0]["notes"] == "Updated notes"
        assert sessions[0]["location"] == "New Location"

    def test_update_recalculates_profit(self, sample_session):
        """Should recalculate profit when buy_in or cash_out changes."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)

        updates = {"cash_out": 500.0}  # Was 350
        update_poker_session(session_id, updates, user_id=TEST_USER_ID)

        sessions = get_poker_sessions(days=0, user_id=TEST_USER_ID)
        assert sessions[0]["profit_loss"] == 300.0  # 500 - 200

    def test_update_nonexistent_session(self):
        """Should return False for non-existent session."""
        result = update_poker_session(99999, {"notes": "test"}, user_id=TEST_USER_ID)
        assert result is False


class TestPokerSessionModel:
    """Tests for PokerSession model properties."""

    def test_hourly_rate_property(self, sample_session):
        """Should calculate hourly rate correctly."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            session = (
                db.query(PokerSession).filter(PokerSession.id == session_id).first()
            )
            # 150 profit / 3 hours = 50/hr
            assert session.hourly_rate == pytest.approx(50.0, rel=0.01)
        finally:
            db.close()

    def test_hourly_rate_no_duration(self):
        """Should return None when no duration."""
        session_data = {
            "stake_level": "1/2",
            "buy_in": 100.0,
            "cash_out": 200.0,
        }
        session_id = save_poker_session(session_data, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            session = (
                db.query(PokerSession).filter(PokerSession.id == session_id).first()
            )
            assert session.hourly_rate is None
        finally:
            db.close()

    def test_bb_per_hour_standard_format(self, sample_session):
        """Should calculate bb/hr for standard stake format."""
        session_id = save_poker_session(sample_session, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            session = (
                db.query(PokerSession).filter(PokerSession.id == session_id).first()
            )
            # 150 profit / 2 BB = 75 BB, / 3 hours = 25 BB/hr
            assert session.bb_per_hour == pytest.approx(25.0, rel=0.01)
        finally:
            db.close()

    def test_bb_per_hour_nl_format(self):
        """Should calculate bb/hr for NL stake format."""
        session_data = {
            "date": datetime.now(timezone.utc),
            "stake_level": "NL50",  # 0.50 BB
            "buy_in": 50.0,
            "cash_out": 75.0,  # +25 profit
            "duration_minutes": 60,  # 1 hour
        }
        session_id = save_poker_session(session_data, user_id=TEST_USER_ID)

        db = SessionLocal()
        try:
            session = (
                db.query(PokerSession).filter(PokerSession.id == session_id).first()
            )
            # 25 profit / 0.50 BB = 50 BB, / 1 hour = 50 BB/hr
            assert session.bb_per_hour == pytest.approx(50.0, rel=0.01)
        finally:
            db.close()
