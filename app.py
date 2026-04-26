# app.py - correct import order
# toggling projects and tasks done is not working and there is no code for milestones
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
from models import Milestone, Priority, Project, Task

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


class ProjectFormScreen(ModalScreen):
    """Simple form to create a new project."""

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


class TaskForm(ModalScreen):
    """Form to create a new task inside the selected project."""

    def __init__(
        self, project_id: int, priorities: list[Priority], milestones: list[Milestone]
    ) -> None:
        super().__init__()
        self._project_id = project_id
        self._priorities = priorities
        self._milestones = milestones

    def compose(self) -> ComposeResult:
        pri_hint = "  ".join(
            f"{p.priority_id}={p.priority_name}" for p in self._priorities
        )
        ms_hint = (
            "  ".join(f"{m.milestone_id}={m.milestone_name}" for m in self._milestones)
            or "None"
        )
        with Container(id="dialog"):
            yield Label("New Task", id="title")
            yield Label("Task name")
            yield Input(placeholder="Task name", id="inp-name")
            yield Label("Description")
            yield Input(placeholder="(optional)", id="inp-desc")
            yield Label(f"Priority id  [{pri_hint}]")
            yield Input(placeholder="1", id="inp-pri", value="1")
            yield Label(f"Milestone id [{ms_hint}]")
            yield Input(placeholder="(optional)", id="inp-ms")
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

        ms_val = self.query_one("#inp-ms", Input).value.strip()
        ms_id = int(ms_val) if ms_val.isdigit() else None
        t = Task(
            project_id=self._project_id,
            priority_id=pri,
            milestone_id=ms_id,
            task_name=name,
            task_description=desc,
        )
        t.save()
        self.dismiss(t)


# ---------------------------------------------------------------------------
# Modal: add a milestone to a project
# ---------------------------------------------------------------------------
class MilestoneForm(ModalScreen):
    def __init__(self, project_id: int) -> None:
        super().__init__()
        self._project_id = project_id

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("New Milestone", id="title")
            yield Label("Milestone Name")
            yield Input(placeholder="e.g. Beta Release", id="inp-name")
            yield Label("Date (YYYY-MM-DD)")
            yield Input(placeholder="optional", id="inp-date")
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

        date_str = self.query_one("#inp-date", Input).value.strip()

        m = Milestone(project_id=self._project_id, milestone_name=name, date=date_str)
        m.save()
        self.dismiss(m)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class ProjectView(ListView):
    """ListView for context aware key bindings"""

    BINDINGS = [
        Binding("n", "new_project", "New Project"),
        Binding("u", "update_project", "Update Project"),
        Binding("d", "delete_project", "Delete Project"),
        Binding("m", "add_milestone", "Add Milestone"),
        Binding("j", "cursor_down", "↓"),
        Binding("k", "cursor_up", "↑"),
    ]

    def action_new_project(self) -> None:
        self.app.action_new_project()

    def action_delete_project(self) -> None:
        self.app.action_delete_selected()

    def action_update_project(self) -> None:
        # Doesn't exist yet
        # self.app.action_update_project()
        pass

    def action_add_milestone(self) -> None:
        if self.index is not None:
            self.app.action_add_milestone()


class TaskView(DataTable):
    """DataTable for context aware task bindings"""

    BINDINGS = [
        Binding("t", "new_task", "New Task"),
        Binding("T", "new_subtask", "New Sub-Task"),
        Binding("u", "update_task", "Update Task"),
        Binding("U", "update_subtask", "Update Sub-Task"),
        Binding("x", "toggle_done", "Toggle Done"),
        Binding("d", "delete_task", "Delete Task"),
        Binding("h", "cursor_left", "←"),
        Binding("j", "cursor_down", "↓"),
        Binding("k", "cursor_up", "↑"),
        Binding("l", "cursor_right", "→"),
    ]

    def action_new_task(self) -> None:
        self.app.action_new_task()

    def action_new_subtask(self) -> None:
        pass

    def action_delete_task(self) -> None:
        self.app.action_delete_selected()

    def action_toggle_done(self) -> None:
        self.app.action_toggle_done()

    def action_update_task(self) -> None:
        pass

    def action_update_subtask(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


class SnekPMApp(App):
    """snekPM – terminal project manager."""

    CSS_PATH = "style.tcss"
    ENABLE_COMMAND_PALETTE = False

    TITLE = "🐍 snekPM"
    SUB_TITLE = "Project Manager"

    BINDINGS = [
        Binding("H", "focus_previous", "← Panel"),
        Binding("L", "focus_next", "Panel →"),
        Binding("q", "quit", "Quit"),
    ]

    selected_project_id: reactive[int | None] = reactive(None)

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("  PROJECTS", id="sidebar-title")
                yield ProjectView(id="project-list")
            with Vertical(id="main"):
                yield Static(" Select a project …", id="tasks-title")
                yield TaskView(id="task-table", zebra_stripes=True)
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

        project = Project.get(self.selected_project_id)
        milestones = Milestone.all_for_project(self.selected_project_id)

        if project:
            ms_text = ", ".join(m.milestone_name for m in milestones) or "None"
            self.query_one("#tasks-title", Static).update(
                f" 📁 {project.project_name}  (id={project.project_id}) | Milestones: {ms_text}"
            )
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
        self.query_one("#task-table", DataTable).focus()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_new_project(self) -> None:
        self.push_screen(ProjectFormScreen(), callback=self._on_project_created)

    def _on_project_created(self, result: Project | None) -> None:
        if result:
            self._refresh_projects()
            self._set_status(f"Project '{result.project_name}' created.")

    def action_new_task(self) -> None:
        if self.selected_project_id is None:
            self._set_status("Select a project first (click in the left panel).")
            return

        priorities = Priority.all()
        milestones = Milestone.all_for_project(self.selected_project_id)
        self.push_screen(
            TaskForm(self.selected_project_id, priorities, milestones),
            callback=self._on_task_created,
        )

    def _on_task_created(self, result: Task | None) -> None:
        if result:
            self._refresh_tasks()
            self._set_status(f"Task '{result.task_name}' added.")

    def action_add_milestone(self) -> None:
        if self.selected_project_id is None:
            self._set_status("Select a project first.")
            return
        self.push_screen(
            MilestoneForm(self.selected_project_id), callback=self._on_milestone_created
        )

    def _on_milestone_created(self, result: Milestone | None) -> None:
        if result:
            self._set_status(f"Milestone '{result.milestone_name}' added.")
            self._refresh_tasks()

    def action_toggle_done(self) -> None:
        table = self.query_one("#task-table", DataTable)

        if table.row_count == 0:
            self._set_status("No tasks to toggle.")
            return

        if table.cursor_row < 0 or table.cursor_row >= table.row_count:
            self._set_status("Select a task row first.")
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
