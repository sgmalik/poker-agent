# Poker Coach Agent - Architecture Overview

## Introduction

The Poker Coach Agent is a comprehensive poker study application built with a **three-layer architecture** where every feature exists as:
1. **Core Logic** - Pure Python business logic (no UI dependencies)
2. **TUI Screen** - Interactive terminal interface using Textual
3. **Agent Tool** - LangChain-compatible tools for AI integration

This architecture enables the same logic to be used across terminal UI, AI agent, and future mobile/web interfaces.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.12+ | Core application |
| Package Manager | uv | Fast dependency management |
| TUI Framework | Textual | Terminal user interface |
| Database | SQLite + SQLAlchemy | Data persistence |
| Poker Logic | treys | Hand evaluation |
| AI Agent | LangChain + Anthropic | AI coaching |
| Type Checking | pyright | Static type analysis |
| Formatting | black | Code formatting |
| Linting | ruff | Code linting |
| Testing | pytest | Test framework |

---

## Directory Structure

```
poker-agent/
├── src/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── config.py            # Centralized configuration
│   │
│   ├── core/                # Business logic (no UI)
│   │   ├── __init__.py
│   │   ├── hand_evaluator.py    # Hand evaluation & equity
│   │   ├── spot_analyzer.py     # Situation analysis
│   │   ├── poker_math.py        # Odds & probabilities
│   │   ├── outs_calculator.py   # Drawing odds
│   │   ├── range_parser.py      # Range notation parsing
│   │   ├── gto_charts.py        # GTO preflop charts
│   │   ├── hand_history.py      # Hand history utilities
│   │   └── session_tracker.py   # Session tracking logic
│   │
│   ├── database/            # Data persistence
│   │   ├── __init__.py
│   │   ├── db.py                # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   └── service.py           # CRUD operations
│   │
│   ├── quiz/                # Quiz system
│   │   ├── __init__.py
│   │   ├── questions.py         # Question bank (216 questions)
│   │   └── engine.py            # Quiz session logic
│   │
│   ├── tools/               # LangChain agent tools
│   │   ├── __init__.py
│   │   ├── hand_eval_tools.py   # Hand evaluation tools
│   │   ├── range_tools.py       # Range analysis tools
│   │   ├── session_tools.py     # Session tracking tools
│   │   ├── history_tools.py     # Hand history tools
│   │   └── quiz_tools.py        # Quiz tools
│   │
│   ├── agent/               # AI coaching agent
│   │   ├── __init__.py
│   │   ├── coach.py             # PokerCoachAgent class
│   │   └── prompts.py           # System prompts
│   │
│   └── tui/                 # Terminal UI
│       ├── __init__.py
│       ├── app.py               # Main Textual application
│       └── screens/             # Individual mode screens
│           ├── __init__.py
│           ├── mode1_*.py       # Hand Evaluator screens
│           ├── mode2_*.py       # Range Tools screens
│           ├── mode3_*.py       # Quiz screens
│           ├── mode4_*.py       # Session Tracker screens
│           ├── mode5_*.py       # Hand History screens
│           ├── mode6_*.py       # AI Agent screen
│           └── mode7_*.py       # Admin screens
│
├── tests/                   # Test suite (415+ tests)
│   ├── core/
│   ├── database/
│   ├── quiz/
│   ├── tools/
│   └── agent/
│
├── data/                    # Runtime data
│   └── poker_coach.db           # SQLite database
│
├── docs/                    # Documentation
│   ├── architecture/
│   ├── modules/
│   └── libraries/
│
└── .claude/                 # Claude Code configuration
    ├── context.md
    ├── guidelines.md
    └── commands/
```

---

## Application Modes

| Mode | Name | Description | Core Files | TUI Screens | Tools |
|------|------|-------------|------------|-------------|-------|
| 1 | Hand Evaluator | Evaluate hands, calculate equity | `hand_evaluator.py`, `spot_analyzer.py` | `mode1_input.py`, `mode1_comprehensive.py` | `hand_eval_tools.py` |
| 2 | Range Tools | GTO charts, range analysis | `gto_charts.py`, `range_parser.py` | `mode2_input.py`, `mode2_matrix.py` | `range_tools.py` |
| 3 | Quiz | Practice questions | `questions.py`, `engine.py` | `mode3_setup.py`, `mode3_quiz.py`, `mode3_results.py` | `quiz_tools.py` |
| 4 | Session Tracker | Track poker sessions | `session_tracker.py` | `mode4_menu.py`, `mode4_entry.py`, `mode4_history.py`, `mode4_stats.py`, `mode4_detail.py` | `session_tools.py` |
| 5 | Hand History | Log and review hands | `hand_history.py` | `mode5_menu.py`, `mode5_entry.py`, `mode5_history.py`, `mode5_detail.py` | `history_tools.py` |
| 6 | AI Coach | Chat with AI coach | `coach.py`, `prompts.py` | `mode6_chat.py` | All tools |
| 7 | Admin | Database viewer | - | `mode7_admin.py`, `mode7_detail.py` | - |

---

## Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│                    (Terminal / Future: Mobile)                       │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           TUI LAYER                                  │
│                         (src/tui/)                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Mode 1  │ │ Mode 2  │ │ Mode 3  │ │ Mode 4  │ │ Mode 5  │ ...   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
└───────┼──────────┼──────────┼──────────┼──────────┼─────────────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CORE LAYER                                  │
│              (src/core/, src/quiz/, src/agent/)                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │hand_evaluator│ │  gto_charts  │ │    engine    │ ...             │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                 │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                                │
│                       (src/database/)                                │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐                   │
│  │  models  │◄───│ service  │◄───│     db       │                   │
│  └──────────┘    └──────────┘    └──────────────┘                   │
│        │                                  │                          │
│        ▼                                  ▼                          │
│  ┌──────────────────────────────────────────────┐                   │
│  │              SQLite Database                  │                   │
│  │           data/poker_coach.db                 │                   │
│  └──────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │    AI AGENT PATH    │
                    └──────────┬──────────┘
                               │
┌─────────────────────────────────────────────────────────────────────┐
│                         TOOLS LAYER                                  │
│                        (src/tools/)                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │hand_eval_tool│ │ range_tools  │ │session_tools │ ...             │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                 │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LANGCHAIN AGENT                                 │
│                     (src/agent/coach.py)                             │
│                              │                                       │
│                              ▼                                       │
│                    ┌──────────────────┐                             │
│                    │   Anthropic API  │                             │
│                    │  (Claude Model)  │                             │
│                    └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

```
┌─────────────────────────┐     ┌─────────────────────────┐
│     poker_sessions      │     │     quiz_sessions       │
├─────────────────────────┤     ├─────────────────────────┤
│ id (PK)                 │     │ id (PK)                 │
│ user_id                 │     │ user_id                 │
│ date                    │     │ topic                   │
│ stake_level             │     │ difficulty              │
│ buy_in                  │     │ total_questions         │
│ cash_out                │     │ questions_attempted     │
│ profit_loss             │     │ correct_answers         │
│ duration_minutes        │     │ time_total              │
│ hands_played            │     │ created_at              │
│ location                │     └─────────────────────────┘
│ game_type               │
│ notes                   │     ┌─────────────────────────┐
│ created_at              │     │     quiz_attempts       │
└─────────────────────────┘     ├─────────────────────────┤
                                │ id (PK)                 │
┌─────────────────────────┐     │ user_id                 │
│     hand_histories      │     │ question_id             │
├─────────────────────────┤     │ scenario                │
│ id (PK)                 │     │ user_answer             │
│ user_id                 │     │ correct_answer          │
│ hero_hand               │     │ is_correct              │
│ board                   │     │ time_taken              │
│ position                │     │ difficulty              │
│ action_summary          │     │ topic                   │
│ result                  │     │ created_at              │
│ stake_level             │     └─────────────────────────┘
│ pot_size                │
│ tags                    │
│ notes                   │
│ hand_text               │
│ created_at              │
└─────────────────────────┘
```

---

## Key Design Principles

### 1. Separation of Concerns
- **Core logic** has no knowledge of UI or database
- **Database layer** is independent of UI
- **TUI screens** only orchestrate, don't contain business logic
- **Tools** wrap core logic for AI agent consumption

### 2. Single Source of Truth
- All poker logic in `src/core/`
- All database operations in `src/database/service.py`
- All configuration in `src/config.py`

### 3. Testability
- Core logic is pure functions where possible
- Database operations can be mocked
- 415+ tests covering all layers

### 4. Extensibility
- New modes follow the same pattern
- New tools automatically available to AI agent
- Database schema can be extended via migrations

---

## Entry Points

### Terminal Application
```bash
uv run python -m src
# or
uv run python src/__main__.py
```

### Running Tests
```bash
uv run pytest tests/ -v
```

### Linting & Formatting
```bash
uv run black src/
uv run ruff check src/
uv run pyright src/
```

---

## Next Steps

For detailed documentation on each component, see:
- [Flow Documentation](./FLOW.md) - Mode-by-mode interaction flows
- [Core Module](../modules/core.md) - Business logic documentation
- [Database Module](../modules/database.md) - Data layer documentation
- [TUI Module](../modules/tui.md) - User interface documentation
- [Library References](../libraries/) - External library usage
