import asyncio
import re
import subprocess
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.widgets import Button, DataTable, Input, Static, Label


class InteractiveTaskbook(Static):
    """An interactive widget to manage tasks and notes from taskbook."""

    class RefreshData(Message):
        """A custom message to tell the app to refresh the home screen view."""

        pass

    def on_mount(self) -> None:
        """Set up the widget and load initial data."""
        self.run_worker(self.load_data, exclusive=True)

    def compose(self) -> ComposeResult:
        """Create the child widgets for the interactive taskbook."""
        with Vertical(id="add-controls"):
            yield Label("Add New Item:")
            with Horizontal():
                yield Input(placeholder="Description...", id="tb-input")
                yield Button("Add Task", variant="primary", id="tb-add-task")
                yield Button("Add Note", variant="success", id="tb-add-note")

        yield DataTable(id="tb-datatable")

        with Horizontal(id="manage-controls"):
            yield Button("Check/Uncheck Task", id="tb-check")
            yield Button("Delete Selected", variant="error", id="tb-delete")

        yield Static(id="tb-output")

    async def load_data(self) -> None:
        """Fetch data from taskbook and populate the DataTable."""
        datatable = self.query_one(DataTable)
        datatable.clear()

        if not datatable.columns:
            datatable.add_columns("ID", "Type", "Description", "Status")

        try:
            command = "tb"
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                self.parse_and_populate(stdout.decode(), datatable)
            else:
                datatable.add_row("[red]Error", "Could not load data.", stderr.decode())
        except FileNotFoundError:
            datatable.add_row("[red]Error", "Command 'tb' not found.", "")

    def parse_and_populate(self, text: str, table: DataTable) -> None:
        """Parse the raw text output from taskbook into table rows."""
        # FIX: New regex to match the format '1. V description' or '2. * description' etc.
        item_regex = re.compile(r"^\s*(\d+)\.\s+([V*]|\[ \]|-)\s+(.+)")

        for line in text.splitlines():
            # Strip ANSI color codes which can interfere with matching
            line = re.sub(r"\x1b\[[0-9;]*m", "", line)

            match = item_regex.search(line)

            if match:
                item_id, status_char, desc = match.groups()
                item_type = "Note"
                status = "[blue]Note[/]"

                if status_char == "-":
                    # It's a note
                    pass
                else:  # It's a task
                    item_type = "Task"
                    if status_char == "V":
                        status = "[green]Done[/]"
                    elif status_char == "*":
                        status = "[cyan]Starred[/]"
                    else:  # Assuming '[ ]'
                        status = "[yellow]Pending[/]"

                table.add_row(item_id, item_type, desc.strip(), status)

    async def run_tb_command(self, command: str) -> None:
        """Run a taskbook command and refresh the table on success."""
        output_widget = self.query_one("#tb-output", Static)
        process = subprocess.run(
            command, shell=True, capture_output=True, text=True, encoding="utf-8"
        )
        if process.returncode == 0:
            output_widget.update("[green]Success![/]")
            await self.load_data()
            self.post_message(self.RefreshData())
        else:
            output_widget.update(f"[red]Error:\n{process.stderr}[/]")

        self.set_timer(3, lambda: output_widget.update(""))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for all actions."""
        input_widget = self.query_one("#tb-input", Input)
        description = input_widget.value
        output_widget = self.query_one("#tb-output", Static)

        if event.button.id in ("tb-add-task", "tb-add-note") and description:
            flag = "-t" if event.button.id == "tb-add-task" else "-n"
            await self.run_tb_command(f'tb {flag} "{description}"')
            input_widget.value = ""
            input_widget.focus()
            return

        table = self.query_one(DataTable)
        if table.cursor_row < 0:
            output_widget.update(
                "[yellow]Please select an item from the table first.[/]"
            )
            self.set_timer(3, lambda: output_widget.update(""))
            return

        # Use get_row_at to be safe
        selected_row = table.get_row_at(table.cursor_row)
        if not selected_row:
            return

        selected_id = selected_row[0]

        if event.button.id == "tb-check":
            await self.run_tb_command(f"tb -c {selected_id}")
        elif event.button.id == "tb-delete":
            await self.run_tb_command(f"tb -d {selected_id}")
