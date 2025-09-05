import subprocess
import psutil
from textual.app import App, ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    TabbedContent,
    TabPane,
    Label,
)

# --- Custom Widget Imports ---
# Make sure this file is in the correct directory so it can find the 'widgets' folder.
from widgets.calendar import CalendarPane
from widgets.taskbook import TaskbookPane
from widgets.task_manager import TaskbookManager
from widgets.taskbook_interactive import InteractiveTaskbook

# ----------------------------


# --- NEW CUSTOM WIDGET FOR DISK USAGE ---
class DufDisplay(Static):
    """A widget to display the output of the 'duf' command."""

    def on_mount(self) -> None:
        """Event handler called when widget is added to the DOM."""
        self.update("⏳ Fetching disk usage information...")
        self.run_worker(self.fetch_duf_output, exclusive=True)

    def get_duf_output(self) -> str:
        """Runs the 'duf' command and returns its output as a string."""
        try:
            result = subprocess.run(
                ["duf", "-style", "ascii", "-width", "120"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,  # Add a timeout to prevent indefinite hanging
            )
            return result.stdout
        except FileNotFoundError:
            return "[bold red]Error: The 'duf' command was not found.\nPlease make sure it's installed and in your system's PATH.[/]"
        except subprocess.CalledProcessError as e:
            return f"[bold red]An error occurred while running 'duf':\n{e.stderr}[/]"
        except subprocess.TimeoutExpired:
            return "[bold red]Error: The 'duf' command timed out after 10 seconds.[/]"
        except Exception as e:
            return f"[bold red]An unexpected error occurred: {e}[/]"

    async def fetch_duf_output(self) -> None:
        """Worker task that runs the duf command and updates the content."""
        output = self.get_duf_output()
        self.update(output)


def is_process_running(process_name: str) -> bool:
    """Check if a process with the given name is running (cross-platform)."""
    for proc in psutil.process_iter(["name", "cmdline"]):
        if process_name.lower() in proc.info.get("name", "").lower():
            return True
        cmdline = proc.info.get("cmdline")
        if cmdline and process_name.lower() in " ".join(cmdline).lower():
            return True
    return False


class DashboardApp(App):
    """A TUI dashboard merging all features into a tabbed interface."""

    CSS_PATH = "style.css"

    # --- BINDINGS MODIFIED HERE ---
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        # Home row keys to switch tabs
        ("h", "switch_tab('home-tab')", "Home"),
        ("b", "switch_tab('taskbook-tab')", "Taskbook"),
        ("s", "switch_tab('services-tab')", "Services"),
        ("l", "switch_tab('tools-tab')", "Launch Tools"),
        ("f", "switch_tab('disk-management-tab')", "Disk Mngmt"),
    ]
    # --------------------------

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # yield Header()
        yield Footer()

        with TabbedContent(initial="home-tab"):
            # Tab 1: Home
            with TabPane("Home", id="home-tab"):
                with Container(id="home-grid"):
                    yield Container(
                        Label("[b]🗓️ Calendar[/b]"), CalendarPane(), id="calendar"
                    )
                    yield Container(
                        Label("[b]✔ Tasks & Notes[/b]"), TaskbookPane(), id="taskbook"
                    )

            # Tab 2: Interactive Taskbook
            with TabPane("Taskbook", id="taskbook-tab"):
                yield InteractiveTaskbook()

            # Tab 3: Service Dashboard
            with TabPane("Services", id="services-tab"):
                with Vertical(classes="pane"):
                    yield Static("Services Status", classes="pane-title")
                    yield Static(
                        "▶ copyparty: [bold green]...[/]", id="copyparty-status"
                    )

            # Tab 4: Tool Launcher
            with TabPane("Launch Tools", id="tools-tab"):
                with Vertical(classes="pane"):
                    yield Static("Launch External Tools", classes="pane-title")
                    yield Static(id="tool-status", classes="status-message")
                    yield Button(
                        "Task Manager (btop)", id="btn-btop", variant="primary"
                    )
                    yield Button(
                        "File Explorer (superfile)",
                        id="btn-superfile",
                        variant="success",
                    )

            # Tab 5: Disk Management now uses our custom widget
            with TabPane("Disk Management", id="disk-management-tab"):
                yield DufDisplay(classes="pane-content")

    # --- NEW ACTION METHOD ADDED ---
    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to a tab with the given ID."""
        self.query_one(TabbedContent).active = tab_id

    # -------------------------------

    def on_mount(self) -> None:
        """Called when the app is first mounted to start the status checker."""
        self.update_copyparty_status()
        self.set_interval(5, self.update_copyparty_status)

    def on_taskbook_manager_refresh_data(
        self, message: TaskbookManager.RefreshData
    ) -> None:
        """Catches custom message to refresh the home screen's taskbook pane."""
        taskbook_pane = self.query_one(TaskbookPane)
        taskbook_pane.update_taskbook()

    def update_copyparty_status(self) -> None:
        """Update the status of the copyparty service in the Dashboard tab."""
        if self.is_mounted(self.query_one("#copyparty-status")):
            status_widget = self.query_one("#copyparty-status")
            if is_process_running("copyparty"):
                status_widget.update("▶ copyparty: [bold green]UP[/]")
            else:
                status_widget.update("▶ copyparty: [bold red]DOWN[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events from the Tools tab."""
        command = None
        status_widget = self.query_one("#tool-status")
        status_widget.update()

        if event.button.id == "btn-btop":
            command = "btop4win"
        elif event.button.id == "btn-superfile":
            command = "spf"

        if command:
            try:
                with self.suspend():
                    subprocess.run(command, shell=True, check=True)
            except FileNotFoundError:
                status_widget.update(
                    f"[bold red]Error: Command '{command}' not found.[/]"
                )
            except Exception as e:
                status_widget.update(f"[bold red]An error occurred: {e}[/bold red]")


if __name__ == "__main__":
    app = DashboardApp()
    app.run()
