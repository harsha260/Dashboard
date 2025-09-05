import subprocess
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static


class TaskbookManager(Static):
    """A widget to add tasks or notes to taskbook."""

    # A custom message to tell the app to refresh the home screen view
    class RefreshData(Message):
        pass

    def __init__(self, item_type: str = "task"):
        super().__init__()
        self.item_type = item_type  # "task" or "note"
        self.command_flag = "-t" if item_type == "task" else "-n"

    def compose(self) -> ComposeResult:
        yield Label(f"Enter new {self.item_type} description below:")
        yield Input(placeholder=f"Your new {self.item_type}...", id="tb-input")
        yield Button(
            f"Add {self.item_type.capitalize()}", variant="primary", id="tb-add-btn"
        )
        # FIX: Use a Static widget for the output so we can update it.
        yield Static(id="tb-output")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "tb-add-btn":
            input_widget = self.query_one("#tb-input", Input)
            description = input_widget.value
            if description:
                # Clear the output message before running the worker
                self.query_one("#tb-output", Static).update("")
                self.run_worker(self.add_item(description))
                input_widget.value = ""
                input_widget.focus()

    async def add_item(self, description: str) -> None:
        """Runs the taskbook command to add a new item."""
        # FIX: Ensure we query for a Static widget.
        output_widget = self.query_one("#tb-output", Static)
        try:
            # Construct the command, e.g., `tb -t "My new task"`
            command = f'tb {self.command_flag} "{description}"'
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )
            if process.returncode == 0:
                output_widget.update("[green]Success![/]")
                # Post a message to tell the main app to refresh the home screen
                self.post_message(self.RefreshData())
            else:
                output_widget.update(f"[red]Error:\n{process.stderr}[/]")
        except FileNotFoundError:
            output_widget.update("[red]Error: 'tb' command not found.[/]")
