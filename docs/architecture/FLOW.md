# Mode-by-Mode Flow Documentation

This document details how files and functions interact across each application mode.

---

## Table of Contents
1. [Application Startup](#application-startup)
2. [Mode 1: Hand Evaluator](#mode-1-hand-evaluator)
3. [Mode 2: Range Tools](#mode-2-range-tools)
4. [Mode 3: Quiz System](#mode-3-quiz-system)
5. [Mode 4: Session Tracker](#mode-4-session-tracker)
6. [Mode 5: Hand History](#mode-5-hand-history)
7. [Mode 6: AI Coach](#mode-6-ai-coach)
8. [Mode 7: Admin Dashboard](#mode-7-admin-dashboard)

---

## Application Startup

### Entry Point Flow

```
src/__main__.py
    │
    ├── Imports src.tui.app.PokerCoachApp
    │
    └── Calls app.run()
            │
            ▼
src/tui/app.py :: PokerCoachApp
    │
    ├── on_mount()
    │   └── Initializes database via src/database/db.py::init_db()
    │
    └── compose()
        └── Creates main menu with mode buttons (1-7)
```

### Database Initialization

```
src/database/db.py :: init_db()
    │
    ├── Creates SQLite engine (data/poker_coach.db)
    │
    ├── Imports all models from src/database/models.py
    │   ├── PokerSession
    │   ├── QuizAttempt
    │   ├── QuizSession
    │   └── HandHistory
    │
    └── Calls Base.metadata.create_all(engine)
        └── Creates tables if they don't exist
```

---

## Mode 1: Hand Evaluator

### User Flow
```
User enters hand (e.g., "As Kh") and board (e.g., "Qh Jh 2c")
    │
    ▼
Input Screen validates and forwards to Comprehensive Analysis
    │
    ▼
Results displayed with hand ranking, equity, outs, recommendations
```

### File Interaction Flow

```
src/tui/screens/mode1_input.py :: Mode1InputScreen
    │
    ├── User Input: hero_hand, villain_hand, board
    │
    ├── Validation via:
    │   └── src/core/hand_evaluator.py :: validate_cards()
    │
    └── On Submit → push_screen(Mode1ComprehensiveScreen)
            │
            ▼
src/tui/screens/mode1_comprehensive.py :: Mode1ComprehensiveScreen
    │
    ├── Hand Evaluation:
    │   └── src/core/hand_evaluator.py :: evaluate_hand(hero_hand, board)
    │       │
    │       └── Uses treys library:
    │           ├── Card.new(card_str) - Parse card strings
    │           ├── Evaluator() - Create evaluator
    │           └── evaluator.evaluate(board, hand) - Get hand rank
    │
    ├── Equity Calculation:
    │   └── src/core/hand_evaluator.py :: calculate_equity(hero, villain, board)
    │       │
    │       └── Monte Carlo simulation using treys
    │           ├── Generate remaining deck
    │           ├── Run N simulations
    │           └── Return win/tie/lose percentages
    │
    ├── Spot Analysis:
    │   └── src/core/spot_analyzer.py :: analyze_spot(hero, board, position, ...)
    │       │
    │       ├── Calls evaluate_hand() for hand strength
    │       ├── Calls calculate_outs() for drawing potential
    │       ├── Calls calculate_pot_odds() for math
    │       └── Returns SpotAnalysis with recommendation
    │
    └── Outs Calculation:
        └── src/core/outs_calculator.py :: calculate_outs(hero, board)
            │
            └── Identifies draws:
                ├── Flush draws (4 to flush)
                ├── Straight draws (OESD, gutshot)
                ├── Overcards
                └── Returns OutsResult with outs and odds
```

### Key Functions

| File | Function | Purpose | Returns |
|------|----------|---------|---------|
| `hand_evaluator.py` | `evaluate_hand(hero, board)` | Evaluate 5-7 card hand | `HandResult(rank, name, description)` |
| `hand_evaluator.py` | `calculate_equity(hero, villain, board)` | Monte Carlo equity | `EquityResult(win%, tie%, lose%)` |
| `spot_analyzer.py` | `analyze_spot(...)` | Full situation analysis | `SpotAnalysis(strength, equity, outs, recommendation)` |
| `outs_calculator.py` | `calculate_outs(hero, board)` | Count drawing outs | `OutsResult(outs, draws, odds)` |
| `poker_math.py` | `calculate_pot_odds(pot, bet)` | Pot odds math | `float` (percentage) |

---

## Mode 2: Range Tools

### User Flow
```
User selects position and action (e.g., "BTN" + "open")
    │
    ▼
System retrieves GTO range for that situation
    │
    ▼
Range matrix displayed with colored hand categories
```

### File Interaction Flow

```
src/tui/screens/mode2_input.py :: Mode2InputScreen
    │
    ├── User selects: position, action
    │
    ├── Fetches available actions:
    │   └── src/core/gto_charts.py :: GTOCharts.get_actions(position)
    │
    └── On Submit → push_screen(Mode2MatrixScreen)
            │
            ▼
src/tui/screens/mode2_matrix.py :: Mode2MatrixScreen
    │
    ├── Get Range:
    │   └── src/core/gto_charts.py :: GTOCharts.get_range(position, action)
    │       │
    │       └── Returns set of hand strings: {"AA", "KK", "AKs", ...}
    │
    ├── Convert to Matrix:
    │   └── src/core/gto_charts.py :: GTOCharts.hands_to_matrix(hands)
    │       │
    │       └── Returns 13x13 boolean matrix
    │           ├── Rows: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2
    │           ├── Cols: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2
    │           ├── Upper triangle: suited hands
    │           ├── Diagonal: pairs
    │           └── Lower triangle: offsuit hands
    │
    └── Check Individual Hands:
        └── src/core/gto_charts.py :: GTOCharts.is_hand_in_range(hand, position, action)
```

### Key Functions

| File | Function | Purpose | Returns |
|------|----------|---------|---------|
| `gto_charts.py` | `get_positions()` | List valid positions | `List[str]` |
| `gto_charts.py` | `get_actions(position)` | Available actions | `List[str]` |
| `gto_charts.py` | `get_range(position, action)` | Get hand range | `Set[str]` |
| `gto_charts.py` | `hands_to_matrix(hands)` | Convert to 13x13 grid | `List[List[bool]]` |
| `gto_charts.py` | `is_hand_in_range(hand, pos, action)` | Check single hand | `bool` |
| `range_parser.py` | `parse_range(range_str)` | Parse "AA,KK,AKs" | `Set[str]` |
| `range_parser.py` | `expand_range(range_str)` | Expand "TT+" notation | `Set[str]` |

### Range Matrix Layout

```
      A    K    Q    J    T    9    8    7    6    5    4    3    2
   ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
 A │ AA │AKs │AQs │AJs │ATs │A9s │A8s │A7s │A6s │A5s │A4s │A3s │A2s │ ← Suited
   ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
 K │AKo │ KK │KQs │KJs │KTs │K9s │K8s │K7s │K6s │K5s │K4s │K3s │K2s │
   ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
 Q │AQo │KQo │ QQ │QJs │QTs │Q9s │Q8s │Q7s │Q6s │Q5s │Q4s │Q3s │Q2s │
   └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
     ↑                  ↑
   Offsuit            Pairs (diagonal)
```

---

## Mode 3: Quiz System

### User Flow
```
User selects topic and difficulty
    │
    ▼
Quiz engine generates questions
    │
    ▼
User answers questions one by one
    │
    ▼
Results saved to database, statistics shown
```

### File Interaction Flow

```
src/tui/screens/mode3_setup.py :: Mode3SetupScreen
    │
    ├── User selects: topic, difficulty, num_questions
    │
    ├── Get available topics:
    │   └── src/quiz/questions.py :: get_topics()
    │
    └── On Start → push_screen(Mode3QuizScreen)
            │
            ▼
src/tui/screens/mode3_quiz.py :: Mode3QuizScreen
    │
    ├── Initialize Quiz Engine:
    │   └── src/quiz/engine.py :: QuizEngine(topic, difficulty, num_questions)
    │       │
    │       └── Filters questions from QUESTIONS list
    │           └── src/quiz/questions.py :: QUESTIONS (216 questions)
    │
    ├── For each question:
    │   │
    │   ├── Get current question:
    │   │   └── engine.get_current_question()
    │   │
    │   ├── Format for display:
    │   │   └── src/quiz/questions.py :: format_question_display(question)
    │   │
    │   ├── User submits answer
    │   │
    │   └── Check answer:
    │       └── engine.submit_answer(answer)
    │           │
    │           └── Records: time_taken, is_correct
    │
    └── On Complete → push_screen(Mode3ResultsScreen)
            │
            ▼
src/tui/screens/mode3_results.py :: Mode3ResultsScreen
    │
    ├── Get Results:
    │   └── engine.get_results()
    │       └── Returns: score, total, percentage, answers[]
    │
    ├── Save to Database:
    │   └── src/database/service.py :: save_quiz_session(results, topic, difficulty)
    │       │
    │       ├── Creates QuizSession record
    │       │
    │       └── For each answer:
    │           └── save_quiz_attempt(answer)
    │               └── Creates QuizAttempt record
    │
    └── Display statistics and review
```

### Key Functions

| File | Function | Purpose | Returns |
|------|----------|---------|---------|
| `questions.py` | `QUESTIONS` | Question bank constant | `List[Question]` |
| `questions.py` | `get_topics()` | Available topics | `List[str]` |
| `questions.py` | `get_difficulties()` | Available difficulties | `List[str]` |
| `questions.py` | `filter_questions(topic, diff)` | Filter question bank | `List[Question]` |
| `engine.py` | `QuizEngine.__init__(...)` | Create quiz session | `QuizEngine` |
| `engine.py` | `get_current_question()` | Get active question | `Question` |
| `engine.py` | `submit_answer(answer)` | Check and record | `bool` (is_correct) |
| `engine.py` | `get_results()` | Final statistics | `QuizResults` |
| `service.py` | `save_quiz_session(...)` | Persist to DB | `int` (session_id) |

### Question Structure

```python
Question = TypedDict('Question', {
    'id': str,              # e.g., "post_001"
    'topic': str,           # e.g., "postflop"
    'difficulty': str,      # "beginner", "intermediate", "advanced", "elite"
    'scenario': str,        # Situation description
    'question': str,        # The actual question
    'options': List[str],   # ["Fold", "Call", "Raise"]
    'correct': str,         # Correct option
    'explanation': str,     # Why it's correct
    'hero_hand': Optional[str],  # e.g., "As Kh"
    'board': Optional[str],      # e.g., "Qh Jh 2c"
    'position': Optional[str],   # e.g., "BTN"
})
```

---

## Mode 4: Session Tracker

### User Flow
```
User can: Log new session, View history, View statistics
    │
    ├── Log Session: Enter buy-in, cash-out, duration, etc.
    │
    ├── View History: See all sessions in table, click for details
    │
    └── View Stats: Aggregate statistics, profit by stake/location
```

### File Interaction Flow

```
src/tui/screens/mode4_menu.py :: Mode4MenuScreen
    │
    ├── "Log Session" → push_screen(Mode4EntryScreen)
    ├── "View History" → push_screen(Mode4HistoryScreen)
    └── "View Stats" → push_screen(Mode4StatsScreen)

─────────────────────────────────────────────────────────────────

src/tui/screens/mode4_entry.py :: Mode4EntryScreen
    │
    ├── User inputs: date, stake, buy_in, cash_out, duration, notes
    │
    ├── Validation:
    │   └── src/core/session_tracker.py :: validate_session_data(data)
    │
    └── Save:
        └── src/database/service.py :: save_poker_session(data)
            │
            └── Creates PokerSession record
                ├── Calculates profit_loss = cash_out - buy_in
                ├── Calculates hourly_rate if duration provided
                └── Calculates bb_per_hour if stake parsed

─────────────────────────────────────────────────────────────────

src/tui/screens/mode4_history.py :: Mode4HistoryScreen
    │
    ├── Load Sessions:
    │   └── src/database/service.py :: get_poker_sessions(days, stake, limit)
    │
    ├── Display in DataTable
    │
    ├── On Row Select → push_screen(Mode4DetailScreen)
    │
    └── Delete:
        └── src/database/service.py :: delete_poker_session(id)

─────────────────────────────────────────────────────────────────

src/tui/screens/mode4_stats.py :: Mode4StatsScreen
    │
    └── Load Statistics:
        └── src/database/service.py :: get_session_stats(days, stake)
            │
            └── Returns aggregated data:
                ├── total_sessions
                ├── total_profit
                ├── total_hours
                ├── hourly_rate
                ├── win_rate
                ├── by_stake: {stake: {sessions, profit, hours}}
                └── by_location: {location: {sessions, profit}}
```

### Key Functions

| File | Function | Purpose | Returns |
|------|----------|---------|---------|
| `session_tracker.py` | `validate_session_data(data)` | Validate input | `(bool, Optional[str])` |
| `session_tracker.py` | `parse_stake_level(stake)` | Parse "1/2" → bb | `Optional[float]` |
| `service.py` | `save_poker_session(data)` | Create record | `int` (session_id) |
| `service.py` | `get_poker_sessions(...)` | Query sessions | `List[Dict]` |
| `service.py` | `get_poker_session_by_id(id)` | Single session | `Optional[Dict]` |
| `service.py` | `get_session_stats(...)` | Aggregated stats | `Dict` |
| `service.py` | `get_bankroll_data(days)` | Cumulative profit | `Dict` |
| `service.py` | `delete_poker_session(id)` | Remove record | `bool` |

---

## Mode 5: Hand History

### User Flow
```
User can: Log new hand, View history, View hand details
    │
    ├── Log Hand: Enter cards, board, action, result, tags
    │
    ├── View History: See all hands in table, filter by position/result
    │
    └── View Details: Full hand information with formatted cards
```

### File Interaction Flow

```
src/tui/screens/mode5_menu.py :: Mode5MenuScreen
    │
    ├── "Log Hand" → push_screen(Mode5EntryScreen)
    └── "View History" → push_screen(Mode5HistoryScreen)

─────────────────────────────────────────────────────────────────

src/tui/screens/mode5_entry.py :: Mode5EntryScreen
    │
    ├── User inputs: hero_hand, position, board, action, result, tags, notes, hand_text
    │
    ├── Real-time Validation:
    │   └── src/core/hand_history.py :: validate_hand_and_board(hero, board)
    │       │
    │       ├── validate_hero_hand(hero)
    │       │   └── Checks: 2 cards, valid format, no duplicates
    │       │
    │       └── validate_board(board)
    │           └── Checks: 0/3/4/5 cards, valid format
    │
    ├── Card Preview:
    │   └── src/core/hand_history.py :: format_cards(cards)
    │       └── "As Kh" → "A♠ K♥" (with suit symbols)
    │
    ├── Tag Suggestions:
    │   └── src/core/hand_history.py :: suggest_tags(action, hero_hand)
    │       └── Analyzes action text for keywords: "bluff", "value", etc.
    │
    └── Save:
        └── src/database/service.py :: save_hand_history(data)

─────────────────────────────────────────────────────────────────

src/tui/screens/mode5_history.py :: Mode5HistoryScreen
    │
    ├── Load Hands:
    │   └── src/database/service.py :: get_hand_histories(days, result, position, tags)
    │
    ├── Display in DataTable with formatted cards
    │
    └── On Row Select → push_screen(Mode5DetailScreen)

─────────────────────────────────────────────────────────────────

src/tui/screens/mode5_detail.py :: Mode5DetailScreen
    │
    ├── Load Hand:
    │   └── src/database/service.py :: get_hand_history_by_id(id)
    │
    └── Display with:
        └── src/core/hand_history.py :: format_board_by_street(board)
            └── Splits "Qh Jh 2c 5s 9d" into {flop, turn, river}
```

### Key Functions

| File | Function | Purpose | Returns |
|------|----------|---------|---------|
| `hand_history.py` | `validate_hero_hand(hand)` | Check 2 cards valid | `(bool, Optional[str])` |
| `hand_history.py` | `validate_board(board)` | Check 0/3/4/5 cards | `(bool, Optional[str])` |
| `hand_history.py` | `validate_hand_and_board(h, b)` | Combined validation | `(bool, Optional[str])` |
| `hand_history.py` | `format_cards(cards)` | Add suit symbols | `str` |
| `hand_history.py` | `format_board_by_street(board)` | Split by street | `Dict[str, str]` |
| `hand_history.py` | `suggest_tags(action, hand)` | AI tag suggestions | `List[str]` |
| `service.py` | `save_hand_history(data)` | Create record | `int` |
| `service.py` | `get_hand_histories(...)` | Query hands | `List[Dict]` |
| `service.py` | `get_hand_history_by_id(id)` | Single hand | `Optional[Dict]` |

---

## Mode 6: AI Coach

### User Flow
```
User enters chat message
    │
    ▼
AI agent processes with access to all poker tools
    │
    ▼
Response displayed with tool usage shown
```

### File Interaction Flow

```
src/tui/screens/mode6_chat.py :: Mode6ChatScreen
    │
    ├── Initialize Agent:
    │   └── src/agent/coach.py :: PokerCoachAgent()
    │       │
    │       ├── Load API key from config
    │       │   └── src/config.py :: get_anthropic_api_key()
    │       │
    │       ├── Initialize LangChain ChatAnthropic
    │       │
    │       ├── Load all tools:
    │       │   └── src/tools/__init__.py :: get_all_tools()
    │       │       ├── hand_eval_tools (3 tools)
    │       │       ├── range_tools (4 tools)
    │       │       ├── session_tools (4 tools)
    │       │       ├── history_tools (3 tools)
    │       │       └── quiz_tools (3 tools)
    │       │
    │       └── Create agent with tools
    │
    ├── User sends message
    │
    └── Get Response:
        └── agent.chat(message)
            │
            ├── LangChain processes message
            │
            ├── Agent decides which tools to use
            │   │
            │   └── Example: "What's my equity with AA vs KK?"
            │       │
            │       └── Calls: calculate_equity_tool("As Ac", "Ks Kc", "")
            │           │
            │           └── src/tools/hand_eval_tools.py :: calculate_equity(...)
            │               │
            │               └── src/core/hand_evaluator.py :: calculate_equity(...)
            │
            └── Returns AgentResponse(content, tool_calls, usage)
```

### Agent Tool Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PokerCoachAgent                          │
│                  (src/agent/coach.py)                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangChain Agent                           │
│              (ChatAnthropic + Tools)                        │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ hand_eval_tools │ │  range_tools    │ │ session_tools   │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ evaluate_hand   │ │ get_gto_range   │ │ log_session     │
│ calculate_equity│ │ list_ranges     │ │ get_stats       │
│ analyze_spot    │ │ parse_range     │ │ get_sessions    │
└────────┬────────┘ │ check_hand      │ │ get_bankroll    │
         │          └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Logic                             │
│     (hand_evaluator.py, gto_charts.py, service.py, etc.)   │
└─────────────────────────────────────────────────────────────┘
```

### All Available Tools (17 total)

| Category | Tool | Purpose |
|----------|------|---------|
| **Hand Eval** | `evaluate_hand` | Get hand ranking |
| | `calculate_equity` | Monte Carlo equity |
| | `analyze_spot` | Full situation analysis |
| **Ranges** | `get_gto_range` | Get GTO range |
| | `list_available_ranges` | Show positions/actions |
| | `parse_range` | Parse range string |
| | `check_hand_in_range` | Check if hand in range |
| **Sessions** | `log_poker_session` | Record session |
| | `get_session_stats` | Get statistics |
| | `get_recent_sessions` | List sessions |
| | `get_bankroll_progress` | Profit over time |
| **History** | `save_hand` | Log hand history |
| | `search_hands` | Query hand histories |
| | `get_hand_stats` | Hand statistics |
| **Quiz** | `start_quiz` | Begin quiz session |
| | `get_quiz_stats` | Performance stats |
| | `identify_leaks` | Find weak areas |

---

## Mode 7: Admin Dashboard

### User Flow
```
User selects table to view
    │
    ▼
All records displayed with filters
    │
    ▼
User can view details, delete records
```

### File Interaction Flow

```
src/tui/screens/mode7_admin.py :: Mode7AdminScreen
    │
    ├── Configuration:
    │   └── TABLE_CONFIG dict defines:
    │       ├── quiz_attempts: columns, filters
    │       ├── quiz_sessions: columns, filters
    │       ├── poker_sessions: columns, filters
    │       └── hand_histories: columns, filters
    │
    ├── Load Data (based on selected table):
    │   ├── get_quiz_attempts(topic, difficulty, is_correct)
    │   ├── get_quiz_sessions_list(topic, difficulty)
    │   ├── get_poker_sessions(stake_level, days)
    │   └── get_hand_histories(position, result, days)
    │
    ├── Display in DataTable
    │
    ├── On Row Select → push_screen(Mode7DetailScreen)
    │
    └── Delete:
        ├── delete_quiz_attempt(id)
        ├── delete_quiz_session(id)
        ├── delete_poker_session(id)
        └── delete_hand_history(id)

─────────────────────────────────────────────────────────────────

src/tui/screens/mode7_detail.py :: Mode7DetailScreen
    │
    ├── Configuration:
    │   └── DETAIL_CONFIG dict defines:
    │       ├── Fields to display for each table
    │       ├── Field types (text, date, money, etc.)
    │       ├── Fetch function
    │       └── Delete function
    │
    └── Dynamic rendering based on table_type
```

### Key Functions

| File | Function | Purpose | Returns |
|------|----------|---------|---------|
| `service.py` | `get_admin_stats()` | Record counts | `Dict[str, int]` |
| `service.py` | `get_quiz_attempts(...)` | Query attempts | `List[Dict]` |
| `service.py` | `get_quiz_attempt_by_id(id)` | Single attempt | `Optional[Dict]` |
| `service.py` | `get_quiz_sessions_list(...)` | Query sessions | `List[Dict]` |
| `service.py` | `get_quiz_session_by_id(id)` | Single session | `Optional[Dict]` |

---

## Cross-Mode Interactions

### Database Service as Central Hub

All modes interact with the database through `src/database/service.py`:

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Mode 3  │  │ Mode 4  │  │ Mode 5  │  │ Mode 7  │
│  Quiz   │  │Sessions │  │ Hands   │  │ Admin   │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │
     └────────────┴─────┬──────┴────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   service.py          │
            │  (CRUD operations)    │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │     SQLite DB         │
            │  poker_coach.db       │
            └───────────────────────┘
```

### AI Agent Uses All Core Logic

```
┌─────────────────────────────────────────────────┐
│              AI Agent (Mode 6)                   │
└─────────────────────────────────────────────────┘
                        │
         Uses tools that wrap:
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
     ▼                  ▼                  ▼
┌─────────┐      ┌─────────────┐      ┌─────────┐
│ Mode 1  │      │   Mode 2    │      │Mode 3/4 │
│  Logic  │      │   Logic     │      │  Logic  │
│(hand_   │      │(gto_charts) │      │(quiz,   │
│evaluator│      │             │      │sessions)│
└─────────┘      └─────────────┘      └─────────┘
```

---

## Summary

The application follows a clean separation where:

1. **Core logic** (`src/core/`, `src/quiz/`) contains pure business logic
2. **Database layer** (`src/database/`) handles all persistence
3. **TUI screens** (`src/tui/screens/`) orchestrate user interactions
4. **Tools** (`src/tools/`) wrap core logic for AI consumption
5. **Agent** (`src/agent/`) provides AI coaching via LangChain

This architecture allows the same logic to be reused across:
- Terminal UI (current)
- AI agent (current)
- Mobile/Web UI (future)
