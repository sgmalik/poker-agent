# Textual Library Reference

## Overview

**Textual** is a modern Python framework for building sophisticated terminal user interfaces (TUIs). It provides reactive UI components, CSS styling, and async support.

**Official Documentation:** https://textual.textualize.io/

**API Reference:** https://textual.textualize.io/api/

**Installation:**
```bash
pip install textual
```

---

## Core Architecture

### Application Structure

```
App (PokerCoachApp)
├── Screen (Mode1InputScreen)
│   ├── Container
│   │   ├── Widget (Static)
│   │   ├── Widget (Input)
│   │   └── Widget (Button)
│   └── Footer
├── Screen (Mode2InputScreen)
└── ...
```

---

## App Class

**Documentation:** https://textual.textualize.io/api/app/

### Creating an App

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

class MyApp(App):
    """My Textual application."""

    CSS = """
    /* Embedded CSS styles */
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    TITLE = "My App"
    SUB_TITLE = "Application subtitle"

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Footer()
```

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `CSS` | `str` | Embedded CSS stylesheet |
| `CSS_PATH` | `str` | Path to external CSS file |
| `BINDINGS` | `list` | Global keyboard bindings |
| `TITLE` | `str` | Window title |
| `SUB_TITLE` | `str` | Subtitle in header |

### Methods

| Method | Description |
|--------|-------------|
| `compose()` | Yield widgets to build UI |
| `push_screen(screen)` | Navigate to new screen |
| `pop_screen()` | Go back to previous screen |
| `switch_screen(screen)` | Replace current screen |
| `exit(result)` | Close application |
| `run()` | Start the application |
| `run_worker(coro)` | Run async task |
| `notify(message, severity)` | Show notification |

### Running the App

```python
def main():
    app = MyApp()
    app.run()

if __name__ == "__main__":
    main()
```

---

## Screen Class

**Documentation:** https://textual.textualize.io/api/screen/

### Creating a Screen

```python
from textual.screen import Screen
from textual.app import ComposeResult
from textual.binding import Binding

class MyScreen(Screen):
    """A custom screen."""

    CSS = """
    MyScreen {
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Content"),
            Button("Click Me", id="btn"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        pass

    def on_screen_resume(self) -> None:
        """Called when returning to this screen."""
        pass
```

### Screen Lifecycle

1. `__init__()` - Constructor
2. `compose()` - Create widgets
3. `on_mount()` - Screen ready, widgets available
4. (User interaction)
5. `on_screen_resume()` - When popped screen returns here

### Navigation

```python
# Push new screen (can go back)
self.app.push_screen(OtherScreen())

# Pop current screen (go back)
self.app.pop_screen()

# Replace screen (no going back)
self.app.switch_screen(OtherScreen())
```

---

## Widgets

### Header & Footer

```python
from textual.widgets import Header, Footer

yield Header()          # Shows app title
yield Header(show_clock=True)  # With clock

yield Footer()          # Shows key bindings
```

### Static (Text Display)

**Documentation:** https://textual.textualize.io/widgets/static/

```python
from textual.widgets import Static

# Plain text
yield Static("Hello World")

# With Rich markup
yield Static("[bold cyan]Title[/bold cyan]")
yield Static("[green]Success[/green]")
yield Static("[dim]Muted[/dim]")

# With ID for updates
yield Static("Initial", id="status")

# Update later
self.query_one("#status", Static).update("[green]Complete[/green]")
```

### Button

**Documentation:** https://textual.textualize.io/widgets/button/

```python
from textual.widgets import Button

# Basic button
yield Button("Click Me", id="btn")

# With variant
yield Button("Primary", variant="primary")    # Blue
yield Button("Success", variant="success")    # Green
yield Button("Warning", variant="warning")    # Yellow
yield Button("Error", variant="error")        # Red

# Event handling
def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "btn":
        self.handle_click()
```

### Input

**Documentation:** https://textual.textualize.io/widgets/input/

```python
from textual.widgets import Input

# Basic input
yield Input(placeholder="Enter text...", id="name_input")

# Get value
value = self.query_one("#name_input", Input).value

# Handle Enter key
def on_input_submitted(self, event: Input.Submitted) -> None:
    if event.input.id == "name_input":
        self.process(event.value)
```

### Label

```python
from textual.widgets import Label

yield Label("Field Name:")
```

### Select (Dropdown)

**Documentation:** https://textual.textualize.io/widgets/select/

```python
from textual.widgets import Select

# Create with options (display, value) tuples
options = [
    ("Option A", "a"),
    ("Option B", "b"),
    ("Option C", "c"),
]
yield Select(options, id="my_select", value="a")

# Handle change
def on_select_changed(self, event: Select.Changed) -> None:
    if event.select.id == "my_select":
        selected_value = str(event.value)
```

### DataTable

**Documentation:** https://textual.textualize.io/widgets/data_table/

```python
from textual.widgets import DataTable

# Create table
yield DataTable(id="table", zebra_stripes=True, cursor_type="row")

# Setup columns in on_mount
def on_mount(self) -> None:
    table = self.query_one("#table", DataTable)
    table.add_column("Name", key="name", width=20)
    table.add_column("Value", key="value", width=10)

# Add rows
table.add_row("Item 1", "$10", key="row_1")
table.add_row("Item 2", "$20", key="row_2")

# Clear
table.clear()

# Handle selection
def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    row_key = event.row_key
```

### TextArea

**Documentation:** https://textual.textualize.io/widgets/text_area/

```python
from textual.widgets import TextArea

yield TextArea(id="notes", text="")

# Get content
content = self.query_one("#notes", TextArea).text
```

### ProgressBar

**Documentation:** https://textual.textualize.io/widgets/progress_bar/

```python
from textual.widgets import ProgressBar

yield ProgressBar(id="progress", total=100, show_eta=False)

# Update progress
self.query_one("#progress", ProgressBar).progress = 50
```

### LoadingIndicator

```python
from textual.widgets import LoadingIndicator

yield LoadingIndicator(id="loading")
```

---

## Containers

**Documentation:** https://textual.textualize.io/widgets/containers/

```python
from textual.containers import Container, Horizontal, Vertical, VerticalScroll

# Vertical layout (default)
with Container(id="main"):
    yield Static("First")
    yield Static("Second")

# Horizontal layout
with Horizontal(id="row"):
    yield Button("A")
    yield Button("B")

# Scrollable vertical
with VerticalScroll(id="scroll"):
    # Many items...
```

### Grid Layout

```python
from textual.containers import Grid

CSS = """
Grid {
    grid-size: 2 3;  /* 2 columns, 3 rows */
}
"""

with Grid():
    yield Static("1")
    yield Static("2")
    yield Static("3")
    yield Static("4")
```

---

## Bindings

**Documentation:** https://textual.textualize.io/api/binding/

```python
from textual.binding import Binding

BINDINGS = [
    # Basic binding
    Binding("q", "quit", "Quit"),

    # With show control
    Binding("escape", "back", "Back", show=True),
    Binding("ctrl+s", "save", "Save", show=True),

    # Hidden binding (no footer display)
    Binding("a", "select_a", "A", show=False),
]

# Action methods (prefix with action_)
def action_quit(self) -> None:
    self.app.exit()

def action_back(self) -> None:
    self.app.pop_screen()
```

### Key Names

| Key | Binding |
|-----|---------|
| Escape | `"escape"` |
| Enter | `"enter"` |
| Backspace | `"backspace"` |
| Tab | `"tab"` |
| Arrow keys | `"up"`, `"down"`, `"left"`, `"right"` |
| Function keys | `"f1"`, `"f2"`, ... |
| Ctrl combinations | `"ctrl+s"`, `"ctrl+a"`, ... |
| Letters | `"a"`, `"b"`, ... |
| Numbers | `"1"`, `"2"`, ... |

---

## CSS Styling

**Documentation:** https://textual.textualize.io/guide/CSS/

### Inline CSS

```python
class MyScreen(Screen):
    CSS = """
    MyScreen {
        align: center middle;
    }

    #container {
        width: 80;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }

    .title {
        text-style: bold;
        color: $accent;
    }

    Button {
        width: 100%;
        margin: 1;
    }
    """
```

### CSS Properties

| Property | Values | Description |
|----------|--------|-------------|
| `width` | number, `auto`, `1fr` | Width |
| `height` | number, `auto`, `1fr` | Height |
| `min-width` | number | Minimum width |
| `max-width` | number | Maximum width |
| `padding` | number | Inner spacing |
| `margin` | number | Outer spacing |
| `border` | `solid`, `dashed`, `round` | Border style |
| `background` | color | Background color |
| `color` | color | Text color |
| `text-align` | `left`, `center`, `right` | Text alignment |
| `text-style` | `bold`, `italic`, `underline` | Text style |
| `align` | `left`, `center`, `right` + `top`, `middle`, `bottom` | Content alignment |
| `display` | `block`, `none` | Visibility |

### CSS Variables

| Variable | Description |
|----------|-------------|
| `$primary` | Primary accent color |
| `$secondary` | Secondary color |
| `$accent` | Accent color |
| `$surface` | Background surface |
| `$panel` | Panel background |
| `$success` | Success/green |
| `$warning` | Warning/yellow |
| `$error` | Error/red |
| `$text` | Primary text |
| `$text-muted` | Muted text |

### Selectors

```css
/* Type selector */
Button { }

/* ID selector */
#my_id { }

/* Class selector */
.my_class { }

/* Combined */
Button.primary { }
#container Button { }

/* Pseudo-classes */
Button:hover { }
Button:focus { }
Input:focus { }
```

---

## Querying Widgets

```python
# Single widget by ID
widget = self.query_one("#my_id", Button)

# Single widget by type
widget = self.query_one(Input)

# Multiple widgets
widgets = self.query(Button)
widgets = self.query(".my_class")

# With parent context
container = self.query_one("#container")
buttons = container.query(Button)
```

---

## Events

### Button Events

```python
def on_button_pressed(self, event: Button.Pressed) -> None:
    button_id = event.button.id
    if button_id == "submit":
        self.handle_submit()
```

### Input Events

```python
def on_input_submitted(self, event: Input.Submitted) -> None:
    if event.input.id == "search":
        self.search(event.value)

def on_input_changed(self, event: Input.Changed) -> None:
    if event.input.id == "search":
        self.filter(event.value)
```

### Select Events

```python
def on_select_changed(self, event: Select.Changed) -> None:
    if event.select.id == "filter":
        self.apply_filter(str(event.value))
```

### DataTable Events

```python
def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    # Double-click or Enter on row
    self.view_detail(event.row_key)
```

---

## Workers (Async)

**Documentation:** https://textual.textualize.io/guide/workers/

```python
from textual.worker import Worker, WorkerState

# Start async operation
self.run_worker(
    self.async_operation(),
    name="my_worker",
    exclusive=True,  # Cancel previous
)

# Async coroutine
async def async_operation(self) -> str:
    await asyncio.sleep(1)
    return "Result"

# Handle completion
def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
    if event.worker.name != "my_worker":
        return

    if event.state == WorkerState.SUCCESS:
        result = event.worker.result
        self.handle_result(result)

    elif event.state == WorkerState.ERROR:
        self.handle_error(event.worker.error)

    elif event.state == WorkerState.CANCELLED:
        pass
```

### Worker States

| State | Description |
|-------|-------------|
| `PENDING` | Not started |
| `RUNNING` | In progress |
| `SUCCESS` | Completed successfully |
| `ERROR` | Failed with exception |
| `CANCELLED` | Cancelled |

---

## Notifications

```python
# Information (default)
self.notify("Operation complete")

# Warning
self.notify("Please check your input", severity="warning")

# Error
self.notify("Operation failed", severity="error")
```

---

## Widget Manipulation

### Adding/Removing Classes

```python
# Add class
widget.add_class("active")

# Remove class
widget.remove_class("active")

# Toggle class
widget.toggle_class("active")

# Check class
if widget.has_class("active"):
    ...
```

### Visibility

```python
# Hide widget (CSS: display: none)
widget.display = False

# Show widget
widget.display = True
```

### Disable/Enable

```python
# Disable
button.disabled = True
input.disabled = True

# Enable
button.disabled = False
```

### Dynamic Content

```python
# Mount new widget
container = self.query_one("#messages")
container.mount(ChatMessage("Hello"))

# Remove widget
widget.remove()

# Clear children
for child in list(container.children):
    child.remove()
```

---

## Rich Markup

Textual supports Rich markup for text styling:

```python
Static("[bold]Bold text[/bold]")
Static("[italic]Italic text[/italic]")
Static("[red]Red text[/red]")
Static("[green]Green text[/green]")
Static("[cyan]Cyan text[/cyan]")
Static("[bold cyan]Bold cyan[/bold cyan]")
Static("[dim]Muted text[/dim]")
Static("[link=https://example.com]Click here[/link]")
```

**Rich Documentation:** https://rich.readthedocs.io/en/stable/markup.html
