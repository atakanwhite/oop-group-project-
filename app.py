# app.py - correct import order
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

import db
from models import Priority, Project, Task

# ---------------------------------------------------------------------------
# Helper: seed default priorities if the table is empty
# ---------------------------------------------------------------------------


def _ensure_priorities() -> None:
    if not Priority.all():
        for name in ("Low", "Medium", "High", "Critical"):
            Priority(priority_name=name).save()


# ---------------------------------------------------------------------------
# Modal: create / edit a project
# ---------------------------------------------------------------------------


class ProjectFormScreen(ModalScreen[Project | None]):
    """Simple form to create a new project."""

    DEFAULT_CSS = """
    ProjectFormScreen {
        align: center middle;
    }
    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }
    #dialog Label { margin-bottom: 1; }
    #dialog Input  { margin-bottom: 1; }
    #btn-row { height: auto; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("New Project", id="title")
            yield Label("Name")
            yield Input(placeholder="Project name", id="inp-name")
            yield Label("Description")
            yield Input(placeholder="(optional)", id="inp-desc")
            with Horizontal(id="btn-row"):
                yield Button("Create", variant="primary", id="btn-ok")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return
        name = self.query_one("#inp-name", Input).value.strip()
        if not name:
            self.query_one("#inp-name", Input).focus()
            return
        desc = self.query_one("#inp-desc", Input).value.strip()
        p = Project(project_name=name, project_description=desc)
        p.save()
        self.dismiss(p)


# ---------------------------------------------------------------------------
# Modal: add a task to a project
# ---------------------------------------------------------------------------


class TaskFormScreen(ModalScreen[Task | None]):
    """Form to create a new task inside the selected project."""

    DEFAULT_CSS = """
    TaskFormScreen {
        align: center middle;
    }
    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }
    #dialog Label { margin-bottom: 1; }
    #dialog Input  { margin-bottom: 1; }
    #btn-row { height: auto; }
    """

    def __init__(self, project_id: int, priorities: list[Priority]) -> None:
        super().__init__()
        self._project_id = project_id
        self._priorities = priorities

    def compose(self) -> ComposeResult:
        pri_hint = "  ".join(
            f"{p.priority_id}={p.priority_name}" for p in self._priorities
        )
        with Container(id="dialog"):
            yield Label("New Task", id="title")
            yield Label("Task name")
            yield Input(placeholder="Task name", id="inp-name")
            yield Label("Description")
            yield Input(placeholder="(optional)", id="inp-desc")
            yield Label(f"Priority id  [{pri_hint}]")
            yield Input(placeholder="1", id="inp-pri", value="1")
            with Horizontal(id="btn-row"):
                yield Button("Add", variant="primary", id="btn-ok")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return
        name = self.query_one("#inp-name", Input).value.strip()
        if not name:
            self.query_one("#inp-name", Input).focus()
            return
        desc = self.query_one("#inp-desc", Input).value.strip()
        try:
            pri = int(self.query_one("#inp-pri", Input).value.strip() or "1")
        except ValueError:
            pri = 1
        t = Task(
            project_id=self._project_id,
            priority_id=pri,
            task_name=name,
            task_description=desc,
        )
        t.save()
        self.dismiss(t)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


class SnekPMApp(App):
    """snekPM – terminal project manager."""

    TITLE = "🐍 snekPM"
    SUB_TITLE = "Project Manager"

    BINDINGS = [
        Binding("n", "new_project", "New project"),
        Binding("t", "new_task", "New task"),
        Binding("space", "toggle_done", "Toggle done"),
        Binding("delete,d", "delete_selected", "Delete"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    #sidebar {
        width: 30;
        border-right: solid $primary;
        height: 100%;
    }

    #sidebar-title {
        background: $primary;
        color: $background;
        padding: 0 1;
        text-align: center;
    }

    #project-list {
        height: 1fr;
    }

    #main {
        width: 1fr;
        height: 100%;
    }

    #tasks-title {
        background: $accent;
        color: $background;
        padding: 0 1;
    }

    #task-table {
        height: 1fr;
    }

    #status-bar {
        height: 1;
        background: $panel;
        padding: 0 1;
        color: $text-muted;
    }
    """

    selected_project_id: reactive[int | None] = reactive(None)

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("  PROJECTS", id="sidebar-title")
                yield ListView(id="project-list")
            with Vertical(id="main"):
                yield Static(" Select a project …", id="tasks-title")
                yield DataTable(id="task-table", zebra_stripes=True)
        yield Static("", id="status-bar")
        yield Footer()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        self._project_ids = []
        db.init_db()
        _ensure_priorities()
        self._setup_task_table()
        self._refresh_projects()

    def _setup_task_table(self) -> None:
        table = self.query_one("#task-table", DataTable)
        table.add_columns("ID", "Task", "Priority", "Milestone", "Done", "Ends")

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _refresh_projects(self) -> None:
        lv = self.query_one("#project-list", ListView)
        lv.clear()

        self._project_ids = []

        for p in Project.all():
            tick = "✓" if p.is_complete else "○"
            lv.append(ListItem(Label(f" {tick} {p.project_name}")))
            self._project_ids.append(p.project_id)

    def _refresh_tasks(self) -> None:
        table = self.query_one("#task-table", DataTable)
        table.clear()
        if self.selected_project_id is None:
            return
        for t in Task.by_project(self.selected_project_id):
            indent = "  " if t.parent_task_id else ""
            done = "✓" if t.is_complete else "○"
            table.add_row(
                str(t.task_id),
                f"{indent}{t.task_name}",
                str(t.priority_id),
                str(t.milestone_id or "—"),
                done,
                str(t.date_end or "—"),
                key=str(t.task_id),
            )

    def _set_status(self, msg: str) -> None:
        self.query_one("#status-bar", Static).update(msg)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index

        if index is None or index < 0:
            return

        if index >= len(self._project_ids):
            return

        pid = self._project_ids[index]
        if pid is None:
            return

        self.selected_project_id = pid
        p = Project.get(pid)
        if p:
            self.query_one("#tasks-title", Static).update(
                f" 📁 {p.project_name}  (id={pid})"
            )
        self._refresh_tasks()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_new_project(self) -> None:
        def _done(result: Project | None) -> None:
            if result:
                self._refresh_projects()
                self._set_status(f"Project '{result.project_name}' created.")

        self.push_screen(ProjectFormScreen(), _done)

    def action_new_task(self) -> None:
        if self.selected_project_id is None:
            self._set_status("Select a project first (click in the left panel).")
            return

        def _done(result: Task | None) -> None:
            if result:
                self._refresh_tasks()
                self._set_status(f"Task '{result.task_name}' added.")

        priorities = Priority.all()
        self.push_screen(TaskFormScreen(self.selected_project_id, priorities), _done)

def action_toggle_done(self) -> None:
    table = self.query_one("#task-table", DataTable)

    # No project / no tasks loaded
    if table.row_count == 0:
        self._set_status("No task selected.")
        return

    # Guard against invalid cursor position
    if table.cursor_row < 0 or table.cursor_row >= table.row_count:
        self._set_status("No task selected.")
        return

    row = table.get_row_at(table.cursor_row)
    task_id = int(row[0])
    task = Task.get(task_id)
    if task is None:
        self._set_status("Task not found.")
        return

    task.is_complete = 0 if task.is_complete else 1
    task.save()
    self._refresh_tasks()
    self._set_status(
        f"Task #{task_id} marked {'done' if task.is_complete else 'open'}."
    )
    def action_delete_selected(self) -> None:
        # Try task table first
        table = self.query_one("#task-table", DataTable)
        if table.has_focus and table.cursor_row >= 0:
            row = table.get_row_at(table.cursor_row)
            task_id = int(row[0])
            task = Task.get(task_id)
            if task:
                task.delete()
                self._refresh_tasks()
                self._set_status(f"Task #{task_id} deleted.")
            return

        # Otherwise try deleting the selected project
        if self.selected_project_id is not None:
            p = Project.get(self.selected_project_id)
            if p:
                p.delete()
                self.selected_project_id = None
                self.query_one("#tasks-title", Static).update(" Select a project …")
                self.query_one("#task-table", DataTable).clear()
                self._refresh_projects()
                self._set_status("Project deleted.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    app = SnekPMApp()
    app.run()


if __name__ == "__main__":
    main()
