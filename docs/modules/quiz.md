# Quiz Module Documentation

## Overview

The quiz module (`src/quiz/`) provides an interactive poker knowledge assessment system. It manages a question bank with 216 questions across 8 topics and 4 difficulty levels, handling question validation, session management, answer checking, and results tracking.

---

## Module Structure

```
src/quiz/
├── __init__.py       # Module exports
├── questions.py      # Question types, validation, formatting utilities
└── engine.py         # Quiz session management engine
```

---

## File: questions.py

### Purpose
Defines question structure, validation rules, and formatting utilities for quiz questions.

### Constants

#### `TOPICS`
```python
TOPICS: List[str] = [
    "preflop",
    "ranges",
    "pot_odds",
    "hand_strength",
    "position",
    "postflop",
    "game_theory",
    "tournament",
]
```
Valid topic categories for quiz questions.

#### `DIFFICULTIES`
```python
DIFFICULTIES: List[str] = [
    "beginner",
    "intermediate",
    "advanced",
    "elite",
]
```
Valid difficulty levels for questions.

#### `QUESTION_TYPES`
```python
QUESTION_TYPES: List[str] = [
    "preflop_action",
    "range_check",
    "hand_strength",
    "pot_odds",
    "position_open",
    "postflop_action",
    "board_texture_analysis",
    "blocker_logic",
    "sizing_strategy",
    "icm_logic",
    "range_interaction",
    "4bet_theory",
    "equity_realization",
    "mixed_strategies",
    "node_locking",
    "geometric_sizing",
    "uncapped_ranges",
    "protection_betting",
    "indifference_principle",
    "multiway_dynamics",
    "range_merging",
    "solver_logic",
    "postflop_theory",
    "advanced_icm",
    "range_construction",
]
```
Valid question type identifiers (25 types).

#### `REQUIRED_FIELDS`
```python
REQUIRED_FIELDS: Set[str] = {
    "id",
    "type",
    "difficulty",
    "topic",
    "question",
    "options",
    "answer",
    "explanation",
}
```
Required fields that every valid question must contain.

---

### Functions

#### `validate_question(question)`

Validates that a question dictionary has all required fields and valid values.

```python
def validate_question(question: Dict[str, Any]) -> bool:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `Dict[str, Any]` | Question dictionary to validate |

**Returns:**
| Type | Description |
|------|-------------|
| `bool` | `True` if valid, `False` otherwise |

**Validation Rules:**
1. All `REQUIRED_FIELDS` must exist
2. `topic` must be in `TOPICS`
3. `difficulty` must be in `DIFFICULTIES`
4. `type` must be in `QUESTION_TYPES`
5. `options` must be a list with at least 2 items
6. `answer` must be in the `options` list
7. `id` must be a non-empty string

**Example:**
```python
from src.quiz.questions import validate_question

question = {
    "id": "pf_001",
    "type": "preflop_action",
    "difficulty": "beginner",
    "topic": "preflop",
    "question": "You have AKs UTG. What is the standard action?",
    "options": ["Fold", "Limp", "Raise", "All-in"],
    "answer": "Raise",
    "explanation": "AKs is a premium hand that should be raised..."
}

is_valid = validate_question(question)  # True
```

---

#### `check_answer(question, user_answer)`

Checks if the user's answer matches the correct answer.

```python
def check_answer(question: Dict[str, Any], user_answer: str) -> bool:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `Dict[str, Any]` | Question dictionary |
| `user_answer` | `str` | User's submitted answer |

**Returns:**
| Type | Description |
|------|-------------|
| `bool` | `True` if correct, `False` otherwise |

**Notes:**
- Comparison is case-insensitive
- Leading/trailing whitespace is stripped

**Example:**
```python
from src.quiz.questions import check_answer

question = {"answer": "Raise"}
check_answer(question, "raise")  # True
check_answer(question, "RAISE")  # True
check_answer(question, " Raise ")  # True
check_answer(question, "Call")  # False
```

---

#### `format_question_display(question)`

Formats a question for TUI display with rich text markup.

```python
def format_question_display(question: Dict[str, Any]) -> str:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `Dict[str, Any]` | Question dictionary |

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Formatted string with Rich markup |

**Features:**
- Bold question text
- Card notation converted to Unicode suits
- Scenario details (hero hand, position, board) if present
- Color-coded elements (cyan for hands, yellow for position, green for board)

**Example Output:**
```
[bold]You hold As Kh on the button. What is your action?[/bold]

Hand: [cyan]A♠ K♥[/cyan]
Position: [yellow]BTN[/yellow]
Board: [green]Q♠ J♦ T♣[/green]
```

---

#### `format_options(options)`

Formats answer options with letter labels (A, B, C, etc.).

```python
def format_options(options: List[str]) -> List[str]:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `options` | `List[str]` | List of option strings |

**Returns:**
| Type | Description |
|------|-------------|
| `List[str]` | Formatted options with labels |

**Example:**
```python
from src.quiz.questions import format_options

options = ["Fold", "Call", "Raise"]
formatted = format_options(options)
# ["A) Fold", "B) Call", "C) Raise"]
```

---

#### `get_option_from_label(options, label)`

Converts a letter label back to the option text.

```python
def get_option_from_label(options: List[str], label: str) -> str:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `options` | `List[str]` | List of option strings |
| `label` | `str` | Single character label (A-J) |

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Option text, or empty string if invalid |

**Example:**
```python
from src.quiz.questions import get_option_from_label

options = ["Fold", "Call", "Raise"]
get_option_from_label(options, "B")  # "Call"
get_option_from_label(options, "b")  # "Call" (case-insensitive)
get_option_from_label(options, "Z")  # ""
```

---

#### `_format_cards(text)`

Internal function to convert card notation to Unicode suit symbols.

```python
def _format_cards(text: str) -> str:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Text containing card notation |

**Returns:**
| Type | Description |
|------|-------------|
| `str` | Text with Unicode suit symbols |

**Suit Mappings:**
| Input | Unicode | Symbol |
|-------|---------|--------|
| `s` | `\u2660` | ♠ |
| `h` | `\u2665` | ♥ |
| `d` | `\u2666` | ♦ |
| `c` | `\u2663` | ♣ |

**Example:**
```python
_format_cards("As Kh")  # "A♠ K♥"
_format_cards("Qd Jc")  # "Q♦ J♣"
```

---

#### `get_topics()`

Returns a copy of the available topics list.

```python
def get_topics() -> List[str]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `List[str]` | Copy of `TOPICS` list |

---

#### `get_difficulties()`

Returns a copy of the available difficulties list.

```python
def get_difficulties() -> List[str]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `List[str]` | Copy of `DIFFICULTIES` list |

---

#### `filter_questions(questions, topic, difficulty)`

Filters a list of questions by topic and/or difficulty.

```python
def filter_questions(
    questions: List[Dict[str, Any]],
    topic: str | None = None,
    difficulty: str | None = None,
) -> List[Dict[str, Any]]:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `questions` | `List[Dict[str, Any]]` | - | List of question dictionaries |
| `topic` | `str \| None` | `None` | Topic filter (None/"all" for all) |
| `difficulty` | `str \| None` | `None` | Difficulty filter (None/"all" for all) |

**Returns:**
| Type | Description |
|------|-------------|
| `List[Dict[str, Any]]` | Filtered list of questions |

**Example:**
```python
from src.quiz.questions import filter_questions

# Filter by topic only
preflop_qs = filter_questions(all_questions, topic="preflop")

# Filter by difficulty only
beginner_qs = filter_questions(all_questions, difficulty="beginner")

# Filter by both
easy_preflop = filter_questions(all_questions, topic="preflop", difficulty="beginner")

# "all" values are treated as no filter
all_qs = filter_questions(all_questions, topic="all", difficulty="all")
```

---

## File: engine.py

### Purpose
Manages interactive quiz sessions including question loading, answer submission, progress tracking, and results calculation.

### Dependencies
- `json` (Python standard library)
- `random` (Python standard library)
- `datetime` (Python standard library)
- `pathlib.Path` (Python standard library)
- `.questions` (internal module)
- `..config` (for `QUIZ_BANK_FILE`)

---

### Class: QuizEngine

Main quiz session manager that handles the complete lifecycle of a quiz.

```python
class QuizEngine:
    """
    Interactive poker quiz engine.

    Manages quiz sessions including question loading, filtering,
    answer submission, progress tracking, and results.
    """
```

#### Constructor

```python
def __init__(self, bank_file: Optional[Path] = None) -> None:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bank_file` | `Optional[Path]` | `None` | Path to quiz bank JSON. Uses `QUIZ_BANK_FILE` from config if None |

**Instance Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `_bank_file` | `Path` | Path to the question bank JSON file |
| `_all_questions` | `List[Dict[str, Any]]` | All validated questions from bank |
| `_questions` | `List[Dict[str, Any]]` | Questions for current session |
| `_current_idx` | `int` | Current question index (0-based) |
| `_answers` | `List[Dict[str, Any]]` | Recorded answers for session |
| `_start_time` | `Optional[datetime]` | Session start timestamp |
| `_question_start_time` | `Optional[datetime]` | Current question start timestamp |

**Example:**
```python
from src.quiz.engine import QuizEngine

# Use default question bank
engine = QuizEngine()

# Use custom question bank
from pathlib import Path
engine = QuizEngine(bank_file=Path("custom_questions.json"))
```

---

#### Method: `_load_bank()`

Internal method to load and validate questions from the bank file.

```python
def _load_bank(self) -> None:
```

**Raises:**
- `FileNotFoundError`: If the bank file doesn't exist

**Expected JSON Format:**
```json
{
    "questions": [
        {
            "id": "unique_id",
            "type": "preflop_action",
            "difficulty": "beginner",
            "topic": "preflop",
            "question": "Question text",
            "options": ["A", "B", "C", "D"],
            "answer": "A",
            "explanation": "Why A is correct",
            "scenario": {
                "hero_hand": "As Kh",
                "position": "BTN",
                "board": "Qc Jd Th"
            }
        }
    ]
}
```

---

#### Method: `load_questions(topic, difficulty, limit, shuffle)`

Loads and filters questions for a new quiz session.

```python
def load_questions(
    self,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 10,
    shuffle: bool = True,
) -> int:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | `Optional[str]` | `None` | Topic filter (None/"all" for all topics) |
| `difficulty` | `Optional[str]` | `None` | Difficulty filter (None/"all" for all) |
| `limit` | `int` | `10` | Maximum questions to load |
| `shuffle` | `bool` | `True` | Randomize question order |

**Returns:**
| Type | Description |
|------|-------------|
| `int` | Number of questions actually loaded |

**Side Effects:**
- Resets `_current_idx` to 0
- Clears `_answers`
- Sets `_start_time` to current time
- Sets `_question_start_time` to current time

**Example:**
```python
engine = QuizEngine()

# Load 10 random preflop questions
count = engine.load_questions(topic="preflop", limit=10)
print(f"Loaded {count} questions")

# Load all beginner questions in order
count = engine.load_questions(difficulty="beginner", limit=50, shuffle=False)
```

---

#### Method: `get_current_question()`

Returns the current question in the session.

```python
def get_current_question(self) -> Optional[Dict[str, Any]]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `Optional[Dict[str, Any]]` | Current question dict, or `None` if quiz complete/not started |

**Example:**
```python
question = engine.get_current_question()
if question:
    print(question["question"])
    print(question["options"])
```

---

#### Method: `submit_answer(answer)`

Submits an answer for the current question and records the result.

```python
def submit_answer(self, answer: str) -> Dict[str, Any]:
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `answer` | `str` | User's answer string |

**Returns:**
| Type | Description |
|------|-------------|
| `Dict[str, Any]` | Result dictionary |

**Return Dictionary Structure:**
```python
{
    "is_correct": bool,        # Whether answer was correct
    "correct_answer": str,     # The correct answer
    "explanation": str,        # Explanation for the answer
    "time_taken": int,         # Seconds spent on question
}
```

**Side Effects:**
- Appends answer record to `_answers` list with full details

**Example:**
```python
result = engine.submit_answer("Raise")
if result["is_correct"]:
    print("Correct!")
else:
    print(f"Wrong. The answer was: {result['correct_answer']}")
    print(f"Explanation: {result['explanation']}")
print(f"Time: {result['time_taken']} seconds")
```

---

#### Method: `next_question()`

Advances to the next question in the session.

```python
def next_question(self) -> Optional[Dict[str, Any]]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `Optional[Dict[str, Any]]` | Next question dict, or `None` if quiz complete |

**Side Effects:**
- Increments `_current_idx`
- Resets `_question_start_time` to current time

**Example:**
```python
next_q = engine.next_question()
if next_q:
    print(f"Next question: {next_q['question']}")
else:
    print("Quiz complete!")
```

---

#### Method: `get_progress()`

Returns current quiz progress and statistics.

```python
def get_progress(self) -> Dict[str, Any]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `Dict[str, Any]` | Progress dictionary |

**Return Dictionary Structure:**
```python
{
    "current": int,            # 1-indexed question number
    "total": int,              # Total questions in session
    "answered": int,           # Number answered so far
    "correct": int,            # Correct answers count
    "incorrect": int,          # Incorrect answers count
    "percentage": float,       # Score percentage (0-100)
    "by_topic": {              # Breakdown by topic
        "preflop": {"correct": 3, "total": 5},
        "postflop": {"correct": 2, "total": 3},
    }
}
```

**Example:**
```python
progress = engine.get_progress()
print(f"Question {progress['current']} of {progress['total']}")
print(f"Score: {progress['correct']}/{progress['answered']} ({progress['percentage']:.1f}%)")
```

---

#### Method: `is_complete()`

Checks if all questions have been answered.

```python
def is_complete(self) -> bool:
```

**Returns:**
| Type | Description |
|------|-------------|
| `bool` | `True` if quiz is finished |

**Example:**
```python
while not engine.is_complete():
    question = engine.get_current_question()
    # ... get user answer ...
    engine.submit_answer(answer)
    engine.next_question()
```

---

#### Method: `get_results()`

Returns comprehensive final quiz results.

```python
def get_results(self) -> Dict[str, Any]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `Dict[str, Any]` | Results dictionary |

**Return Dictionary Structure:**
```python
{
    "score": int,              # Correct answer count
    "total": int,              # Total questions
    "percentage": float,       # Score percentage (0-100)
    "time_total": int,         # Total seconds for quiz
    "by_topic": {              # Breakdown by topic
        "preflop": {"correct": 3, "total": 5},
    },
    "by_difficulty": {         # Breakdown by difficulty
        "beginner": {"correct": 4, "total": 4},
        "intermediate": {"correct": 2, "total": 3},
    },
    "incorrect_questions": [   # List of wrong answers
        {
            "question": "Question text",
            "your_answer": "Call",
            "correct_answer": "Raise",
            "explanation": "...",
            "topic": "preflop",
        }
    ],
    "answers": [...]           # Full answer records
}
```

**Example:**
```python
results = engine.get_results()
print(f"Final Score: {results['score']}/{results['total']} ({results['percentage']:.1f}%)")
print(f"Total Time: {results['time_total']} seconds")

print("\nBy Topic:")
for topic, stats in results["by_topic"].items():
    print(f"  {topic}: {stats['correct']}/{stats['total']}")

print("\nIncorrect Questions:")
for q in results["incorrect_questions"]:
    print(f"  - {q['question'][:50]}...")
    print(f"    Your answer: {q['your_answer']}")
    print(f"    Correct: {q['correct_answer']}")
```

---

#### Method: `get_available_topics()`

Returns topics that have questions in the loaded bank.

```python
def get_available_topics(self) -> List[str]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `List[str]` | Sorted list of topic names |

**Example:**
```python
topics = engine.get_available_topics()
# ['game_theory', 'hand_strength', 'position', 'postflop', 'pot_odds', 'preflop', 'ranges', 'tournament']
```

---

#### Method: `get_available_difficulties()`

Returns difficulties that have questions in the loaded bank.

```python
def get_available_difficulties(self) -> List[str]:
```

**Returns:**
| Type | Description |
|------|-------------|
| `List[str]` | Sorted list of difficulty names |

**Example:**
```python
difficulties = engine.get_available_difficulties()
# ['advanced', 'beginner', 'elite', 'intermediate']
```

---

#### Method: `get_question_count(topic, difficulty)`

Returns count of questions matching the given filters.

```python
def get_question_count(
    self,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> int:
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | `Optional[str]` | `None` | Topic filter |
| `difficulty` | `Optional[str]` | `None` | Difficulty filter |

**Returns:**
| Type | Description |
|------|-------------|
| `int` | Number of matching questions |

**Example:**
```python
# Count all questions
total = engine.get_question_count()  # 216

# Count preflop questions
preflop_count = engine.get_question_count(topic="preflop")

# Count beginner questions
beginner_count = engine.get_question_count(difficulty="beginner")

# Count beginner preflop questions
easy_preflop = engine.get_question_count(topic="preflop", difficulty="beginner")
```

---

## File: __init__.py

### Purpose
Module initialization that exports the public API.

### Exports

```python
__all__ = [
    "QuizEngine",
    "TOPICS",
    "DIFFICULTIES",
    "QUESTION_TYPES",
    "validate_question",
    "check_answer",
    "format_question_display",
    "format_options",
    "get_option_from_label",
    "get_topics",
    "get_difficulties",
    "filter_questions",
]
```

### Usage

```python
# Import the engine
from src.quiz import QuizEngine

# Import constants
from src.quiz import TOPICS, DIFFICULTIES, QUESTION_TYPES

# Import utility functions
from src.quiz import (
    validate_question,
    check_answer,
    format_question_display,
    format_options,
    get_option_from_label,
    filter_questions,
)
```

---

## Question Bank Format

The quiz engine expects a JSON file with the following structure:

```json
{
    "version": "1.0",
    "questions": [
        {
            "id": "pf_action_001",
            "type": "preflop_action",
            "difficulty": "beginner",
            "topic": "preflop",
            "question": "You are UTG with As Ks. What is the standard action?",
            "options": ["Fold", "Limp", "Raise 2.5BB", "Raise 4BB"],
            "answer": "Raise 2.5BB",
            "explanation": "AKs is a premium hand. The standard open raise size UTG is 2.5BB to build a pot while maintaining positional disadvantage considerations.",
            "scenario": {
                "hero_hand": "As Ks",
                "position": "UTG",
                "stack": "100BB",
                "villain_action": null,
                "board": null
            }
        }
    ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | Yes | Unique identifier for the question |
| `type` | `string` | Yes | Question type (from `QUESTION_TYPES`) |
| `difficulty` | `string` | Yes | Difficulty level (from `DIFFICULTIES`) |
| `topic` | `string` | Yes | Topic category (from `TOPICS`) |
| `question` | `string` | Yes | The question text |
| `options` | `array` | Yes | List of answer options (min 2) |
| `answer` | `string` | Yes | Correct answer (must be in options) |
| `explanation` | `string` | Yes | Explanation of why answer is correct |
| `scenario` | `object` | No | Optional scenario context |

### Scenario Fields

| Field | Type | Description |
|-------|------|-------------|
| `hero_hand` | `string` | Hero's hole cards |
| `position` | `string` | Hero's position |
| `stack` | `string` | Stack size |
| `villain_action` | `string` | Previous villain action |
| `board` | `string` | Community cards |

---

## Complete Usage Example

```python
from src.quiz import QuizEngine, format_question_display, format_options, get_option_from_label

# Initialize engine
engine = QuizEngine()

# Check available content
print(f"Topics: {engine.get_available_topics()}")
print(f"Difficulties: {engine.get_available_difficulties()}")
print(f"Total questions: {engine.get_question_count()}")

# Start a quiz session
num_loaded = engine.load_questions(
    topic="preflop",
    difficulty="beginner",
    limit=5,
    shuffle=True
)
print(f"Starting quiz with {num_loaded} questions")

# Quiz loop
while not engine.is_complete():
    # Get current question
    question = engine.get_current_question()

    # Display formatted question
    print(format_question_display(question))

    # Display formatted options
    for opt in format_options(question["options"]):
        print(f"  {opt}")

    # Get user input (e.g., "B")
    user_input = input("Your answer (A/B/C/D): ").strip()

    # Convert label to option text
    answer = get_option_from_label(question["options"], user_input)

    # Submit answer
    result = engine.submit_answer(answer)

    if result["is_correct"]:
        print("Correct!")
    else:
        print(f"Wrong! The answer was: {result['correct_answer']}")
        print(f"Explanation: {result['explanation']}")

    # Show progress
    progress = engine.get_progress()
    print(f"Score: {progress['correct']}/{progress['answered']}")

    # Move to next question
    engine.next_question()

# Show final results
results = engine.get_results()
print(f"\nFinal Score: {results['score']}/{results['total']} ({results['percentage']:.1f}%)")
print(f"Time: {results['time_total']} seconds")
```

---

## Library References

### Python Standard Library

#### `json` Module
Used for loading the question bank JSON file.

**Documentation:** https://docs.python.org/3/library/json.html

**Functions Used:**
- `json.load(fp)` - Deserialize file to Python object

#### `random` Module
Used for shuffling questions.

**Documentation:** https://docs.python.org/3/library/random.html

**Functions Used:**
- `random.shuffle(x)` - Shuffle list in place

#### `datetime` Module
Used for tracking quiz timing.

**Documentation:** https://docs.python.org/3/library/datetime.html

**Classes Used:**
- `datetime.datetime.now()` - Get current timestamp
- `datetime - datetime` - Calculate time delta

#### `pathlib` Module
Used for file path handling.

**Documentation:** https://docs.python.org/3/library/pathlib.html

**Classes Used:**
- `Path.exists()` - Check if file exists

#### `re` Module
Used for card notation regex replacement.

**Documentation:** https://docs.python.org/3/library/re.html

**Functions Used:**
- `re.sub(pattern, repl, string, flags)` - Replace pattern matches

---

## Integration Points

### TUI Integration (Mode 3)
The quiz module is used by TUI screens:
- `mode3_setup.py` - Quiz configuration (topic, difficulty, count)
- `mode3_quiz.py` - Active quiz display and answer submission
- `mode3_results.py` - Results display

### Database Integration
Quiz results are persisted via:
- `database/service.py` - `save_quiz_session()`, `save_quiz_attempt()`
- `database/models.py` - `QuizSession`, `QuizAttempt` models

### Agent Integration
Quiz tools for AI agent:
- `tools/quiz_tools.py` - LangChain tools wrapping quiz engine
