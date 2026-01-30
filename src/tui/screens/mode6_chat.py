"""Mode 6: AI Agent Coach Chat Screen."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Input, LoadingIndicator
from textual.binding import Binding
from textual.worker import Worker, WorkerState

from ...agent import PokerCoachAgent, AgentResponse


class ChatMessage(Static):
    """A single chat message widget."""

    def __init__(
        self,
        message_text: str,
        role: str = "user",
        tool_calls: list[str] | None = None,
    ) -> None:
        """Initialize a chat message.

        Args:
            message_text: The message content
            role: "user", "assistant", "tool", or "error"
            tool_calls: List of tool names used (for assistant messages)
        """
        self.role = role
        self.tool_calls = tool_calls or []
        self.message_text = message_text
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create the message content."""
        if self.role == "user":
            yield Static(f"[bold cyan]You:[/bold cyan] {self.message_text}")
        elif self.role == "assistant":
            prefix = "[bold green]Coach:[/bold green]"
            if self.tool_calls:
                tools_str = ", ".join(self.tool_calls)
                yield Static(f"[dim]Used: {tools_str}[/dim]", classes="tool-indicator")
            yield Static(f"{prefix} {self.message_text}")
        elif self.role == "tool":
            yield Static(f"[dim]{self.message_text}[/dim]")
        elif self.role == "error":
            yield Static(f"[bold red]Error:[/bold red] {self.message_text}")
        elif self.role == "system":
            yield Static(f"[bold magenta]{self.message_text}[/bold magenta]")


class Mode6ChatScreen(Screen):
    """AI Agent Coach chat interface."""

    CSS = """
    Mode6ChatScreen {
        background: $surface;
    }

    #chat-header {
        width: 100%;
        height: 3;
        background: $primary-background;
        padding: 0 2;
        align: center middle;
    }

    #chat-title {
        text-style: bold;
        color: $accent;
    }

    #stats {
        dock: right;
        width: auto;
        color: $text-muted;
    }

    #chat-scroll {
        width: 100%;
        height: 1fr;
        padding: 1 2;
        border: solid $primary;
    }

    ChatMessage {
        width: 100%;
        height: auto;
        padding: 0 0 1 0;
        margin: 0;
    }

    .tool-indicator {
        padding: 0;
        margin: 0 0 0 2;
    }

    #loading-container {
        width: 100%;
        height: 3;
        align: center middle;
    }

    #loading {
        width: auto;
    }

    #input-row {
        width: 100%;
        height: 3;
        padding: 0 2;
    }

    #user-input {
        width: 1fr;
    }

    #send-btn {
        width: 10;
        margin-left: 1;
    }

    #button-row {
        width: 100%;
        height: 3;
        align: center middle;
        padding: 0 2;
    }

    #button-row Button {
        margin: 0 1;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("ctrl+l", "clear_chat", "Clear Chat", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the chat screen."""
        super().__init__()
        self.agent = PokerCoachAgent()
        self._current_worker: Worker | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Chat header with stats
        with Horizontal(id="chat-header"):
            yield Static("AI Poker Coach", id="chat-title")
            yield Static("Tokens: 0 | Cost: $0.00", id="stats")

        # Chat messages scroll area
        with VerticalScroll(id="chat-scroll"):
            pass  # Messages will be added dynamically

        # Loading indicator (hidden by default)
        with Container(id="loading-container", classes="hidden"):
            yield LoadingIndicator(id="loading")
            yield Static("Thinking...", id="loading-text")

        # Input row
        with Horizontal(id="input-row"):
            yield Input(placeholder="Ask me anything about poker...", id="user-input")
            yield Button("Send", id="send-btn", variant="primary")

        # Button row
        with Horizontal(id="button-row"):
            yield Button("Clear Chat", id="clear-btn", variant="default")
            yield Button("Back to Menu", id="back-btn", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Check if agent is ready
        if not self.agent.is_ready:
            error = self.agent.init_error or "Unknown error initializing agent"
            self._add_message(error, "error")
            self._add_message(
                "Please ensure ANTHROPIC_API_KEY is set in your .env file.",
                "system",
            )
        else:
            # Show greeting
            self._add_message(self.agent.greeting, "assistant")

        # Focus the input
        self.query_one("#user-input", Input).focus()

    def _add_message(
        self,
        content: str,
        role: str = "user",
        tool_calls: list[str] | None = None,
    ) -> None:
        """Add a message to the chat."""
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        message = ChatMessage(content, role, tool_calls)
        scroll.mount(message)
        scroll.scroll_end(animate=False)

    def _update_stats(self) -> None:
        """Update the stats display."""
        stats = self.agent.get_stats()
        stats_widget = self.query_one("#stats", Static)
        cost_str = f"${stats['estimated_cost']:.4f}"
        stats_widget.update(f"Tokens: {stats['total_tokens']} | Cost: {cost_str}")

    def _set_loading(self, loading: bool) -> None:
        """Show or hide loading indicator."""
        container = self.query_one("#loading-container", Container)
        input_widget = self.query_one("#user-input", Input)
        send_btn = self.query_one("#send-btn", Button)

        if loading:
            container.remove_class("hidden")
            input_widget.disabled = True
            send_btn.disabled = True
        else:
            container.add_class("hidden")
            input_widget.disabled = False
            send_btn.disabled = False
            input_widget.focus()

    async def _send_message(self, message: str) -> None:
        """Send a message to the agent."""
        if not message.strip():
            return

        if not self.agent.is_ready:
            self._add_message(
                "Agent not initialized. Please check your API key.", "error"
            )
            return

        # Add user message
        self._add_message(message, "user")

        # Clear input
        input_widget = self.query_one("#user-input", Input)
        input_widget.value = ""

        # Show loading
        self._set_loading(True)

        # Run the agent in a worker
        self._current_worker = self.run_worker(
            self._chat_worker(message),
            name="chat_worker",
            exclusive=True,
        )

    async def _chat_worker(self, message: str) -> AgentResponse:
        """Worker to run the agent chat."""
        return await self.agent.chat(message)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.worker.name != "chat_worker":
            return

        if event.state == WorkerState.SUCCESS:
            result = event.worker.result
            self._set_loading(False)

            if result is None:
                self._add_message("No response received", "error")
                return

            response: AgentResponse = result
            if response.error:
                self._add_message(response.error, "error")
            else:
                self._add_message(
                    response.content,
                    "assistant",
                    response.tool_calls,
                )

            self._update_stats()

        elif event.state == WorkerState.ERROR:
            self._set_loading(False)
            self._add_message(f"Worker error: {event.worker.error}", "error")

        elif event.state == WorkerState.CANCELLED:
            self._set_loading(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "send-btn":
            input_widget = self.query_one("#user-input", Input)
            self.run_worker(
                self._send_message(input_widget.value),
                exclusive=False,
            )
        elif button_id == "clear-btn":
            self.action_clear_chat()
        elif button_id == "back-btn":
            self.action_back()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "user-input":
            self.run_worker(
                self._send_message(event.value),
                exclusive=False,
            )

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()

    def action_clear_chat(self) -> None:
        """Clear the chat history."""
        # Clear agent history
        self.agent.clear_history()

        # Clear messages from screen
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        for child in list(scroll.children):
            child.remove()

        # Show greeting again
        self._add_message(self.agent.greeting, "assistant")

        # Reset stats display
        stats_widget = self.query_one("#stats", Static)
        stats_widget.update("Tokens: 0 | Cost: $0.00")
