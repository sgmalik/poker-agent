"""Tests for the PokerCoachAgent."""

import os
import pytest
from unittest.mock import patch

from src.agent import PokerCoachAgent, AgentResponse, TokenUsage
from src.agent.prompts import GREETING_MESSAGE, POKER_COACH_SYSTEM_PROMPT


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_total_tokens(self):
        """Test total token calculation."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.total_tokens == 150

    def test_estimated_cost(self):
        """Test cost estimation."""
        usage = TokenUsage(input_tokens=1_000_000, output_tokens=1_000_000)
        # Input: $3 per 1M, Output: $15 per 1M
        expected_cost = 3.0 + 15.0
        assert usage.estimated_cost == expected_cost

    def test_zero_usage(self):
        """Test zero token usage."""
        usage = TokenUsage()
        assert usage.total_tokens == 0
        assert usage.estimated_cost == 0.0


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_response_with_content(self):
        """Test creating a response with content."""
        response = AgentResponse(
            content="Test response",
            tool_calls=["tool1", "tool2"],
        )
        assert response.content == "Test response"
        assert response.tool_calls == ["tool1", "tool2"]
        assert response.error is None

    def test_response_with_error(self):
        """Test creating a response with error."""
        response = AgentResponse(
            content="",
            error="Test error",
        )
        assert response.content == ""
        assert response.error == "Test error"


class TestPokerCoachAgent:
    """Tests for PokerCoachAgent class."""

    def test_agent_creation(self):
        """Test creating an agent instance."""
        agent = PokerCoachAgent()
        assert agent.model_name == "claude-sonnet-4-20250514"
        assert agent.chat_history == []

    def test_agent_custom_model(self):
        """Test creating agent with custom model."""
        agent = PokerCoachAgent(model="claude-3-opus-20240229")
        assert agent.model_name == "claude-3-opus-20240229"

    def test_greeting_property(self):
        """Test greeting property returns correct message."""
        agent = PokerCoachAgent()
        assert agent.greeting == GREETING_MESSAGE

    def test_clear_history(self):
        """Test clearing chat history."""
        agent = PokerCoachAgent()
        # Manually add to history
        agent.chat_history = ["message1", "message2"]
        agent.clear_history()
        assert agent.chat_history == []

    def test_get_stats_initial(self):
        """Test getting stats with no usage."""
        agent = PokerCoachAgent()
        stats = agent.get_stats()
        assert stats["messages"] == 0
        assert stats["input_tokens"] == 0
        assert stats["output_tokens"] == 0
        assert stats["total_tokens"] == 0
        assert stats["estimated_cost"] == 0.0

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=True)
    def test_agent_without_api_key(self):
        """Test that agent reports error without API key."""
        agent = PokerCoachAgent()
        # Trigger initialization
        assert agent.is_ready is False
        assert "ANTHROPIC_API_KEY" in agent.init_error


class TestPrompts:
    """Tests for prompt content."""

    def test_system_prompt_content(self):
        """Test that system prompt contains key elements."""
        assert "poker coach" in POKER_COACH_SYSTEM_PROMPT.lower()
        assert "tool" in POKER_COACH_SYSTEM_PROMPT.lower()
        assert "GTO" in POKER_COACH_SYSTEM_PROMPT

    def test_greeting_message_content(self):
        """Test that greeting contains helpful examples."""
        assert "example" in GREETING_MESSAGE.lower()
        assert "range" in GREETING_MESSAGE.lower() or "Range" in GREETING_MESSAGE


# Integration tests - only run if API key is available
# These tests are skipped unless ANTHROPIC_API_KEY is set AND pytest-asyncio is installed
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
class TestPokerCoachAgentIntegration:
    """Integration tests requiring an API key.

    These tests require pytest-asyncio to be installed.
    Run with: uv add pytest-asyncio && uv run pytest tests/agent/
    """

    @pytest.fixture
    def agent(self):
        """Create an agent for testing."""
        return PokerCoachAgent()

    def test_simple_chat_sync(self, agent):
        """Test a simple chat interaction using sync wrapper."""
        response = agent.chat_sync("What is a flush in poker?")
        assert response.error is None
        assert len(response.content) > 0
        assert "flush" in response.content.lower() or "Flush" in response.content

    def test_tool_usage_sync(self, agent):
        """Test that tools are used when appropriate using sync wrapper."""
        response = agent.chat_sync("What is the BTN opening range?")
        assert response.error is None
        # Should use the get_gto_range tool
        assert len(response.tool_calls) > 0 or "BTN" in response.content
