from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Static, TextArea


class NoteItem(Widget):
    """A single note widget with a text area and a delete button."""

    DEFAULT_CLASSES = "note-item-container"

    def compose(self) -> ComposeResult:
        """Create the child widgets for a note."""
        yield TextArea(classes="note-pad")
        # This line adds the delete button back to each note.
        yield Button("Delete Note", variant="error", classes="note-delete-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """When the delete button is pressed, remove this note."""
        # This action removes the parent NoteItem widget.
        self.remove()


class NotesList(Static):
    """The main notes widget with add functionality."""

    def compose(self) -> ComposeResult:
        yield Button("Add New Note", variant="success", id="add-note")
        yield VerticalScroll(id="notes-list-items")

    def on_mount(self) -> None:
        # Start with one note by default
        self.query_one("#notes-list-items").mount(NoteItem())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-note":
            self.query_one("#notes-list-items").mount(NoteItem())
