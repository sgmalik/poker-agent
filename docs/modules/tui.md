# TUI Module Documentation

## Overview

The TUI (Text User Interface) module (`src/tui/`) implements the terminal-based user interface using the Textual framework. It provides an interactive, keyboard-driven interface for all seven application modes.

---

## Module Structure

```
src/tui/
├── __init__.py                # Module initialization
├── app.py                     # Main application and welcome screen
└── screens/                   # Individual mode screens
    ├── __init__.py           # Screen exports
    ├── mode1_input.py        # Hand Evaluator input
    ├── mode1_comprehensive.py # Hand Evaluator results
    ├── mode2_input.py        # Range Tools input
    ├── mode2_matrix.py       # Range matrix display
    ├── mode3_setup.py        # Quiz setup
    ├── mode3_quiz.py         # Active quiz
    ├── mode3_results.py      # Quiz results
    ├── mode4_menu.py         # Session Tracker menu
    ├── mode4_entry.py        # Session entry form
    ├── mode4_history.py      # Session history table
    ├── mode4_stats.py        # Session statistics
    ├── mode4_detail.py       # Session detail view
    ├── mode5_menu.py         # Hand History menu
    ├── mode5_entry.py        # Hand entry form
    ├── mode5_history.py      # Hand history table
    ├── mode5_detail.py       # Hand detail view
    ├── mode6_chat.py         # AI Coach chat interface
    ├── mode7_admin.py        # Admin database viewer
    └── mode7_detail.py       # Admin record detail
```

---

## Library Reference: Textual

### Overview

**Documentation:** https://textual.textualize.io/

**Installation:**
```bash
pip install textual
```

**Key Concepts:**
- **App** - Main application container
- **Screen** - Full-screen view (can be pushed/popped)
- **Widget** - UI component (Button, Input, Static, etc.)
- **Container** - Layout container for widgets
- **CSS** - Textual CSS for styling
- **Binding** - Keyboard shortcuts

---

### Core Imports

```python
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Button,
    Input,
    Static,
    Label,
    Select,
    DataTable,
    TextArea,
    ProgressBar,
    LoadingIndicator,
)
from textual.binding import Binding
from textual.worker import Worker, WorkerState
```

---

### Class: `App`

Main application class that manages screens and global state.

**Documentation:** https://textual.textualize.io/api/app/

**Key Methods:**
| Method | Description |
|--------|-------------|
| `compose()` | Yield widgets to create UI |
| `push_screen(screen)` | Navigate to a new screen |
| `pop_screen()` | Return to previous screen |
| `switch_screen(screen)` | Replace current screen |
| `exit()` | Close the application |
| `run()` | Start the application |

**Class Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `CSS` | `str` | Embedded CSS styles |
| `BINDINGS` | `List[Binding]` | Global keyboard shortcuts |
| `TITLE` | `str` | Application title |
| `SUB_TITLE` | `str` | Application subtitle |

---

### Class: `Screen`

Full-screen view that can be pushed onto the screen stack.

**Documentation:** https://textual.textualize.io/api/screen/

**Key Methods:**
| Method | Description |
|--------|-------------|
| `compose()` | Yield widgets for this screen |
| `on_mount()` | Called when screen is mounted |
| `on_screen_resume()` | Called when returning to this screen |
| `notify(message, severity)` | Show a notification toast |
| `query_one(selector, widget_type)` | Find single widget |
| `query(selector)` | Find multiple widgets |

**Lifecycle:**
1. `__init__()` - Constructor
2. `compose()` - Create widgets
3. `on_mount()` - Screen ready
4. (User interaction)
5. `on_screen_resume()` - When returning

---

### Class: `Binding`

Defines keyboard shortcuts.

**Documentation:** https://textual.textualize.io/api/binding/

**Constructor:**
```python
Binding(key: str, action: str, description: str, show: bool = True)
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | Key combination (e.g., "ctrl+s", "escape") |
| `action` | `str` | Action method name (without "action_" prefix) |
| `description` | `str` | Description shown in footer |
| `show` | `bool` | Whether to show in footer |

**Example:**
```python
BINDINGS = [
    Binding("escape", "back", "Back", show=True),
    Binding("ctrl+a", "analyze", "Analyze", show=True),
    Binding("q", "quit", "Quit", show=True),
]

def action_back(self) -> None:
    """Handle escape key."""
    self.app.pop_screen()
```

---

### Widget: `Static`

Displays static or dynamic text with Rich markup.

**Documentation:** https://textual.textualize.io/widgets/static/

```python
Static(content: str, id: str = None, classes: str = None)
```

**Methods:**
| Method | Description |
|--------|-------------|
| `update(content)` | Change displayed text |

**Rich Markup:**
```python
Static("[bold cyan]Title[/bold cyan]")
Static("[green]Success[/green]")
Static("[dim]Muted text[/dim]")
```

---

### Widget: `Button`

Clickable button with variants.

**Documentation:** https://textual.textualize.io/widgets/button/

```python
Button(label: str, id: str = None, variant: str = "default")
```

**Variants:**
- `"default"` - Standard button
- `"primary"` - Primary action (blue)
- `"success"` - Success (green)
- `"warning"` - Warning (yellow)
- `"error"` - Error/danger (red)

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `label` | `str` | Button text |
| `disabled` | `bool` | Disable interaction |
| `display` | `bool` | Visibility |

**Event Handling:**
```python
def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "submit":
        self.handle_submit()
```

---

### Widget: `Input`

Text input field.

**Documentation:** https://textual.textualize.io/widgets/input/

```python
Input(placeholder: str = "", id: str = None)
```

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `value` | `str` | Current input text |
| `placeholder` | `str` | Placeholder text |
| `disabled` | `bool` | Disable interaction |

**Events:**
```python
def on_input_submitted(self, event: Input.Submitted) -> None:
    """Handle Enter key in input."""
    if event.input.id == "user-input":
        self.process_input(event.value)
```

---

### Widget: `Select`

Dropdown selection widget.

**Documentation:** https://textual.textualize.io/widgets/select/

```python
Select(options: List[Tuple[str, str]], id: str = None, value: str = None)
```

**Parameters:**
- `options` - List of (display_text, value) tuples
- `value` - Initial selected value

**Events:**
```python
def on_select_changed(self, event: Select.Changed) -> None:
    if event.select.id == "topic_select":
        self.selected_topic = str(event.value)
```

---

### Widget: `DataTable`

Tabular data display with selection.

**Documentation:** https://textual.textualize.io/widgets/data_table/

```python
DataTable(id: str = None, zebra_stripes: bool = False, cursor_type: str = "cell")
```

**Methods:**
| Method | Description |
|--------|-------------|
| `add_column(label, key, width)` | Add a column |
| `add_row(*values, key)` | Add a row |
| `clear()` | Clear all rows |
| `remove_row(key)` | Remove specific row |

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `cursor_row` | `int` | Current row index |
| `rows` | `Dict` | Row data by key |

**Events:**
```python
def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    """Handle row double-click or Enter."""
    self.view_detail(event.row_key)
```

---

### Widget: `TextArea`

Multi-line text input.

**Documentation:** https://textual.textualize.io/widgets/text_area/

```python
TextArea(text: str = "", id: str = None)
```

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `text` | `str` | Full text content |

---

### Containers

**Documentation:** https://textual.textualize.io/widgets/containers/

```python
# Vertical layout (default)
Container()

# Horizontal layout
Horizontal()

# Vertical with scrolling
VerticalScroll()
```

**Context Manager Usage:**
```python
with Container(id="main"):
    with Horizontal(classes="row"):
        yield Label("Name:")
        yield Input(id="name_input")
    with Horizontal(classes="row"):
        yield Label("Email:")
        yield Input(id="email_input")
```

---

### Workers (Async)

For running async operations without blocking UI.

**Documentation:** https://textual.textualize.io/guide/workers/

```python
from textual.worker import Worker, WorkerState

# Start a worker
self.run_worker(
    self.async_operation(),
    name="my_worker",
    exclusive=True,  # Cancel previous workers
)

# Handle completion
def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
    if event.worker.name == "my_worker":
        if event.state == WorkerState.SUCCESS:
            result = event.worker.result
            # Handle success
        elif event.state == WorkerState.ERROR:
            # Handle error
```

---

## File: app.py

### Purpose
Defines the main application class and welcome screen.

### Class: `WelcomeScreen`

Static widget displaying the main menu.

```python
class WelcomeScreen(Static):
    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]🃏 Poker Coach[/bold cyan]", id="title")
        yield Button("Hand Evaluator & Spot Analyzer", id="mode_1", variant="primary")
        yield Button("Range Tools", id="mode_2")
        # ... more buttons
```

### Class: `PokerCoachApp`

Main Textual application.

```python
class PokerCoachApp(App):
    TITLE = "Poker Coach"
    SUB_TITLE = "Your personal poker study companion"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("1", "mode_1", "Hand Eval", show=True),
        # ... number keys 2-7 for modes
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(WelcomeScreen())
        yield Footer()

    def action_mode_1(self) -> None:
        self.push_screen(Mode1InputScreen())
```

### Function: `run_app()`

Entry point to start the application.

```python
def run_app():
    app = PokerCoachApp()
    app.run()
```

---

## Screen Patterns

### Input Screen Pattern

Used for: Mode 1, Mode 2, Mode 4 Entry, Mode 5 Entry

```python
class InputScreen(Screen):
    CSS = """..."""

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+s", "submit", "Submit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.data = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="form"):
            # Input fields
            with Horizontal(classes="row"):
                yield Label("Field:")
                yield Input(id="field_input")
            # Buttons
            with Horizontal(classes="buttons"):
                yield Button("Submit", id="submit", variant="primary")
                yield Button("Back", id="back")
        yield Footer()

    def _collect_inputs(self) -> bool:
        """Validate and collect inputs."""
        try:
            self.data["field"] = self.query_one("#field_input", Input).value
            return True
        except Exception:
            self.notify("Invalid input", severity="error")
            return False

    def action_submit(self) -> None:
        if self._collect_inputs():
            self.app.push_screen(ResultScreen(self.data))
```

### List/Table Screen Pattern

Used for: Mode 4 History, Mode 5 History, Mode 7 Admin

```python
class ListScreen(Screen):
    CSS = """..."""

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("d", "delete", "Delete", show=True),
        Binding("enter", "view_detail", "View", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.items: List[Dict] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="list_container"):
            # Filters
            with Horizontal(id="filter_row"):
                yield Select(options, id="filter_select")
            # Table
            yield DataTable(id="table", zebra_stripes=True, cursor_type="row")
            # Summary
            with Horizontal(id="summary_row"):
                yield Static("", id="summary_count")
        yield Footer()

    def on_mount(self) -> None:
        # Setup columns
        table = self.query_one("#table", DataTable)
        table.add_column("Date", key="date", width=12)
        table.add_column("Amount", key="amount", width=10)
        self._load_data()

    def _load_data(self) -> None:
        self.items = get_items_from_database()
        self._populate_table()

    def _populate_table(self) -> None:
        table = self.query_one("#table", DataTable)
        table.clear()
        for item in self.items:
            table.add_row(
                item["date"],
                item["amount"],
                key=str(item["id"]),
            )

    def action_view_detail(self) -> None:
        table = self.query_one("#table", DataTable)
        if table.cursor_row is not None:
            row_keys = list(table.rows.keys())
            item_id = int(str(row_keys[table.cursor_row].value))
            self.app.push_screen(DetailScreen(item_id))
```

### Quiz Screen Pattern

Special pattern for interactive quizzes.

```python
class QuizScreen(Screen):
    BINDINGS = [
        Binding("a", "select_a", "A", show=False),
        Binding("b", "select_b", "B", show=False),
        Binding("enter", "next_or_submit", "Next", show=False),
    ]

    def __init__(self, topic: str, count: int) -> None:
        super().__init__()
        self.engine = QuizEngine()
        self.answered = False

    def on_mount(self) -> None:
        self.engine.load_questions(topic=self.topic, limit=self.count)
        self._display_question()

    def _display_question(self) -> None:
        question = self.engine.get_current_question()
        # Update question text and options
        self._update_ui(question)

    def _submit_answer(self, answer: str) -> None:
        if self.answered:
            return
        self.answered = True
        result = self.engine.submit_answer(answer)
        self._show_feedback(result)

    def _next_question(self) -> None:
        self.answered = False
        self.engine.next_question()
        if self.engine.is_complete():
            self._show_results()
        else:
            self._display_question()
```

### Chat Screen Pattern

For AI agent interaction with async workers.

```python
class ChatScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.agent = PokerCoachAgent()

    def on_mount(self) -> None:
        if self.agent.is_ready:
            self._add_message(self.agent.greeting, "assistant")
        else:
            self._add_message(self.agent.init_error, "error")

    def _add_message(self, content: str, role: str) -> None:
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        scroll.mount(ChatMessage(content, role))
        scroll.scroll_end()

    async def _send_message(self, message: str) -> None:
        self._add_message(message, "user")
        self._set_loading(True)
        self.run_worker(self._chat_worker(message))

    async def _chat_worker(self, message: str) -> AgentResponse:
        return await self.agent.chat(message)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self._set_loading(False)
            response = event.worker.result
            self._add_message(response.content, "assistant")
```

---

## CSS Styling

### Textual CSS Reference

**Documentation:** https://textual.textualize.io/guide/CSS/

### Common Patterns

```css
/* Center content */
MyScreen {
    align: center middle;
}

/* Container with border */
#container {
    width: 80;
    height: auto;
    border: solid $primary;
    background: $surface;
    padding: 2;
}

/* Title styling */
#title {
    text-align: center;
    color: $accent;
    text-style: bold;
}

/* Input row layout */
.input_row {
    height: auto;
    margin-bottom: 1;
}

.input_row Label {
    width: 20;
}

.input_row Input {
    width: 1fr;
}

/* Button row */
.button_row {
    height: 3;
    align: center middle;
}

.button_row Button {
    margin: 0 1;
}

/* Hidden element */
.hidden {
    display: none;
}

/* Show hidden element */
.hidden.show {
    display: block;
}
```

### CSS Variables

| Variable | Description |
|----------|-------------|
| `$primary` | Primary color |
| `$secondary` | Secondary color |
| `$accent` | Accent color |
| `$surface` | Background surface |
| `$success` | Success/green |
| `$error` | Error/red |
| `$warning` | Warning/yellow |
| `$text` | Text color |
| `$text-muted` | Muted text |

---

## Screen Summary

### Mode 1: Hand Evaluator

| Screen | Purpose |
|--------|---------|
| `Mode1InputScreen` | Input hero hand, board, optional pot info |
| `Mode1ComprehensiveScreen` | Display analysis results |

### Mode 2: Range Tools

| Screen | Purpose |
|--------|---------|
| `Mode2InputScreen` | Select position and action |
| `Mode2MatrixScreen` | Display 13x13 range matrix |

### Mode 3: Quiz

| Screen | Purpose |
|--------|---------|
| `Mode3SetupScreen` | Configure topic, difficulty, count |
| `Mode3QuizScreen` | Interactive quiz questions |
| `Mode3ResultsScreen` | Show final results |

### Mode 4: Session Tracker

| Screen | Purpose |
|--------|---------|
| `Mode4MenuScreen` | Menu with options |
| `Mode4EntryScreen` | Log new session |
| `Mode4HistoryScreen` | View session table |
| `Mode4StatsScreen` | View statistics |
| `Mode4DetailScreen` | View session details |

### Mode 5: Hand History

| Screen | Purpose |
|--------|---------|
| `Mode5MenuScreen` | Menu with options |
| `Mode5EntryScreen` | Log new hand |
| `Mode5HistoryScreen` | View hands table |
| `Mode5DetailScreen` | View hand details |

### Mode 6: AI Coach

| Screen | Purpose |
|--------|---------|
| `Mode6ChatScreen` | Chat interface with AI agent |

### Mode 7: Admin

| Screen | Purpose |
|--------|---------|
| `Mode7AdminScreen` | Dynamic database table viewer |
| `Mode7DetailScreen` | Dynamic record detail viewer |

---

## Navigation Flow

```
PokerCoachApp (Welcome)
├── Mode 1: Hand Eval
│   ├── Mode1InputScreen
│   └── Mode1ComprehensiveScreen
├── Mode 2: Ranges
│   ├── Mode2InputScreen
│   └── Mode2MatrixScreen
├── Mode 3: Quiz
│   ├── Mode3SetupScreen
│   ├── Mode3QuizScreen
│   └── Mode3ResultsScreen
├── Mode 4: Sessions
│   ├── Mode4MenuScreen
│   ├── Mode4EntryScreen
│   ├── Mode4HistoryScreen
│   │   └── Mode4DetailScreen
│   └── Mode4StatsScreen
├── Mode 5: Hands
│   ├── Mode5MenuScreen
│   ├── Mode5EntryScreen
│   └── Mode5HistoryScreen
│       └── Mode5DetailScreen
├── Mode 6: AI Coach
│   └── Mode6ChatScreen
└── Mode 7: Admin
    └── Mode7AdminScreen
        └── Mode7DetailScreen
```

---

## Common Operations

### Push Screen (Navigate Forward)
```python
self.app.push_screen(NewScreen(param="value"))
```

### Pop Screen (Navigate Back)
```python
self.app.pop_screen()
```

### Switch Screen (Replace Current)
```python
self.app.switch_screen(NewScreen())
```

### Show Notification
```python
self.notify("Success!", severity="information")
self.notify("Warning!", severity="warning")
self.notify("Error!", severity="error")
```

### Query Widgets
```python
# Single widget by ID
input_widget = self.query_one("#my_input", Input)

# Single widget by class
button = self.query_one(".submit_btn", Button)

# Multiple widgets
all_inputs = self.query(Input)
```

### Update Widget
```python
static_widget = self.query_one("#status", Static)
static_widget.update("[green]Complete![/green]")
```

### Toggle Classes
```python
# Add class
widget.add_class("active")

# Remove class
widget.remove_class("active")

# Toggle
widget.toggle_class("active")

# Check class
if widget.has_class("active"):
    ...
```

---

## Entry Point

```python
# src/__main__.py
from src.tui.app import run_app

if __name__ == "__main__":
    run_app()
```

**Running the Application:**
```bash
# With uv
uv run python -m src

# Direct
python -m src
```
