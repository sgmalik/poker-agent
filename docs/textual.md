# Textual Library Reference

Textual is a Python TUI framework. Apps are built from Screens containing Widgets, styled with CSS.

## App Structure

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

class MyApp(App):
    CSS = """/* Textual CSS here */"""

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("1", "mode_1", "Mode 1", show=True),
    ]

    TITLE = "App Title"
    SUB_TITLE = "Subtitle shown in header"

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield Header()
        yield Static("Hello World")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "my_button":
            self.notify("Clicked!")

    def action_mode_1(self) -> None:
        """Called when binding triggers."""
        self.push_screen(SomeScreen())

# Run
app = MyApp()
app.run()
```

## Screens

Screens are full-page views. Push/pop for navigation.

```python
from textual.screen import Screen

class MyScreen(Screen):
    CSS = """/* Screen-specific CSS */"""

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
    ]

    def __init__(self, data: str) -> None:
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"Data: {self.data}")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()
```

### Navigation

```python
# Push screen (adds to stack)
self.app.push_screen(MyScreen(data="test"))

# Pop screen (go back)
self.app.pop_screen()

# Switch screen (replaces current)
self.app.switch_screen(OtherScreen())

# Exit app
self.app.exit()
```

## Common Widgets

### Static (text display)

```python
from textual.widgets import Static

yield Static("Plain text")
yield Static("[bold cyan]Rich markup[/bold cyan]", id="my_id")
yield Static("", id="dynamic")  # Update later

# Update content
self.query_one("#dynamic", Static).update("New content")
```

### Button

```python
from textual.widgets import Button

yield Button("Click Me", id="btn_1", variant="primary")
yield Button("Cancel", id="btn_2", variant="error")

# Variants: "default", "primary", "success", "warning", "error"
```

### Input

```python
from textual.widgets import Input

yield Input(placeholder="Enter value...", id="my_input")

# Get value
value = self.query_one("#my_input", Input).value
```

### Select (dropdown)

```python
from textual.widgets import Select

options = [("Display Text", "value"), ("Option 2", "opt2")]
yield Select(options, id="my_select", value="value")

# Handle changes
def on_select_changed(self, event: Select.Changed) -> None:
    if event.select.id == "my_select":
        selected = str(event.value)
```

### Label

```python
from textual.widgets import Label
yield Label("Field name:", classes="label")
```

### ProgressBar

```python
from textual.widgets import ProgressBar

yield ProgressBar(id="progress", total=100, show_eta=False)

# Update
self.query_one("#progress", ProgressBar).progress = 50
```

## Containers

Containers organize widgets spatially.

```python
from textual.containers import Container, Horizontal, Vertical, VerticalScroll

# Basic container
with Container(id="main"):
    yield Static("Inside container")

# Horizontal layout
with Horizontal(classes="row"):
    yield Button("Left")
    yield Button("Right")

# Vertical layout
with Vertical():
    yield Static("Top")
    yield Static("Bottom")

# Scrollable
with VerticalScroll(id="scroll_area"):
    for i in range(100):
        yield Static(f"Line {i}")
```

## CSS Styling

Textual CSS is similar to web CSS but with differences.

```python
CSS = """
/* Target by widget type */
Button {
    width: 100%;
    margin: 1;
}

/* Target by ID */
#title {
    text-align: center;
    color: $accent;
    text-style: bold;
}

/* Target by class */
.selected {
    background: $accent;
}

/* Screen-level */
MyScreen {
    align: center middle;
}
"""
```

### Common Properties

| Property | Values | Notes |
|----------|--------|-------|
| `width` | `100%`, `auto`, `80`, `1fr` | Pixels, percent, or fraction |
| `height` | `100%`, `auto`, `20` | |
| `margin` | `1`, `1 2`, `1 2 1 2` | top, right, bottom, left |
| `padding` | `1`, `2 4` | |
| `background` | `$surface`, `red`, `#ff0000` | |
| `color` | `$text`, `$accent`, `green` | Text color |
| `text-align` | `left`, `center`, `right` | |
| `text-style` | `bold`, `italic`, `underline` | |
| `border` | `solid $primary`, `none` | |
| `display` | `block`, `none` | Hide with `none` |
| `align` | `center middle` | Container content alignment |

### Theme Variables

```
$primary, $secondary, $accent
$surface, $surface-darken-1, $surface-lighten-1
$text, $text-muted
$success, $warning, $error
```

## Event Handling

### Button Press

```python
def on_button_pressed(self, event: Button.Pressed) -> None:
    button_id = event.button.id
    if button_id == "submit":
        self.handle_submit()
```

### Key Bindings

```python
BINDINGS = [
    Binding("escape", "back", "Back", show=True),      # Show in footer
    Binding("a", "select_a", "A", show=False),         # Hidden binding
    Binding("ctrl+s", "save", "Save"),
]

def action_back(self) -> None:
    """Method name must be action_{binding_action}."""
    self.app.pop_screen()
```

### Mount (initialization after compose)

```python
def on_mount(self) -> None:
    """Called after widgets are composed."""
    self.load_data()
    self.update_display()
```

## Querying Widgets

```python
# Single widget by ID
button = self.query_one("#my_button", Button)

# Single widget by type
static = self.query_one(Static)

# Multiple widgets by class
for btn in self.query(".option_btn"):
    btn.remove_class("selected")

# Multiple by type
for input_widget in self.query(Input):
    input_widget.value = ""
```

## Widget Methods

```python
# Show/hide
widget.display = True  # or False

# Enable/disable
button.disabled = True

# CSS classes
widget.add_class("selected")
widget.remove_class("selected")
widget.has_class("selected")  # Returns bool

# Update Static content
static.update("[bold]New text[/bold]")
```

## Notifications

```python
self.notify("Operation complete!")
self.notify("Error occurred", severity="error")
self.notify("Warning!", severity="warning")
```

## Rich Markup

Textual uses Rich markup for styled text:

```python
"[bold]Bold text[/bold]"
"[italic]Italic[/italic]"
"[red]Red text[/red]"
"[bold cyan]Bold cyan[/bold cyan]"
"[dim]Dimmed text[/dim]"
"[green]Success[/green] and [red]error[/red]"
```

## Lifecycle

1. `__init__()` - Store data, don't create widgets
2. `compose()` - Yield widgets (called once)
3. `on_mount()` - Post-compose initialization
4. Event handlers run as user interacts
5. `on_unmount()` - Cleanup when screen removed

## Tips

- Use `id` for widgets you need to query later
- Use `classes` for styling groups of widgets
- Keep CSS in the class `CSS` attribute
- Actions are methods named `action_*`
- Bindings connect keys to actions
- Use containers for layout, not CSS positioning
