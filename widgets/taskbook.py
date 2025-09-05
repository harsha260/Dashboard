import asyncio
from textual.message import Message
from textual.widgets import Static


class TaskbookPane(Static):
    """A widget to display the output of the taskbook command."""

    class UpdateTaskbook(Message):
        """A message to update the taskbook content."""

        def __init__(self, content: str) -> None:
            self.content = content
            super().__init__()

    def on_mount(self) -> None:
        """Event handler that sets up a recurring update for the taskbook list."""
        self.update_taskbook()
        self.set_interval(300, self.update_taskbook)  # Refresh every 5 minutes

    def update_taskbook(self) -> None:
        """Worker method to fetch data from taskbook."""
        self.run_worker(self.fetch_taskbook_data, exclusive=True)

    async def fetch_taskbook_data(self) -> None:
        """Asynchronously runs the taskbook command and updates the widget."""
        try:
            # FIX: The correct command to list all items is simply 'tb'.
            command = "tb"
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                self.post_message(self.UpdateTaskbook(stdout.decode()))
            else:
                stdout_output = stdout.decode().strip()
                stderr_output = stderr.decode().strip()

                error_parts = [
                    f"[red]Error running taskbook (Exit Code: {process.returncode})[/]",
                    f"\n[b]Standard Output:[/]\n{stdout_output}",
                    f"\n[b]Standard Error:[/]\n{stderr_output}",
                ]

                full_error_message = "\n".join(
                    part for part in error_parts if part.splitlines()[-1]
                )
                self.post_message(self.UpdateTaskbook(full_error_message))

        except FileNotFoundError:
            self.post_message(
                self.UpdateTaskbook(
                    "[red]Error: 'tb' not found.\nPlease ensure taskbook is installed (`npm install -g taskbook`) and in your PATH.[/]"
                )
            )

    def on_taskbook_pane_update_taskbook(self, message: UpdateTaskbook) -> None:
        """Message handler to update the taskbook widget content."""
        self.update(message.content)
