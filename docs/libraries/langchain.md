# LangChain Library Reference

## Overview

**LangChain** is a framework for building applications powered by large language models (LLMs). The Poker Coach Agent uses LangChain with Anthropic's Claude model to create an AI coaching agent with tool-calling capabilities.

**Official Documentation:** https://python.langchain.com/docs/

**API Reference:** https://api.python.langchain.com/

**Installation:**
```bash
pip install langchain langchain-anthropic
```

---

## Architecture

```
User Query
    ↓
LangChain Agent
    ↓
ChatAnthropic (LLM)
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Response Generation
    ↓
User Response
```

---

## LangChain Anthropic Integration

**Documentation:** https://python.langchain.com/docs/integrations/chat/anthropic

### Installation

```bash
pip install langchain-anthropic
```

### Import

```python
from langchain_anthropic import ChatAnthropic
```

### Creating a Chat Model

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model_name="claude-sonnet-4-20250514",
    api_key="your-api-key",
    max_tokens_to_sample=4096,
    temperature=0.7,
)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` | - | Claude model identifier |
| `api_key` | `str` | - | Anthropic API key |
| `max_tokens_to_sample` | `int` | `1024` | Maximum response tokens |
| `temperature` | `float` | `0.7` | Response randomness (0-1) |

### Available Models

| Model | ID | Description |
|-------|-----|-------------|
| Claude Sonnet | `claude-sonnet-4-20250514` | Balanced, recommended |
| Claude Opus | `claude-3-opus-20240229` | Most capable |
| Claude Haiku | `claude-3-haiku-20240307` | Fastest, cheapest |

---

## Messages

**Documentation:** https://python.langchain.com/docs/concepts/messages

### Import

```python
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)
```

### Message Types

#### HumanMessage

Message from the user.

```python
HumanMessage(content="What is my equity with AA vs KK?")
```

#### AIMessage

Message from the AI assistant.

```python
AIMessage(content="Your equity with AA vs KK is approximately 81.5%")
```

**Attributes:**
- `content` - Message text (str or list)
- `tool_calls` - List of tool invocations

#### SystemMessage

System instructions for the AI.

```python
SystemMessage(content="You are a helpful poker coach.")
```

#### ToolMessage

Result from a tool invocation.

```python
ToolMessage(content="{'equity': 81.5}", tool_call_id="call_123")
```

---

## Tools

**Documentation:** https://python.langchain.com/docs/concepts/tools

### Creating Tools with Decorator

```python
from langchain_core.tools import tool
from typing import Any

@tool
def my_tool(parameter: str) -> dict[str, Any]:
    """
    Description of what this tool does.

    This docstring becomes the tool's description for the AI.

    Args:
        parameter: Description of this parameter

    Returns:
        Dictionary with the result
    """
    result = process(parameter)
    return {"success": True, "result": result}
```

### Tool Properties from Decorator

The `@tool` decorator extracts:
- **Name** - From function name
- **Description** - From docstring
- **Parameters** - From function signature and type hints
- **Returns** - From return type hint

### Tool Return Pattern

Always return a dictionary with a `success` field:

```python
@tool
def example_tool(param: str) -> dict[str, Any]:
    """Tool description."""
    try:
        # ... operation ...
        return {
            "success": True,
            "data": result,
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
        }
```

### Tool with Optional Parameters

```python
from typing import Optional

@tool
def analyze_spot(
    hero_hand: str,
    board: str,
    pot_size: Optional[float] = None,
    bet_to_call: Optional[float] = None,
) -> dict[str, Any]:
    """
    Analyze a poker spot.

    Args:
        hero_hand: Your hole cards (e.g., "As Kh")
        board: Community cards (e.g., "Qh Jh 2c")
        pot_size: Current pot size (optional)
        bet_to_call: Amount to call (optional)

    Returns:
        Analysis dictionary with recommendations
    """
    # Implementation
    pass
```

### Tool with List Parameters

```python
from typing import List, Optional

@tool
def search_hands(
    tags: Optional[List[str]] = None,
    position: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search hand histories.

    Args:
        tags: Filter by tags (e.g., ["bluff", "value"])
        position: Filter by position (e.g., "BTN")

    Returns:
        List of matching hands
    """
    pass
```

---

## Agents

**Documentation:** https://python.langchain.com/docs/concepts/agents

### Creating an Agent

```python
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

# Create LLM
llm = ChatAnthropic(
    model_name="claude-sonnet-4-20250514",
    api_key=api_key,
)

# Create agent with tools
agent = create_agent(
    model=llm,
    tools=tools_list,
    system_prompt=system_prompt,
)
```

### Agent Invocation

```python
# Synchronous
result = agent.invoke({"messages": messages})

# Asynchronous
result = await agent.ainvoke({"messages": messages})
```

### Agent Result Structure

```python
result = agent.invoke({"messages": messages})

# Result contains messages list
output_messages = result.get("messages", [])

# Find the AI response
for msg in reversed(output_messages):
    if isinstance(msg, AIMessage):
        content = msg.content
        tool_calls = msg.tool_calls  # List of tool invocations
        break
```

---

## Complete Agent Implementation

### Agent Class

```python
from dataclasses import dataclass, field
from typing import Any, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import create_agent

from .tools import ALL_TOOLS
from .prompts import SYSTEM_PROMPT


@dataclass
class TokenUsage:
    """Track token usage."""
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class AgentResponse:
    """Response from the agent."""
    content: str
    tool_calls: List[str] = field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    error: Optional[str] = None


class PokerCoachAgent:
    """AI Poker Coach Agent."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model_name = model
        self.chat_history: List[Any] = []
        self.total_usage = TokenUsage()
        self._agent = None
        self._initialized = False
        self._init_error = None

    def _initialize(self) -> bool:
        """Initialize the agent."""
        if self._initialized:
            return self._init_error is None

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self._init_error = "ANTHROPIC_API_KEY not found"
            self._initialized = True
            return False

        try:
            llm = ChatAnthropic(
                model_name=self.model_name,
                api_key=api_key,
                max_tokens_to_sample=4096,
            )

            self._agent = create_agent(
                model=llm,
                tools=ALL_TOOLS,
                system_prompt=SYSTEM_PROMPT,
            )

            self._initialized = True
            return True

        except Exception as e:
            self._init_error = str(e)
            self._initialized = True
            return False

    @property
    def is_ready(self) -> bool:
        if not self._initialized:
            self._initialize()
        return self._init_error is None

    async def chat(self, user_input: str) -> AgentResponse:
        """Send a message and get a response."""
        if not self._initialize():
            return AgentResponse(content="", error=self._init_error)

        try:
            messages = list(self.chat_history) + [HumanMessage(content=user_input)]
            result = await self._agent.ainvoke({"messages": messages})

            # Extract response
            output_messages = result.get("messages", [])
            output_content = ""
            tool_calls = []

            for msg in reversed(output_messages):
                if isinstance(msg, AIMessage):
                    content = msg.content
                    if isinstance(content, list):
                        output_content = " ".join(
                            str(c.get("text", c) if isinstance(c, dict) else c)
                            for c in content
                        )
                    else:
                        output_content = str(content)

                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_calls = [tc.get("name", "") for tc in msg.tool_calls]
                    break

            # Update history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=output_content))

            return AgentResponse(
                content=output_content,
                tool_calls=tool_calls,
            )

        except Exception as e:
            return AgentResponse(content="", error=str(e))

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.chat_history = []
```

---

## System Prompts

The system prompt defines the agent's behavior and capabilities:

```python
SYSTEM_PROMPT = """You are an expert poker coach with access to these tools:

1. **Hand Evaluation** - Evaluate hands, calculate equity
2. **GTO Ranges** - Look up optimal preflop ranges
3. **Quiz Statistics** - Review quiz performance
4. **Session Tracking** - Analyze session results
5. **Hand History** - Search and analyze saved hands

## Tool Usage Guidelines

- Always use tools for accurate information
- Use `analyze_spot` for hand strength questions
- Use `get_gto_range` for range questions
- Use quiz/session/history tools for performance review

## Response Style

- Be encouraging but honest
- Explain concepts clearly
- Provide actionable recommendations
"""
```

---

## Tool Organization

### Tool Lists

```python
# Group tools by category
HAND_EVAL_TOOLS = [evaluate_hand, calculate_equity, analyze_spot]
RANGE_TOOLS = [get_gto_range, parse_range, check_hand_in_range]
QUIZ_TOOLS = [get_quiz_performance, find_study_leaks]
SESSION_TOOLS = [get_session_statistics, get_bankroll_analysis]
HISTORY_TOOLS = [search_hands, analyze_patterns]

# Combine all tools
ALL_TOOLS = (
    HAND_EVAL_TOOLS +
    RANGE_TOOLS +
    QUIZ_TOOLS +
    SESSION_TOOLS +
    HISTORY_TOOLS
)
```

### Exporting Tools

```python
# tools/__init__.py
from .hand_eval_tools import HAND_EVAL_TOOLS
from .range_tools import RANGE_TOOLS
from .quiz_tools import QUIZ_TOOLS
from .session_tools import SESSION_TOOLS
from .history_tools import HISTORY_TOOLS

ALL_TOOLS = (
    HAND_EVAL_TOOLS +
    RANGE_TOOLS +
    QUIZ_TOOLS +
    SESSION_TOOLS +
    HISTORY_TOOLS
)

__all__ = ["ALL_TOOLS", ...]
```

---

## Best Practices

### Tool Docstrings

Write detailed docstrings - they're the AI's guide:

```python
@tool
def get_gto_range(position: str, action: str = "open") -> dict[str, Any]:
    """
    Get the GTO (Game Theory Optimal) preflop range for a position and action.

    Args:
        position: The table position. Valid positions are:
            - UTG (Under the Gun - first to act)
            - UTG1 (UTG+1)
            - MP (Middle Position)
            - LJ (Lojack)
            - HJ (Hijack)
            - CO (Cutoff)
            - BTN (Button)
            - SB (Small Blind)
            - BB (Big Blind)
        action: The action type. Common actions include:
            - "open" - opening raise (RFI - Raise First In)
            - "call_vs_BTN" - calling vs button open (for BB)
            - "3bet_vs_BTN" - 3-betting vs button open

    Returns:
        Dictionary containing:
        - hands: List of hands in the range
        - notation: Compact range notation
        - total_combos: Total combinations
        - percentage: Percentage of all hands

    Example:
        get_gto_range("BTN", "open") -> {"hands": ["AA", "KK", ...], "percentage": 40.0}
    """
```

### Error Handling

Always handle errors gracefully:

```python
@tool
def my_tool(param: str) -> dict[str, Any]:
    """Tool description."""
    try:
        # Validate input
        if not param:
            return {"success": False, "error": "Parameter is required"}

        # Perform operation
        result = do_something(param)

        return {"success": True, "result": result}

    except ValueError as e:
        return {"success": False, "error": f"Invalid input: {str(e)}"}

    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

### Async Support

Use async for I/O operations:

```python
async def chat(self, user_input: str) -> AgentResponse:
    """Async chat method."""
    result = await self._agent.ainvoke({"messages": messages})
    # Process result...

def chat_sync(self, user_input: str) -> AgentResponse:
    """Sync wrapper for async chat."""
    import asyncio

    try:
        asyncio.get_running_loop()
        # In async context - use thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.chat(user_input))
            return future.result()
    except RuntimeError:
        # No loop - use asyncio.run
        return asyncio.run(self.chat(user_input))
```

---

## Environment Setup

### Required Environment Variables

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Loading Environment

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

---

## Additional Resources

- **LangChain Docs:** https://python.langchain.com/docs/
- **Anthropic API:** https://docs.anthropic.com/
- **Tool Calling Guide:** https://python.langchain.com/docs/concepts/tools
- **Agent Concepts:** https://python.langchain.com/docs/concepts/agents
