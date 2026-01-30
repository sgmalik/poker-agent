"""SQLAlchemy database models."""

from datetime import datetime, timezone
from typing import cast

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .db import Base


class PokerSession(Base):
    """Model for storing poker session records."""

    __tablename__ = "poker_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    date = Column(DateTime, nullable=False)
    stake_level = Column(String(20), nullable=False)  # e.g., "1/2", "2/5", "NL50"
    buy_in = Column(Float, nullable=False)
    cash_out = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    hands_played = Column(Integer, nullable=True)
    location = Column(String(100), nullable=True)  # e.g., "Bellagio", "PokerStars"
    game_type = Column(String(20), default="cash", nullable=False)  # cash, tournament
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    @property
    def hourly_rate(self) -> float | None:
        """Calculate hourly profit rate."""
        duration = cast(int, self.duration_minutes) if self.duration_minutes else 0
        profit = cast(float, self.profit_loss) if self.profit_loss else 0.0
        if duration <= 0:
            return None
        return profit / (duration / 60)

    @property
    def bb_per_hour(self) -> float | None:
        """Calculate big blinds per hour (requires stake parsing)."""
        duration = cast(int, self.duration_minutes) if self.duration_minutes else 0
        profit = cast(float, self.profit_loss) if self.profit_loss else 0.0
        stake = cast(str, self.stake_level) if self.stake_level else ""

        if duration <= 0 or not stake:
            return None

        # Parse stake level to get big blind
        try:
            if "/" in stake:
                # Format: "1/2" or "2/5"
                bb = float(stake.split("/")[1])
            elif stake.upper().startswith("NL"):
                # Format: "NL50" means $0.50 BB
                bb = float(stake[2:]) / 100
            else:
                return None

            hours = duration / 60
            return (profit / bb) / hours
        except (ValueError, IndexError):
            return None

    def __repr__(self) -> str:
        return (
            f"<PokerSession(id={self.id}, date={self.date}, profit={self.profit_loss})>"
        )


class QuizAttempt(Base):
    """Model for storing individual quiz question attempts."""

    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    question_id = Column(String(50), nullable=False)
    scenario = Column(Text, nullable=True)
    user_answer = Column(String(100), nullable=False)
    correct_answer = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=True)  # seconds
    difficulty = Column(String(20), nullable=True)
    topic = Column(String(50), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, question_id='{self.question_id}', is_correct={self.is_correct})>"


class QuizSession(Base):
    """Model for storing quiz session summaries."""

    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    topic = Column(String(50), nullable=True)  # None = all topics
    difficulty = Column(String(20), nullable=True)  # None = all difficulties
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    time_total = Column(Integer, nullable=True)  # seconds
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    @property
    def percentage(self) -> float:
        """Calculate score percentage."""
        total = cast(int, self.total_questions) if self.total_questions else 0
        correct = cast(int, self.correct_answers) if self.correct_answers else 0
        if total == 0:
            return 0.0
        return (correct / total) * 100

    def __repr__(self) -> str:
        return f"<QuizSession(id={self.id}, score={self.correct_answers}/{self.total_questions})>"


class HandHistory(Base):
    """Model for storing individual hand histories."""

    __tablename__ = "hand_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1, nullable=False)
    hero_hand = Column(String(10), nullable=False)  # "As Kh"
    board = Column(String(25), nullable=True)  # "Qh Jh 2c 5d 9s"
    position = Column(String(5), nullable=False)  # BTN, CO, etc.
    action_summary = Column(Text, nullable=True)  # "Raised pre, c-bet..."
    result = Column(String(10), nullable=False)  # won, lost, split
    stake_level = Column(String(10), nullable=True)  # "1/2", "NL50"
    pot_size = Column(Float, nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated
    notes = Column(Text, nullable=True)
    hand_text = Column(Text, nullable=True)  # Full hand narrative
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    @property
    def tag_list(self) -> list[str]:
        """Return tags as a list."""
        if not self.tags:
            return []
        return [t.strip() for t in cast(str, self.tags).split(",") if t.strip()]

    @property
    def street(self) -> str:
        """Determine which street the hand reached based on board cards."""
        if not self.board:
            return "preflop"
        board_str = cast(str, self.board).strip()
        cards = [c.strip() for c in board_str.split() if c.strip()]
        if len(cards) == 3:
            return "flop"
        elif len(cards) == 4:
            return "turn"
        elif len(cards) == 5:
            return "river"
        return "preflop"

    def __repr__(self) -> str:
        return f"<HandHistory(id={self.id}, hero_hand='{self.hero_hand}', result='{self.result}')>"
