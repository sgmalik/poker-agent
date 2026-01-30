"""Poker Coach AI Agent using LangChain and Anthropic Claude."""

from dataclasses import dataclass, field
from typing import Any, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import create_agent

from ..config import ANTHROPIC_API_KEY
from ..tools import ALL_TOOLS
from .prompts import POKER_COACH_SYSTEM_PROMPT, GREETING_MESSAGE


@dataclass
class TokenUsage:
    """Track token usage for cost estimation."""

    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost(self) -> float:
        """Estimate cost based on Claude Sonnet pricing.

        Pricing as of late 2024:
        - Input: $3 per 1M tokens
        - Output: $15 per 1M tokens
        """
        input_cost = (self.input_tokens / 1_000_000) * 3.0
        output_cost = (self.output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost


@dataclass
class AgentResponse:
    """Response from the agent including metadata."""

    content: str
    tool_calls: List[str] = field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    error: Optional[str] = None


class PokerCoachAgent:
    """AI Poker Coach powered by LangChain and Claude."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """Initialize the Poker Coach Agent.

        Args:
            model: The Claude model to use (default: claude-sonnet-4-20250514)
        """
        self.model_name = model
        self.chat_history: List[Any] = []
        self.total_usage = TokenUsage()
        self._agent: Any = None
        self._initialized = False
        self._init_error: Optional[str] = None

    def _initialize(self) -> bool:
        """Lazy initialization of the agent.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if self._initialized:
            return self._init_error is None

        api_key = ANTHROPIC_API_KEY
        if not api_key:
            self._init_error = (
                "ANTHROPIC_API_KEY not found. Please set it in your .env file."
            )
            self._initialized = True
            return False

        try:
            # Create the LLM
            llm = ChatAnthropic(
                model_name=self.model_name,
                api_key=api_key,
                max_tokens_to_sample=4096,
            )

            # Create the agent using the new LangChain API
            self._agent = create_agent(
                model=llm,
                tools=ALL_TOOLS,
                system_prompt=POKER_COACH_SYSTEM_PROMPT,
            )

            self._initialized = True
            return True

        except Exception as e:
            self._init_error = f"Failed to initialize agent: {str(e)}"
            self._initialized = True
            return False

    @property
    def greeting(self) -> str:
        """Get the greeting message."""
        return GREETING_MESSAGE

    @property
    def is_ready(self) -> bool:
        """Check if the agent is ready to use."""
        if not self._initialized:
            self._initialize()
        return self._init_error is None

    @property
    def init_error(self) -> Optional[str]:
        """Get any initialization error."""
        if not self._initialized:
            self._initialize()
        return self._init_error

    async def chat(self, user_input: str) -> AgentResponse:
        """Send a message to the agent and get a response.

        Args:
            user_input: The user's message

        Returns:
            AgentResponse with the agent's reply and metadata
        """
        # Initialize if needed
        if not self._initialize():
            return AgentResponse(
                content="",
                error=self._init_error,
            )

        try:
            # Build messages list with history and new input
            messages = list(self.chat_history) + [HumanMessage(content=user_input)]

            # Invoke the agent
            result = await self._agent.ainvoke({"messages": messages})

            # Extract the output from the result
            # The new API returns an AgentState with messages
            output_messages = result.get("messages", [])

            # Find the last AI message
            output_content: str = ""
            tool_calls: List[str] = []

            for msg in reversed(output_messages):
                if isinstance(msg, AIMessage):
                    # Handle content that might be a list or string
                    content = msg.content
                    if isinstance(content, list):
                        # Extract text from content blocks
                        output_content = " ".join(
                            str(c.get("text", c) if isinstance(c, dict) else c)
                            for c in content
                        )
                    else:
                        output_content = str(content)
                    # Check for tool calls in the message
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_calls = [tc.get("name", "") for tc in msg.tool_calls]
                    break

            if not output_content:
                output_content = "I apologize, but I couldn't generate a response."

            # Update chat history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=output_content))

            # Estimate token usage (rough approximation)
            input_estimate = len(user_input.split()) * 1.3
            output_estimate = len(output_content.split()) * 1.3
            usage = TokenUsage(
                input_tokens=int(input_estimate),
                output_tokens=int(output_estimate),
            )
            self.total_usage.input_tokens += usage.input_tokens
            self.total_usage.output_tokens += usage.output_tokens

            return AgentResponse(
                content=output_content,
                tool_calls=tool_calls,
                token_usage=usage,
            )

        except Exception as e:
            error_msg = str(e)
            return AgentResponse(
                content="",
                error=f"Error: {error_msg}",
            )

    def chat_sync(self, user_input: str) -> AgentResponse:
        """Synchronous version of chat for non-async contexts.

        Args:
            user_input: The user's message

        Returns:
            AgentResponse with the agent's reply and metadata
        """
        import asyncio

        # Check if we're already in an async context
        try:
            asyncio.get_running_loop()
            # We're in an async context, need to use a different approach
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.chat(user_input))
                return future.result()
        except RuntimeError:
            # No running loop, we can use asyncio.run directly
            return asyncio.run(self.chat(user_input))

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.chat_history = []

    def get_stats(self) -> dict[str, Any]:
        """Get usage statistics.

        Returns:
            Dictionary with token counts and estimated costs
        """
        return {
            "messages": len(self.chat_history),
            "input_tokens": self.total_usage.input_tokens,
            "output_tokens": self.total_usage.output_tokens,
            "total_tokens": self.total_usage.total_tokens,
            "estimated_cost": round(self.total_usage.estimated_cost, 4),
        }
