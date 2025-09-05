from datetime import datetime
from textual.widgets import Static


class Clock(Static):
    """A widget to display the current date and time."""

    def on_mount(self) -> None:
        """Event handler that starts a timer to update the time every second."""
        self.set_interval(1, self.update_time)
        self.update_time()

    def update_time(self) -> None:
        """Method to update the time display."""
        now = datetime.now()
        self.update(f"{now.strftime('%A, %d %B %Y')}\n{now.strftime('%I:%M %p')}")
