import sys
import asyncio
from textual.message import Message
from textual.widgets import Static


class CalendarPane(Static):
    """A widget to display the gcalcli agenda."""

    class UpdateCalendar(Message):
        """A message to update the calendar content."""

        def __init__(self, content: str) -> None:
            self.content = content
            super().__init__()

    def on_mount(self) -> None:
        self.update_calendar()
        self.set_interval(1800, self.update_calendar)

    def update_calendar(self) -> None:
        self.run_worker(self.fetch_gcal_data, exclusive=True)

    async def fetch_gcal_data(self) -> None:
        try:
            process = await asyncio.create_subprocess_shell(
                "gcalcli --nocolor agenda",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            error_message = stderr.decode()
            if process.returncode == 0:
                self.post_message(self.UpdateCalendar(stdout.decode()))
            # FIX: Add specific check for ModuleNotFoundError from gcalcli
            elif "ModuleNotFoundError" in error_message and "pydantic" in error_message:
                friendly_error = (
                    "[red]Error: `gcalcli` is missing a dependency.[/]\n\n"
                    "Please run the following command in your terminal:\n"
                    "[bold yellow]pip install --upgrade --force-reinstall gcalcli[/]"
                )
                self.post_message(self.UpdateCalendar(friendly_error))
            else:
                self.post_message(
                    self.UpdateCalendar(f"[red]Error:\n{error_message}[/]")
                )

        except FileNotFoundError:
            msg = "[red]Error: `gcalcli` not found.\n\nPlease run `pip install gcalcli`.[/]"
            self.post_message(self.UpdateCalendar(msg))

    def on_calendar_pane_update_calendar(self, message: UpdateCalendar) -> None:
        self.update(message.content)
