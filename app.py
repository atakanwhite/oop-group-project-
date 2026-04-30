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
# Modals (Dependency Injection)
# ---------------------------------------------------------------------------


class ProjectFormScreen(ModalScreen):
    """Form to create a new project. Receives project repository."""

    def __init__(self, project_repo: db.ProjectQueries) -> None:
        super().__init__()
        self.repo = project_repo

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

        p = Project(
            project_name=name,
            project_description=self.query_one("#inp-desc", Input).value,
        )
        self.repo.add_project(p)
        self.dismiss(p)


class TaskForm(ModalScreen):
    """Form to create a new task. Receives repository and context data."""

    def __init__(
        self,
        project_id: int,
        task_repo: db.TaskQueries,
        priorities: list[Priority],
        milestones: list[Milestone],
    ) -> None:
        super().__init__()
        self._project_id = project_id
        self.repo = task_repo
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
            yield Label(f"Priority id [{pri_hint}]")
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
            return

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
            task_description=self.query_one("#inp-desc", Input).value,
        )
        self.repo.add_task(t)
        self.dismiss(t)


class MilestoneForm(ModalScreen):
    def __init__(self, project_id: int, milestone_repo: db.MilestoneQueries) -> None:
        super().__init__()
        self._project_id = project_id
        self.repo = milestone_repo

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("New Milestone", id="title")
            yield Label("Milestone Name")
            yield Input(placeholder="e.g. Beta Release", id="inp-name")
            with Horizontal(id="btn-row"):
                yield Button("Create", variant="primary", id="btn-ok")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return
        name = self.query_one("#inp-name", Input).value.strip()
        if not name:
            return

        m = Milestone(project_id=self._project_id, milestone_name=name)
        self.repo.add_milestone(m)
        self.dismiss(m)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class ProjectView(ListView):
    """Navigation keys handled here, action keys bubble to App."""

    pass


class TaskView(DataTable):
    """Navigation keys handled here, action keys bubble to App."""

    pass


# ---------------------------------------------------------------------------
# Main Controller
# ---------------------------------------------------------------------------


class SnekPMApp(App):
    CSS_PATH = "style.tcss"
    TITLE = "🐍 snekPM"

    BINDINGS = [
        Binding("H", "focus_previous", "← Panel"),
        Binding("L", "focus_next", "Panel →"),
        Binding("q", "quit", "Quit"),
        # Global Action Bindings (Fixes the non-working keys)
        Binding("n", "new_project", "New Project"),
        Binding("t", "new_task", "New Task"),
        Binding("m", "add_milestone", "Add Milestone"),
        Binding("x", "toggle_done", "Toggle Done"),
        Binding("d", "delete_selected", "Delete"),
    ]

    selected_project_id: reactive[int | None] = reactive(None)

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

    def on_mount(self) -> None:
        self._project_ids = []
        # 1. Initialize Engine
        self.db_engine = db.Database()

        # 2. Initialize Specialists
        self.project_queries = db.ProjectQueries(self.db_engine)
        self.task_queries = db.TaskQueries(self.db_engine)
        self.milestone_queries = db.MilestoneQueries(self.db_engine)
        self.priority_queries = db.PriorityQueries(self.db_engine)

        # 3. Setup UI
        self._setup_task_table()
        self._ensure_priorities()
        self._refresh_projects()
        self.query_one("#project-list").focus()

    def on_unmount(self) -> None:
        self.db_engine.close()

    def _ensure_priorities(self) -> None:
        if not self.priority_queries.get_all_priorities():
            for name in ("Low", "Medium", "High", "Critical"):
                self.priority_queries.add_priority(Priority(priority_name=name))

    def _setup_task_table(self) -> None:
        table = self.query_one("#task-table", DataTable)
        table.add_columns("ID", "Task", "Priority", "Done")

    def _refresh_projects(self) -> None:
        lv = self.query_one("#project-list", ListView)
        lv.clear()
        self._project_ids = []
        for row in self.project_queries.get_all_projects():
            tick = "✓" if row[6] else "○"
            lv.append(ListItem(Label(f" {tick} {row[2]}")))
            self._project_ids.append(row[0])

    def _refresh_tasks(self) -> None:
        table = self.query_one("#task-table", DataTable)
        table.clear()
        if not self.selected_project_id:
            return

        # Update Title Panel
        p_row = self.project_queries.get_project(self.selected_project_id)
        if p_row:
            ms_rows = self.milestone_queries.fetch_milestones_by_project(
                self.selected_project_id
            )
            ms_text = ", ".join(m[3] for m in ms_rows) or "None"
            self.query_one("#tasks-title", Static).update(
                f" 📁 {p_row[2]} | Milestones: {ms_text}"
            )

        # Populate Table
        for row in self.task_queries.fetch_tasks_by_project(self.selected_project_id):
            done = "✓" if row[10] else "○"
            table.add_row(str(row[0]), row[6], str(row[4]), done, key=str(row[0]))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # Safe indexing fix
        idx = event.list_view.index
        if idx is not None and 0 <= idx < len(self._project_ids):
            self.selected_project_id = self._project_ids[idx]
            self._refresh_tasks()
            self.query_one("#task-table").focus()

    def action_new_project(self) -> None:
        self.push_screen(
            ProjectFormScreen(self.project_queries),
            callback=lambda _: self._refresh_projects(),
        )

    def action_new_task(self) -> None:
        if self.selected_project_id:
            # Map raw tuples back to objects for the TaskForm hint helpers
            pris = [
                Priority(priority_id=r[0], priority_name=r[2])
                for r in self.priority_queries.get_all_priorities()
            ]
            ms = [
                Milestone(milestone_id=r[0], project_id=r[1], milestone_name=r[3])
                for r in self.milestone_queries.fetch_milestones_by_project(
                    self.selected_project_id
                )
            ]

            self.push_screen(
                TaskForm(self.selected_project_id, self.task_queries, pris, ms),
                callback=lambda _: self._refresh_tasks(),
            )

    def action_add_milestone(self) -> None:
        if self.selected_project_id:
            self.push_screen(
                MilestoneForm(self.selected_project_id, self.milestone_queries),
                callback=lambda _: self._refresh_tasks(),
            )

    def action_toggle_done(self) -> None:
        table = self.query_one("#task-table", DataTable)
        if table.cursor_row >= 0:
            task_id = int(table.get_row_at(table.cursor_row)[0])
            raw = self.task_queries.get_task(task_id)
            if raw:
                # Map raw tuple to model to perform logic
                t = Task(
                    task_id=raw[0],
                    project_id=raw[1],
                    priority_id=raw[4],
                    task_name=raw[6],
                    is_complete=raw[10],
                )
                t.is_complete = 0 if t.is_complete else 1
                self.task_queries.update_task(t)
                self._refresh_tasks()

    def action_delete_selected(self) -> None:
        table = self.query_one("#task-table", DataTable)
        if table.has_focus and table.cursor_row >= 0:
            task_id = int(table.get_row_at(table.cursor_row)[0])
            self.task_queries.delete_task(task_id)
            self._refresh_tasks()
        elif self.selected_project_id:
            self.project_queries.delete_project(self.selected_project_id)
            self.selected_project_id = None
            self._refresh_projects()
            self.query_one("#task-table", DataTable).clear()


if __name__ == "__main__":
    SnekPMApp().run()
