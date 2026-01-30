# Poker Coach Agent - Build Charter

> **Version**: 2.2
> **Last Updated**: 2026-01-30
> **Status**: Phase 1 Complete - All 7 Modes Implemented + Quiz Expansion

## Project Vision

Build a rich, visually appealing **TUI (Text User Interface)** poker study application where each mode is a standalone tool that can also be accessed by an AI agent. The agent uses these tools to provide personalized coaching, identify leaks, and help users improve their poker game.

---

## Core Architecture Principle

**Standalone TUI Modes + Agent Interface**

Every feature is built as:
1. **Core Logic**: Pure Python classes with business logic (`src/core/`)
2. **TUI Screen**: Interactive Textual-based screen for direct user access (`src/tui/`)
3. **Agent Tool**: LangChain-compatible tool for AI agent (`src/tools/`)

```python
# Example: Same function used in both contexts

# TUI mode - Interactive full-screen interface
$ poker-coach
┌─ Poker Coach ─────────────────────────────┐
│                                           │
│  [1] Hand Evaluator & Spot Analyzer       │
│  [2] Range Tools                          │
│  [3] Quiz System                          │
│  [4] Session Tracker                      │
│  [5] Hand History Manager                 │
│  [6] AI Agent Coach                       │
│  [7] Admin Dashboard                      │
│                                           │
└───────────────────────────────────────────┘

# Agent mode (within TUI or standalone)
$ poker-coach agent
> "What's my equity with AK on QJ2 rainbow?"
🤖 Let me check... You have 52.3% equity with top pair and flush draw.
```

---

## Application Modes

### Mode 1: Hand Evaluator & Spot Analyzer

**Purpose**: Quick hand strength checks and comprehensive spot analysis

**TUI Interface**:
- Interactive form-based input for hand, board, pot size, bet, stack
- Real-time calculation and display of all analysis
- Tabbed views: Simple Eval | Hand vs Hand Equity | Spot Analysis
- Visual card selector or text input

**Features**:
- **Hand Strength**: Classification (pair, flush, etc.) ✅ IMPLEMENTED
- **Equity**: Monte Carlo simulation (hand vs hand) ✅ IMPLEMENTED
  - Note: Range-based equity pending (Mode 2 dependency)
- **Outs Counting**: Categorized by draw type ✅ IMPLEMENTED
  - Flush draws (9 outs)
  - Straight draws (OESD: 8 outs, gutshot: 4 outs)
  - Overcards (3 outs per card)
  - Pair improvements (to trips, two pair)
  - Backdoor draws
- **Pot Odds**: Percentage and ratio format ✅ IMPLEMENTED
- **Implied Odds**: Conservative estimation ✅ IMPLEMENTED
- **SPR**: Stack-to-Pot Ratio with categorization (low/medium/high) ✅ IMPLEMENTED
- **EV Calculation**: Call/Fold EV ✅ IMPLEMENTED
- **Decision Recommendation**: With reasoning and confidence ✅ IMPLEMENTED

**Rich Output Example (Simple)**:
```
┌──────────────────────────────────────────┐
│  Hand Evaluation                         │
├──────────────────────────────────────────┤
│  Hero: A♠ K♠                             │
│  Board: Q♠ J♠ 2♣                         │
│                                          │
│  Hand Strength: Flush Draw               │
│  Equity vs Random: 52.3%                 │
│  Outs: 15 (9 spades + 6 straights)       │
└──────────────────────────────────────────┘
```

**Rich Output Example (Comprehensive)**:
```
┌──────────────────────────────────────────┐
│  Spot Analysis                           │
├──────────────────────────────────────────┤
│  Hero: A♠ K♠                             │
│  Board: Q♠ J♠ 2♣                         │
│  Pot: $100 | Bet to Call: $50            │
│  Effective Stack: $500                   │
│                                          │
│  HAND STRENGTH                           │
│  └─ Flush Draw + Overcards               │
│                                          │
│  EQUITY & OUTS                           │
│  └─ Equity: 52.3% (vs random)            │
│  └─ Outs: 15 (9♠ + 6 straights)          │
│                                          │
│  POT ODDS                                │
│  └─ Pot Odds: 33.3% (need to win)        │
│  └─ Your Equity: 52.3%                   │
│  └─ ✓ Profitable to call                 │
│                                          │
│  STACK CONSIDERATIONS                    │
│  └─ SPR: 3.3 (Medium commitment)         │
│  └─ Pot Odds: Getting 2:1               │
│                                          │
│  EXPECTED VALUE                          │
│  └─ EV of Call: +$28.50                  │
│  └─ EV of Fold: $0                       │
│                                          │
│  RECOMMENDATION: CALL                    │
│  Reason: Equity (52.3%) exceeds pot      │
│  odds requirement (33.3%). Positive EV.  │
└──────────────────────────────────────────┘
```

**Core Classes**:
```python
# src/core/hand_evaluator.py
class HandEvaluator:
    """Simple hand strength evaluation."""
    def evaluate(hero_hand, board) -> dict

class EquityCalculator:
    """Simple equity calculation (hand vs hand)."""
    def calculate(hero, villain, board, iterations) -> dict

# src/core/spot_analyzer.py
class SpotAnalyzer:
    """Comprehensive spot analysis with all poker math."""
    def analyze(
        hero_hand, board,
        pot_size=None, bet_to_call=None,
        effective_stack=None, villain_range=None
    ) -> dict:
        """
        Returns complete analysis:
        - hand_strength, equity, outs
        - pot_odds, implied_odds, spr
        - ev (call/fold/raise)
        - recommendation with reasoning
        """
```

**Tool Signatures** (for Agent):
```python
@tool
def evaluate_hand(hero_hand: str, board: str) -> dict:
    """
    Quick hand strength evaluation.
    Use when user just wants to know hand strength or basic equity.
    """

@tool
def analyze_spot(
    hero_hand: str, board: str,
    pot_size: float = None,
    bet_to_call: float = None,
    effective_stack: float = None
) -> dict:
    """
    Comprehensive spot analysis with all poker math.

    Use when user wants full analysis including pot odds, SPR, EV,
    or asks "should I call/fold/raise" or "what's the right play".

    Returns all calculations: equity, outs, pot odds, SPR, EV, recommendation.
    """
```

---

### Mode 2: Range Tools ✅ COMPLETE

**Purpose**: Study and reference GTO range charts

**TUI Interface**:
- Position selector (9 positions: UTG, UTG+1, MP, LJ, HJ, CO, BTN, SB, BB) ✅
- Action selector (Open, 3-bet, Call vs positions) ✅
- Visual 13×13 hand matrix with color-coded ranges ✅
- Custom range input field ✅
- Range parser with combo breakdown ✅

**Features**:
- 9-handed GTO preflop ranges for 1/2 and 1/3 cash games ✅
- Open ranges for all 9 positions ✅
- 3-bet ranges for all positions vs earlier positions ✅
- BB call ranges vs each position (no overlap with 3-bet) ✅
- 13×13 hand matrix with colors (Red=Pairs, Green=Suited, Blue=Offsuit) ✅
- Bright highlighting for in-range, faded for not-in-range ✅
- Range parser (QQ+, AKs, 98s+, QQ-88, A5s-A2s) ✅
- Combo counting (pairs=6, suited=4, offsuit=12) ✅

**Core Classes**: `RangeParser`, `GTOCharts`
**TUI Screens**: `Mode2InputScreen`, `Mode2MatrixScreen`
**Data**: `data/gto_ranges.json`
**Tests**: `test_range_parser.py`, `test_gto_charts.py`

**Pending Enhancement**:
- Mixed frequency hands with hover tooltips showing percentages

**Rich Output Example**:
```
┌─────────────────────────────────────────────────────────┐
│  GTO Opening Range - BTN vs BB                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│      A    K    Q    J    T    9    8    7    6    5     │
│  A  [AA] [AKs][AQs][AJs][ATs][A9s][A8s][A7s][A6s][A5s]  │
│  K  [AKo][KK] [KQs][KJs][KTs][K9s][K8s][K7s][K6s][K5s]  │
│  Q  [AQo][KQo][QQ] [QJs][QTs][Q9s][Q8s][Q7s]│  │  │     │
│  ...                                                     │
│                                                          │
│  Green = Suited | Blue = Offsuit | Red = Pairs          │
│  Total Combos: 326 (46% of hands)                       │
└─────────────────────────────────────────────────────────┘
```

**Tool Signatures** (for Agent):
```python
@tool
def get_gto_range(position: str, action: str) -> dict:
    """Get GTO range for position/action."""

@tool
def parse_range(range_notation: str) -> dict:
    """Parse range notation into combos."""
```

---

### Mode 3: Quiz System ✅ COMPLETE

**Purpose**: Interactive learning through scenario-based quizzes

**TUI Interface**:
- Topic/difficulty selector menu ✅
- Full-screen quiz interface with scenario display ✅
- Interactive answer selection (A/B/C/D buttons + keyboard shortcuts) ✅
- Immediate feedback with explanations ✅
- Progress tracking with visual indicators ✅
- Results screen with performance breakdown by topic/difficulty ✅

**Features**:
- Interactive quiz sessions with immediate feedback ✅
- Multiple question types (preflop_action, range_check, hand_strength, pot_odds, position_open, postflop_action, and more) ✅
- Difficulty levels (beginner, intermediate, advanced, elite) ✅
- 216 questions across 7 topics (preflop, ranges, pot_odds, hand_strength, position, postflop, game_theory) ✅
- Focus on situational scenarios that require thinking (intermediate/advanced/elite difficulty weighted)
- Performance tracking with SQLite persistence ✅
- Saves quiz attempts and sessions to database (including partial quizzes) ✅
- `questions_attempted` tracking for accurate stats on early quit ✅
- Study leak identification (find weak areas) ✅
- Results screen with incorrect answer review ✅

**Core Classes**: `QuizEngine`, question validation/formatting utilities
**TUI Screens**: `Mode3SetupScreen`, `Mode3QuizScreen`, `Mode3ResultsScreen`
**Database Models**: `QuizAttempt`, `QuizSession`
**Data**: `data/quiz_bank.json`
**Tests**: `test_engine.py`, `test_questions.py`, `test_service.py`

**Rich Output Example**:
```
┌─────────────────────────────────────────────────────────┐
│  Quiz: Preflop Decision Making                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Scenario:                                               │
│  Position: BB                                            │
│  Villain: BTN opens to 2.5BB                            │
│  Your Hand: Q♠ J♠                                       │
│                                                          │
│  What should you do?                                     │
│  [A] Fold                                               │
│  [B] Call                                               │
│  [C] 3-bet                                              │
│                                                          │
└─────────────────────────────────────────────────────────┘

Your answer: B

✅ Correct! QJs is in BB's calling range vs BTN.

Explanation: QJs has good playability and blocks some of BTN's
continuing range. It's too weak to 3-bet but too strong to fold.

Progress: ████████████░░░░░░░░ 12/20
```

**Database Schema**:
```sql
quiz_attempts (
    id, user_id, question_id, scenario,
    user_answer, correct_answer, is_correct,
    time_taken, difficulty, topic, created_at
)

quiz_sessions (
    id, user_id, topic, difficulty,
    total_questions, questions_attempted,
    correct_answers, time_total, created_at
)

-- Note: Accuracy is calculated as (correct_answers / questions_attempted) * 100
-- This allows proper tracking when user quits a quiz early
```

**Service Functions** (for persistence):
```python
def save_quiz_attempt(attempt: dict, user_id: int = 1) -> int
def save_quiz_session(results: dict, topic: str, difficulty: str) -> int
def get_quiz_stats(user_id: int, topic: str = None, days: int = 30) -> dict
def identify_study_leaks(user_id: int, min_attempts: int = 5) -> list
def get_recent_sessions(user_id: int, limit: int = 10) -> list
def get_question_performance(user_id: int, question_id: str = None) -> dict
```

**Tool Signatures** (for Agent):
```python
@tool
def get_quiz_performance(topic: str = None, days: int = 30) -> dict:
    """Get quiz performance statistics."""

@tool
def find_study_leaks(min_attempts: int = 5, threshold: float = 60.0) -> list:
    """Analyze quiz history to identify knowledge gaps."""

@tool
def add_quiz_question(topic: str, difficulty: str, question_type: str, ...) -> dict:
    """Add a new quiz question to the question bank."""

@tool
def get_quiz_bank_stats() -> dict:
    """Get statistics about current quiz bank coverage."""
```

---

### Mode 4: Session Tracker ✅ COMPLETE

**Purpose**: Track poker sessions, bankroll, and results

**TUI Interface**:
- Session entry form with validation ✅
- Session history table with filtering/sorting ✅
- Session detail view on row click ✅
- Stats dashboard with graphs and charts ✅
- Bankroll progression visualization ✅
- Menu screen with quick stats ✅

**Features**:
- Session logging (interactive form with validation) ✅
- Bankroll tracking with plotext graphs (braille characters for smooth curves) ✅
- Win rate calculations (bb/100, $/hour) ✅
- Variance analysis and max drawdown calculation ✅
- Streak tracking (current and longest win/loss streaks) ✅
- Bankroll health analysis with recommendations ✅
- Session filtering by date range and stake level ✅
- "All Stakes" as default filter ✅
- Notes column in session history table ✅
- Beautiful tables for session history ✅
- All-time view with `days=0` parameter ✅

**Core Classes**: `PokerSession` (model), session service functions
**TUI Screens**: `Mode4MenuScreen`, `Mode4EntryScreen`, `Mode4HistoryScreen`, `Mode4StatsScreen`, `Mode4DetailScreen`
**Core Logic**: `session_tracker.py` (variance, drawdown, health analysis, streaks, plotext graphs with `uncolorize()` for Textual compatibility)
**Tests**: `test_session_service.py`, `test_session_tracker.py` (isolated with `TEST_USER_ID=99999` to preserve user data)

**Rich Output Example**:
```
┌─────────────────────────────────────────────────────────┐
│  Session Statistics (Last 30 Days)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Total Sessions: 45                                      │
│  Total Profit: $450.50                                   │
│  Win Rate: 5.2 bb/100                                    │
│  Hourly Rate: $15.30                                     │
│  Total Hours: 90                                         │
│                                                          │
│  Bankroll Graph:                                         │
│  $2500 ┤                                            ╭─   │
│  $2000 ┤                                    ╭───────╯    │
│  $1500 ┤                        ╭───────────╯            │
│  $1000 ┤            ╭───────────╯                        │
│   $500 ┤────────────╯                                    │
│        └────────────────────────────────────────────     │
│         Dec 1      Dec 15      Dec 30      Jan 13        │
└─────────────────────────────────────────────────────────┘

Recent Sessions:
┌──────────┬────────┬─────────┬──────────┬──────────┐
│ Date     │ Stake  │ Buy-in  │ Cash-out │ Profit   │
├──────────┼────────┼─────────┼──────────┼──────────┤
│ Jan 13   │ NL50   │ $50     │ $75      │ +$25     │
│ Jan 12   │ NL50   │ $50     │ $45      │ -$5      │
│ Jan 10   │ NL25   │ $25     │ $40      │ +$15     │
└──────────┴────────┴─────────┴──────────┴──────────┘
```

**Database Schema**:
```sql
sessions (
    id, user_id, date, stake_level,
    buy_in, cash_out, profit_loss,
    duration_minutes, hands_played,
    location, notes, created_at
)
```

**Tool Signatures** (for Agent):
```python
@tool
def get_session_stats(user_id: int, days: int = 30) -> dict:
    """Get session statistics."""

@tool
def get_bankroll_health(user_id: int) -> dict:
    """Analyze bankroll health and make recommendations."""
```

---

### Mode 5: Hand History Manager ✅ COMPLETE

**Purpose**: Store and retrieve historical hands

**TUI Interface**:
- Hand entry form with validation ✅
- Searchable hand library with filters (tags, date, position, result) ✅
- Hand history table with Stake and Notes columns ✅
- Hand detail view with full breakdown (all fields visible) ✅
- Tagging interface (23 predefined tags) ✅
- Pattern analysis with insights ✅

**Features**:
- Manual hand entry with validation ✅
- Tagging system (23 predefined tags: bluff, value, mistake, hero_call, etc.) ✅
- Search and filter by position, result, tags, date ✅
- Display hands with formatting ✅
- Click-to-view detail screen showing all hand data ✅
- Pattern analysis with insights ✅
- Win rate by position and tag ✅
- Bluff success rate tracking ✅

**Core Classes**: `HandHistory` (model), `hand_history.py` (validation, formatting, patterns)
**TUI Screens**: `Mode5MenuScreen`, `Mode5EntryScreen`, `Mode5HistoryScreen`, `Mode5DetailScreen`
**Tests**: `test_hand_history.py`, `test_hand_history_service.py`

**Rich Output Example**:
```
┌─────────────────────────────────────────────────────────┐
│  Add Hand to History                                     │
└─────────────────────────────────────────────────────────┘

Your hand: As Kh
Board: Qh Jh 2c 5d 9s
Position: BTN
Action summary: Raised pre, c-bet flop, barreled turn, river bluff
Result: won/lost? won
Tags (comma-separated): bluff, river
Notes: Villain folded river to 2/3 pot bet

✅ Hand saved! (ID: 123)

──────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────┐
│  Search Results (tag: bluff)                             │
├─────────────────────────────────────────────────────────┤
│  [#123] Jan 13 - BTN - NL50                             │
│  Hand: A♠ K♥                                            │
│  Board: Q♥ J♥ 2♣ 5♦ 9♠                                  │
│  Result: Won                                             │
│  Tags: bluff, river                                      │
│  ───────────────────────────────────────────────────────│
│  [#118] Jan 10 - CO - NL50                              │
│  Hand: 7♠ 6♠                                            │
│  Board: A♥ K♣ 2♦ 8♠ 3♣                                  │
│  Result: Lost                                            │
│  Tags: bluff, failed                                     │
└─────────────────────────────────────────────────────────┘
```

**Database Schema**:
```sql
hand_histories (
    id, user_id, hand_text,
    hero_hand, board, position,
    action_summary, result,
    stake_level, pot_size,
    tags, notes, created_at
)
```

**Tool Signatures** (for Agent):
```python
@tool
def search_hands(user_id: int, tags: list = None, days_back: int = 30) -> list:
    """Search hand history."""

@tool
def analyze_hand_patterns(user_id: int) -> dict:
    """Find patterns in stored hands."""
```

---

### Mode 6: AI Agent (Coaching Mode) ✅ COMPLETE

**Purpose**: Conversational coach with access to all tools and user data

**TUI Interface**:
- Full-screen chat interface ✅
- Message history with role-based formatting (user/assistant/tool/error) ✅
- Tool call indicators showing when agent uses tools ✅
- Token/cost tracking in header ✅
- Clear chat and back navigation ✅

**Features**:
- Interactive chat interface with Textual TUI ✅
- Access to all 5 modes as LangChain tools (15 tools total) ✅
- Context-aware responses based on user data ✅
- Multi-turn conversations with memory ✅
- Cost tracking and token management ✅
- Async agent execution with loading indicators ✅

**Core Classes**: `PokerCoachAgent` (src/agent/coach.py)
**TUI Screens**: `Mode6ChatScreen`
**Agent Prompts**: `src/agent/prompts.py` (system prompt, greeting message)
**Tests**: `test_coach.py`, `test_hand_eval_tools.py`, `test_range_tools.py`

**LangChain Tools** (src/tools/):
- `hand_eval_tools.py`: evaluate_hand, calculate_equity, analyze_spot
- `range_tools.py`: get_gto_range, list_available_ranges, parse_range, check_hand_in_range
- `quiz_tools.py`: get_quiz_performance, find_study_leaks, get_recent_quiz_sessions
- `session_tools.py`: get_session_statistics, get_bankroll_analysis, get_session_history, get_bankroll_progression
- `history_tools.py`: search_hands, get_hand_statistics, analyze_patterns, list_available_tags

**Rich Output Example**:
```
┌─────────────────────────────────────────────────────────┐
│  🃏 Poker Coach Agent                                   │
│  Type 'exit' to quit | 'help' for commands              │
└─────────────────────────────────────────────────────────┘

You: I'm struggling with 3-bet defense. Help me improve.

🤖 Let me analyze your performance...

[Agent calls identify_study_leaks()]
[Agent calls get_quiz_stats(topic='3-bet defense')]
[Agent calls search_hands(tags=['3-bet'])]

┌─────────────────────────────────────────────────────────┐
│  Analysis Results                                        │
├─────────────────────────────────────────────────────────┤
│  Quiz Performance: 45% accuracy on 3-bet defense         │
│  Weak areas: Calling vs 3-bet, 4-bet bluffing           │
│  Recent hands: 5 found with 3-bet tag                    │
└─────────────────────────────────────────────────────────┘

Based on your data, here's what I recommend:

1. **Study GTO 3-bet defense ranges** - You're folding too often
   Run: `poker-coach range show BB-vs-3bet`

2. **Practice with quizzes** - Focus on 3-bet scenarios
   Run: `poker-coach quiz start --topic 3bet-defense`

3. **Review your hands** - You called too wide with weak hands
   Run: `poker-coach hands search --tag 3-bet`

Your 3-bet defense is costing you ~$5/hour. Let's fix this!

You: Show me the BB vs 3-bet range

🤖 [Agent calls get_gto_range('BB', '3bet_defense')]

[Displays range chart with Rich formatting]

You: exit

──────────────────────────────────────────────────────────
Session Summary:
- Messages: 4
- Tools used: 4
- Tokens: ~500
- Cost: $0.02
──────────────────────────────────────────────────────────
```

**Agent Architecture**:
```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from rich.console import Console
from rich.panel import Panel

tools = [
    evaluate_hand,
    get_gto_range,
    parse_range,
    get_quiz_stats,
    identify_study_leaks,
    get_session_stats,
    get_bankroll_health,
    search_hands,
    analyze_hand_patterns
]

llm = ChatAnthropic(model="claude-sonnet-4")
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Rich console for beautiful output
console = Console()

while True:
    user_input = console.input("[bold cyan]You:[/bold cyan] ")
    response = agent_executor.invoke({"input": user_input})
    console.print(Panel(response['output'], title="🤖 Coach"))
```

---

### Mode 7: Admin Dashboard ✅ COMPLETE

**Purpose**: View and manage raw database tables for data administration

**TUI Interface**:
- Single dynamic screen with table selector dropdown ✅
- DataTable showing selected database table records ✅
- Table-specific filter dropdowns (topic, difficulty, result, etc.) ✅
- Summary statistics panel ✅
- Delete functionality with confirmation ✅

**Features**:
- View all 4 database tables: Quiz Attempts, Quiz Sessions, Poker Sessions, Hand Histories ✅
- All columns viewable for every table (including Scenario, Notes, Hand Text, etc.) ✅
- Dynamic filter dropdowns based on selected table ✅
- Table record counts in summary panel ✅
- Delete records by ID ✅
- Column-specific formatting (dates, booleans, truncated text) ✅
- Navigate back to main menu ✅

**Core Classes**: Dynamic table configuration with `TABLE_CONFIG`
**TUI Screen**: `Mode7AdminScreen`
**Database Service**: `get_admin_stats`, `get_quiz_attempts`, `get_quiz_sessions_list`, `delete_quiz_attempt`, `delete_quiz_session`

**Rich Output Example**:
```
┌─────────────────────────────────────────────────────────┐
│  Admin Dashboard                                        │
├─────────────────────────────────────────────────────────┤
│  Table: [Quiz Attempts ▼]                               │
│                                                          │
│  Filters:                                               │
│  Topic: [All ▼]  Difficulty: [All ▼]  Result: [All ▼]   │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐│
│  │ID │Date      │Question│Topic   │Difficulty│Correct│ ││
│  ├──────────────────────────────────────────────────────┤│
│  │1  │2026-01-30│PF001   │preflop │intermediate│Yes   │ ││
│  │2  │2026-01-30│PS002   │postflop│advanced   │No    │ ││
│  └──────────────────────────────────────────────────────┘│
│                                                          │
│  Summary: 45 quiz attempts, 12 quiz sessions,           │
│           23 poker sessions, 67 hand histories          │
│                                                          │
│  [Delete Selected] [Refresh] [Back]                     │
└─────────────────────────────────────────────────────────┘
```

---

## Technical Stack

### Core
- **Language**: Python 3.12+
- **Package Manager**: uv
- **TUI Framework**: Textual (full-screen terminal application)
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

### AI/Agent
- **Agent Framework**: LangChain (langchain>=1.2.3)
- **LLM Provider**: langchain-anthropic (Claude Sonnet 4 for coaching)
- **Tool System**: `@tool` decorator from LangChain

### Poker
- **Hand Evaluation**: treys (bit manipulation for fast evaluation)
- **Equity Calculation**: Custom Monte Carlo implementation

### Code Quality
- **Formatting**: black
- **Linting**: ruff
- **Type Checking**: pyrefly
- **Testing**: pytest (415+ tests)

---

## Database Schema

```sql
-- Session tracking
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER DEFAULT 1,  -- Single user for CLI
    date DATETIME NOT NULL,
    stake_level VARCHAR(10) NOT NULL,
    buy_in FLOAT NOT NULL,
    cash_out FLOAT NOT NULL,
    profit_loss FLOAT NOT NULL,
    duration_minutes INTEGER,
    hands_played INTEGER,
    location VARCHAR(50),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Quiz attempts
CREATE TABLE quiz_attempts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER DEFAULT 1,
    question_id INTEGER,
    scenario TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken INTEGER,
    difficulty VARCHAR(20),
    topic VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Hand histories
CREATE TABLE hand_histories (
    id INTEGER PRIMARY KEY,
    user_id INTEGER DEFAULT 1,
    hand_text TEXT,
    hero_hand VARCHAR(10),
    board VARCHAR(20),
    position VARCHAR(5),
    action_summary TEXT,
    result VARCHAR(20),
    stake_level VARCHAR(10),
    pot_size FLOAT,
    tags TEXT,  -- Comma-separated for SQLite
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_sessions_date ON sessions(date);
CREATE INDEX idx_quiz_topic ON quiz_attempts(topic);
CREATE INDEX idx_hands_tags ON hand_histories(tags);
```

---

## File Structure

```
poker-agent/
├── src/
│   ├── config.py               # Centralized configuration (API keys, paths, DB URL)
│   ├── core/                    # Core poker engine
│   │   ├── __init__.py
│   │   ├── hand_evaluator.py   # Hand eval + equity (treys)
│   │   ├── range_parser.py     # Range notation parser
│   │   └── gto_charts.py       # Hardcoded GTO ranges
│   │
│   ├── tools/                   # LangChain tools (all modes)
│   │   ├── __init__.py
│   │   ├── hand_eval_tool.py   # @tool for hand evaluation
│   │   ├── range_tool.py       # @tool for ranges
│   │   ├── quiz_tool.py        # @tool for quiz stats
│   │   ├── session_tool.py     # @tool for session/bankroll
│   │   └── history_tool.py     # @tool for hand history
│   │
│   ├── database/                # Database layer
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy models
│   │   └── service.py          # CRUD operations
│   │
│   ├── quiz/                    # Quiz system
│   │   ├── __init__.py
│   │   ├── engine.py           # Quiz logic
│   │   ├── questions.py        # Question bank
│   │   └── spaced_rep.py       # Spaced repetition algorithm
│   │
│   ├── agent/                   # AI agent
│   │   ├── __init__.py
│   │   ├── coach.py            # LangChain agent setup
│   │   └── prompts.py          # System prompts
│   │
│   └── cli/                     # CLI interface
│       ├── __init__.py
│       └── main.py             # Typer commands + Rich formatting
│
├── tests/                       # Test suite
│   ├── core/
│   ├── tools/
│   └── database/
│
├── data/                        # Static data
│   ├── gto_ranges.json         # GTO preflop charts
│   └── quiz_questions.json     # Question bank
│
├── local/                       # Documentation
│   ├── SYSTEM_DESIGN.md
│   └── LEARNING_PIPELINE.md
│
├── BUILD_CHARTER.md            # This file
├── pyproject.toml              # uv dependencies
└── poker_coach.db              # SQLite database (gitignored)
```

---

## Tool Design Pattern

Every feature follows this pattern:

```python
# 1. Core implementation (pure logic, no CLI/agent dependencies)
def evaluate_hand_impl(hero_hand: str, board: str) -> dict:
    """Pure Python implementation - testable without CLI or LLM."""
    evaluator = Evaluator()
    # ... treys logic ...
    return {
        'hand_class': 'Flush Draw',
        'equity': 52.3,
        'outs': 15
    }

# 2. CLI command (Rich formatting)
from rich.console import Console
from rich.panel import Panel

console = Console()

@app.command()
def eval(hand: str, board: str):
    """
    Evaluate poker hand strength.

    Example: poker-coach eval "As Kh" "Qh Jh 2c"
    """
    result = evaluate_hand_impl(hand, board)

    # Rich formatting
    output = f"""
    Hero: {format_cards(hand)}
    Board: {format_cards(board)}

    Hand Strength: {result['hand_class']}
    Equity: {result['equity']:.1f}%
    Outs: {result['outs']}
    """

    console.print(Panel(output, title="Hand Evaluation", border_style="green"))

# 3. LangChain tool (agent access)
from langchain.tools import tool

@tool
def evaluate_hand(hero_hand: str, board: str) -> dict:
    """
    Evaluate poker hand strength and equity.

    Use this when user asks about hand strength, equity, winning probability,
    or wants to know how strong their hand is.

    Args:
        hero_hand: Hero's cards (e.g., "As Kh")
        board: Board cards (e.g., "Qh Jh 2c")

    Returns:
        Dictionary with hand_class, equity, outs
    """
    return evaluate_hand_impl(hero_hand, board)
```

**Benefits**:
- ✅ Core logic testable without CLI or LLM
- ✅ Same code for CLI and agent
- ✅ Rich formatting separate from logic
- ✅ Easy to maintain

---

## Development Phases

### Phase 1: Core Tools (Standalone CLI Modes)

**Week 1-2: Hand Evaluator**
- Integrate treys for hand evaluation
- Implement Monte Carlo equity calculator
- Build beautiful CLI output with Rich
- Add card symbols (♠♥♦♣) and color coding

**Week 2-3: Range Tools**
- Create GTO preflop charts (JSON data)
- Implement range parser
- Build 13×13 ASCII visualizer with colors
- Range comparison tool

**Week 3-4: Database & Session Tracker**
- SQLAlchemy models (sessions table)
- Session logging with interactive prompts
- Stats calculation (win rate, hourly, variance)
- ASCII bankroll graphs with Rich

**Week 4-5: Quiz System**
- Question bank (JSON)
- Interactive quiz CLI
- Spaced repetition logic
- Progress tracking with Rich progress bars

**Week 5-6: Hand History**
- Manual hand entry (interactive)
- Tagging and search
- Display hands with Rich tables

### Phase 2: LangChain Integration

**Week 6-7: Convert to Tools**
- Add `@tool` decorator to all functions
- Write tool descriptions for LLM
- Test tool calling in isolation

### Phase 3: AI Agent

**Week 7-8: Agent Implementation**
- Set up LangChain agent with Claude
- Create poker coach system prompt
- Build interactive chat loop with Rich
- Add conversation history

**Week 8-9: Polish**
- Prompt engineering for better responses
- Token counting and cost tracking
- Error handling
- Help system and documentation

---

## Rich CLI Features

### Visual Elements to Implement

1. **Card Symbols**: Convert "As Kh" → "A♠ K♥"
2. **Color Coding**:
   - Green: Winning/strong hands
   - Yellow: Medium strength
   - Red: Losing/weak hands
   - Cyan: Headers and titles
   - Dim: Secondary information

3. **Tables**: Session history, quiz results, hand lists
4. **Panels**: Highlighted information (hand eval results, agent responses)
5. **Progress Bars**: Quiz progress, equity calculation, bankroll growth
6. **Charts**: ASCII bankroll graphs, win rate trends
7. **Syntax Highlighting**: Hand histories, ranges
8. **Interactive Prompts**: Session logging, hand entry, quiz questions

---

## Success Criteria

### Phase 1 (TUI Application) ✅ COMPLETE
- ✅ All 7 modes work beautifully in TUI
- ✅ Textual/Rich formatting on all output
- ✅ Interactive prompts are smooth
- ✅ Database tracks all user data (sessions, quizzes, hands)
- ✅ Admin dashboard for raw data management
- ✅ 415+ tests passing with comprehensive coverage

### Phase 2 (Agent Integration) ✅ COMPLETE
- ✅ All modes converted to LangChain tools (15 tools)
- ✅ Agent uses tools autonomously
- ✅ Agent provides personalized coaching based on user data
- ✅ Beautiful chat interface with Textual TUI
- ✅ Token/cost tracking works

---

## Key Decisions

### Why Rich?
- Beautiful terminal output (colors, tables, panels)
- Progress bars and spinners
- Syntax highlighting
- Cross-platform (works on Windows/Mac/Linux)
- Makes CLI feel like a polished app

### Why LangChain?
- Industry standard for agents
- Simple tool decorator
- Built-in Claude support
- Can migrate to MCP later if needed

### Why SQLite?
- Zero setup (single file database)
- Perfect for single-user CLI
- Fast for local queries
- Can migrate to PostgreSQL later if needed

### Why Standalone Modes?
- Each mode is useful on its own
- Easier to test and debug
- Users can use app without agent (free tier)
- Agent enhances but doesn't replace

---

## Development Principles

1. **Rich First**: Every output should look professional
2. **Build Tools First**: Each mode works standalone before becoming agent tool
3. **Test Everything**: 100% coverage on poker logic
4. **Minimize LLM**: Do calculations locally, LLM for synthesis only
5. **Data-Driven Agent**: Powered by user's actual data, not generic advice

---

## Next Steps

### ✅ Phase 1 Complete
1. ✅ Dependencies installed (uv)
2. ✅ Project structure created
3. ✅ Mode 1: Hand Evaluator & Spot Analyzer (core + TUI)
4. ✅ Mode 2: Range Tools (core + TUI)
5. ✅ Mode 3: Quiz System (core + TUI + database)
6. ✅ Mode 4: Session Tracker (core + TUI + database)
7. ✅ Mode 5: Hand History Manager (core + TUI + database)
8. ✅ Mode 6: AI Agent Coach (agent + TUI)
9. ✅ Mode 7: Admin Dashboard (TUI + database admin functions)
10. ✅ Convert modes to LangChain tools (17 tools)
11. ✅ Integrate LangChain agent with Claude

### ⏳ Future Enhancements
- Range-based equity calculator (equity vs opponent ranges)
- Mixed frequency hands with hover tooltips showing percentages
- Spaced repetition algorithm for quiz system
- Hand history import/export (PokerStars, GGPoker formats)

---

**This charter is the source of truth for the project. All implementation decisions should align with this TUI-focused architecture.**
