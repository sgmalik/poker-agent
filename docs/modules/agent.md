# Agent Module Documentation

## Overview

The agent module (`src/agent/`) implements the AI poker coaching agent using LangChain and Anthropic's Claude model. It provides conversational AI capabilities with access to all application tools for comprehensive poker analysis and coaching.

---

## Module Structure

```
src/agent/
├── __init__.py    # Module exports
├── coach.py       # PokerCoachAgent class implementation
└── prompts.py     # System prompts and greeting messages
```

---

## File: coach.py

### Purpose
Implements the main `PokerCoachAgent` class that orchestrates the AI coaching functionality, manages conversation history, tracks token usage, and handles tool invocation.

### Dependencies
- `langchain_anthropic` - Anthropic Claude integration
- `langchain_core.messages` - Message types
- `langchain.agents` - Agent creation
- `..config` - API key configuration
- `..tools` - ALL_TOOLS collection
- `.prompts` - System prompts

---

### Library Reference: LangChain Anthropic

**Documentation:** https://python.langchain.com/docs/integrations/chat/anthropic

**Installation:**
```bash
pip install langchain-anthropic
```

**Import:**
```python
from langchain_anthropic import ChatAnthropic
```

#### Class: `ChatAnthropic`

Creates a chat model instance connected to Anthropic's API.

**Constructor:**
```python
ChatAnthropic(
    model_name: str,
    api_key: str,
    max_tokens_to_sample: int = 1024,
    temperature: float = 0.7,
)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` | - | Claude model ID (e.g., "claude-sonnet-4-20250514") |
| `api_key` | `str` | - | Anthropic API key |
| `max_tokens_to_sample` | `int` | `1024` | Maximum response tokens |
| `temperature` | `float` | `0.7` | Response randomness (0-1) |

---

### Library Reference: LangChain Messages

**Documentation:** https://python.langchain.com/docs/concepts/messages

**Import:**
```python
from langchain_core.messages import AIMessage, HumanMessage
```

#### Class: `HumanMessage`

Represents a message from the user.

```python
HumanMessage(content: str)
```

#### Class: `AIMessage`

Represents a message from the AI assistant.

```python
AIMessage(content: str)
```

**Attributes:**
- `content` - The message text (str or list)
- `tool_calls` - List of tool invocations (if any)

---

### Library Reference: LangChain Agents

**Documentation:** https://python.langchain.com/docs/concepts/agents

**Import:**
```python
from langchain.agents import create_agent
```

#### Function: `create_agent`

Creates a LangChain agent with tools and a system prompt.

```python
create_agent(
    model: ChatAnthropic,
    tools: List[Tool],
    system_prompt: str,
) -> Agent
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `ChatAnthropic` | The LLM to use |
| `tools` | `List[Tool]` | Tools available to the agent |
| `system_prompt` | `str` | System instructions |

**Returns:**
| Type | Description |
|------|-------------|
| `Agent` | Configured agent instance |

---

### Dataclass: `TokenUsage`

Tracks token usage for cost estimation.

```python
@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
```

#### Properties

**`total_tokens`**
```python
@property
def total_tokens(self) -> int:
```
Returns the sum of input and output tokens.

**`estimated_cost`**
```python
@property
def estimated_cost(self) -> float:
```
Estimates cost based on Claude Sonnet pricing:
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Example:**
```python
usage = TokenUsage(input_tokens=1000, output_tokens=500)
print(usage.total_tokens)      # 1500
print(usage.estimated_cost)    # 0.0105 (rough estimate)
```

---

### Dataclass: `AgentResponse`

Response from the agent including metadata.

```python
@dataclass
class AgentResponse:
    content: str
    tool_calls: List[str] = field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    error: Optional[str] = None
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `content` | `str` | The agent's response text |
| `tool_calls` | `List[str]` | Names of tools called |
| `token_usage` | `Optional[TokenUsage]` | Token counts for this response |
| `error` | `Optional[str]` | Error message if request failed |

**Example:**
```python
response = await agent.chat("What is my equity with AA vs KK?")
if response.error:
    print(f"Error: {response.error}")
else:
    print(response.content)
    print(f"Tools used: {response.tool_calls}")
    print(f"Tokens: {response.token_usage.total_tokens}")
```

---

### Class: `PokerCoachAgent`

Main AI coaching agent class.

```python
class PokerCoachAgent:
    """AI Poker Coach powered by LangChain and Claude."""
```

#### Constructor

```python
def __init__(self, model: str = "claude-sonnet-4-20250514"):
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | `"claude-sonnet-4-20250514"` | Claude model identifier |

**Instance Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `model_name` | `str` | The Claude model being used |
| `chat_history` | `List[Any]` | Conversation message history |
| `total_usage` | `TokenUsage` | Cumulative token usage |
| `_agent` | `Any` | Internal LangChain agent |
| `_initialized` | `bool` | Whether initialization attempted |
| `_init_error` | `Optional[str]` | Initialization error message |

**Example:**
```python
from src.agent import PokerCoachAgent

# Use default model
agent = PokerCoachAgent()

# Use specific model
agent = PokerCoachAgent(model="claude-3-opus-20240229")
```

---

#### Method: `_initialize()`

Internal lazy initialization of the agent.

```python
def _initialize(self) -> bool:
```

**Returns:**
| Type | Description |
|------|-------------|
| `bool` | `True` if initialization succeeded |

**Process:**
1. Checks if already initialized
2. Validates `ANTHROPIC_API_KEY` is set
3. Creates `ChatAnthropic` LLM instance
4. Creates agent with `create_agent()`
5. Binds `ALL_TOOLS` and system prompt

**Error Conditions:**
- Missing API key: Sets `_init_error` with helpful message
- API/network error: Captures and stores error message

---

#### Property: `greeting`

Returns the greeting message for new conversations.

```python
@property
def greeting(self) -> str:
```

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Welcome message from `GREETING_MESSAGE` |

---

#### Property: `is_ready`

Checks if the agent is ready to accept messages.

```python
@property
def is_ready(self) -> bool:
```

**Returns:**
| Type | Description |
|------|-------------|
| `bool` | `True` if initialized without errors |

**Side Effect:** Triggers lazy initialization if not done.

---

#### Property: `init_error`

Returns any initialization error.

```python
@property
def init_error(self) -> Optional[str]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `Optional[str]` | Error message or `None` |

---

#### Method: `chat(user_input)` (async)

Sends a message to the agent and gets a response.

```python
async def chat(self, user_input: str) -> AgentResponse:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_input` | `str` | The user's message |

**Returns:**
| Type | Description |
|------|-------------|
| `AgentResponse` | Agent's reply with metadata |

**Process:**
1. Initializes agent if needed
2. Builds message list with history + new input
3. Invokes agent with `await self._agent.ainvoke()`
4. Extracts content from AI message
5. Records tool calls if any
6. Updates chat history
7. Estimates token usage
8. Returns `AgentResponse`

**Example:**
```python
import asyncio

async def main():
    agent = PokerCoachAgent()
    response = await agent.chat("What's my equity with AKs vs QQ preflop?")
    print(response.content)

asyncio.run(main())
```

---

#### Method: `chat_sync(user_input)`

Synchronous wrapper for `chat()` method.

```python
def chat_sync(self, user_input: str) -> AgentResponse:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_input` | `str` | The user's message |

**Returns:**
| Type | Description |
|------|-------------|
| `AgentResponse` | Agent's reply with metadata |

**Implementation Notes:**
- Handles both async and non-async contexts
- Uses `ThreadPoolExecutor` if in async context
- Uses `asyncio.run()` if no event loop running

**Example:**
```python
agent = PokerCoachAgent()
response = agent.chat_sync("Should I open A5s from UTG?")
print(response.content)
```

---

#### Method: `clear_history()`

Clears the conversation history.

```python
def clear_history(self) -> None:
```

**Use Case:** Starting a fresh conversation without recreating the agent.

**Example:**
```python
agent.clear_history()
print("Conversation reset")
```

---

#### Method: `get_stats()`

Returns usage statistics for the session.

```python
def get_stats(self) -> dict[str, Any]:
```

**Returns:**
```python
{
    "messages": int,           # Number of messages in history
    "input_tokens": int,       # Total input tokens used
    "output_tokens": int,      # Total output tokens used
    "total_tokens": int,       # Combined token count
    "estimated_cost": float,   # Estimated API cost (USD)
}
```

**Example:**
```python
stats = agent.get_stats()
print(f"Messages: {stats['messages']}")
print(f"Tokens used: {stats['total_tokens']}")
print(f"Estimated cost: ${stats['estimated_cost']:.4f}")
```

---

## File: prompts.py

### Purpose
Contains the system prompt and greeting message that define the agent's personality, capabilities, and behavior.

---

### Constant: `POKER_COACH_SYSTEM_PROMPT`

The system prompt that configures the AI's behavior.

```python
POKER_COACH_SYSTEM_PROMPT = """You are an expert poker coach..."""
```

**Sections:**

1. **Role Definition**
   - Expert poker coach with knowledge of Texas Hold'em
   - Access to hand evaluation, GTO ranges, quiz, session, and history tools

2. **Coaching Style Guidelines**
   - Be encouraging but honest
   - Use appropriate terminology
   - Back up advice with tool data
   - Provide actionable recommendations
   - Consider multiple factors in analysis

3. **Tool Usage Guidelines**
   - Always use tools for accuracy
   - Use `analyze_spot` or `evaluate_hand` for hand questions
   - Use `get_gto_range` or `check_hand_in_range` for range questions
   - Use quiz/session/history tools for performance review
   - Handle tool errors gracefully

4. **Card Notation Reference**
   - Ranks: 2-9, T, J, Q, K, A
   - Suits: s (spades), h (hearts), d (diamonds), c (clubs)
   - Example: "As Kh" = Ace of spades, King of hearts

5. **Key Poker Concepts**
   - Pot Odds formula
   - SPR (Stack-to-Pot Ratio)
   - Position hierarchy
   - GTO definition
   - Outs and rules of 2/4

---

### Constant: `GREETING_MESSAGE`

Initial message displayed when starting a conversation.

```python
GREETING_MESSAGE = """Welcome to your AI Poker Coach!..."""
```

**Content:**
- Capabilities overview
- Example questions
- Conversation starter prompt

**Example Questions Shown:**
- "What's my equity with AKs on Qh Jh 2c?"
- "Show me the BTN opening range"
- "How am I doing on quizzes?"
- "Analyze my recent session results"

---

## File: __init__.py

### Purpose
Module initialization and public API exports.

### Exports

```python
from .coach import PokerCoachAgent, AgentResponse, TokenUsage
from .prompts import POKER_COACH_SYSTEM_PROMPT, GREETING_MESSAGE

__all__ = [
    "PokerCoachAgent",
    "AgentResponse",
    "TokenUsage",
    "POKER_COACH_SYSTEM_PROMPT",
    "GREETING_MESSAGE",
]
```

### Usage

```python
# Import the agent
from src.agent import PokerCoachAgent

# Import response types
from src.agent import AgentResponse, TokenUsage

# Import prompts (for customization)
from src.agent import POKER_COACH_SYSTEM_PROMPT, GREETING_MESSAGE
```

---

## Complete Usage Example

```python
import asyncio
from src.agent import PokerCoachAgent

async def poker_coaching_session():
    # Initialize agent
    agent = PokerCoachAgent()

    # Check if ready
    if not agent.is_ready:
        print(f"Agent error: {agent.init_error}")
        return

    # Show greeting
    print(agent.greeting)
    print("-" * 50)

    # Conversation loop
    queries = [
        "What's my equity with As Ad against Kh Kd preflop?",
        "Should I open 87s from the cutoff?",
        "How have my quiz scores been this month?",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = await agent.chat(query)

        if response.error:
            print(f"Error: {response.error}")
        else:
            print(f"Coach: {response.content}")
            if response.tool_calls:
                print(f"(Used tools: {', '.join(response.tool_calls)})")

    # Show session stats
    print("\n" + "-" * 50)
    stats = agent.get_stats()
    print(f"Session Statistics:")
    print(f"  Messages: {stats['messages']}")
    print(f"  Total tokens: {stats['total_tokens']}")
    print(f"  Estimated cost: ${stats['estimated_cost']:.4f}")

# Run the session
asyncio.run(poker_coaching_session())
```

---

## Configuration Requirements

### Environment Variables

The agent requires the following environment variable:

```bash
# .env file
ANTHROPIC_API_KEY=your-api-key-here
```

### Config Integration

The API key is loaded via `src/config.py`:

```python
from ..config import ANTHROPIC_API_KEY
```

---

## Error Handling

### Initialization Errors

```python
agent = PokerCoachAgent()

if not agent.is_ready:
    error = agent.init_error
    # Possible errors:
    # - "ANTHROPIC_API_KEY not found..."
    # - "Failed to initialize agent: ..."
```

### Chat Errors

```python
response = await agent.chat("Hello")

if response.error:
    # Error occurred during API call
    print(f"Error: {response.error}")
else:
    # Success
    print(response.content)
```

---

## Integration with TUI

The agent is used in Mode 6 (AI Coach):

```python
# In mode6_chat.py
from src.agent import PokerCoachAgent

class Mode6ChatScreen(Screen):
    def __init__(self):
        super().__init__()
        self.agent = PokerCoachAgent()

    async def on_submit(self, user_input: str):
        response = await self.agent.chat(user_input)
        self.display_response(response)
```

---

## Token Usage Estimation

The agent uses a rough approximation for token counting:

```python
# Approximation: words * 1.3 ≈ tokens
input_estimate = len(user_input.split()) * 1.3
output_estimate = len(output_content.split()) * 1.3
```

**Note:** This is an estimate. Actual token counts may vary based on:
- Tokenization differences
- Special characters
- Tool call overhead
- System prompt tokens (not included in estimate)

For accurate billing, refer to Anthropic's API usage dashboard.

---

## Model Options

The agent supports any Claude model. Common options:

| Model | ID | Use Case |
|-------|------|----------|
| Claude Sonnet | `claude-sonnet-4-20250514` | Default, balanced |
| Claude Opus | `claude-3-opus-20240229` | Most capable |
| Claude Haiku | `claude-3-haiku-20240307` | Fastest, cheapest |

```python
# Use a different model
agent = PokerCoachAgent(model="claude-3-opus-20240229")
```
