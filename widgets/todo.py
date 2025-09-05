from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Input, Static


class TodoItem(Widget):
    """A single to-do item with a checkbox and due date."""

    # FIX: Applying the class directly to the widget is a cleaner way
    # to ensure the entire component is styled correctly.
    DEFAULT_CLASSES = "todo-item"

    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Checkbox(self.text)
        yield Input(placeholder="Due Date (e.g., YYYY-MM-DD)")


class TodoList(Static):
    """The main to-do list widget with add/remove functionality."""

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Input(placeholder="New task description...", id="new-todo-input"),
            Button("Add Task", variant="primary", id="add-todo"),
            classes="add-bar",
        )
        yield VerticalScroll(id="todo-list-items")
        yield Button("Remove Completed Tasks", variant="error", id="remove-completed")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-todo":
            input_widget = self.query_one("#new-todo-input", Input)
            task_text = input_widget.value
            if task_text:
                new_task = TodoItem(task_text)
                self.query_one("#todo-list-items").mount(new_task)
                input_widget.value = ""
                input_widget.focus()
        elif event.button.id == "remove-completed":
            completed_items = [
                item for item in self.query(TodoItem) if item.query_one(Checkbox).value
            ]
            for item in completed_items:
                item.remove()
