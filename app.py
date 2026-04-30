<<<<<<< HEAD
# app.py - correct import order
# toggling projects and tasks done is not working and there is no code for milestones
=======
>>>>>>> 0f1e7ba
from __future__ import annotations

from datetime import date

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

"""
UI Controller in charge of user interaction and passing information
between model and database
"""
# ---------------------------------------------------------------------------
# Modals (Dependency Injection)
# ---------------------------------------------------------------------------


class ProjectDetailScreen(ModalScreen):
    """High level class responsible for
    A floating window showing detailed project information."""

    def __init__(self, project_row: tuple, milestones: list[tuple]) -> None:
        super().__init__()
        self.p = project_row
        self.ms = milestones

    def compose(self) -> ComposeResult:
        """
        Responsible for composing the window,
        and mapping row indices.
        """

        with Container(id="dialog"):
            yield Label(f"PROJECT DETAILS: {self.p[2]}", id="title")

            with Vertical(id="detail-content"):
                yield Label(f"[b]Description:[/b]\n{self.p[3] or 'No description'}")
                yield Label(
                    f"[b]Timeline:[/b] {self.p[4] or 'N/A'}  to  {self.p[5] or 'N/A'}"
                )

                yield Label("\n[b]Milestones:[/b]")
                if not self.ms:
                    yield Label("  - None")
                for m in self.ms:
                    # m[3] is milestone name, m[4] is date
                    yield Label(f"  • {m[3]} ({m[4] or 'No date'})")

                yield Label(
                    f"\n[b]Status:[/b] {'Completed ✓' if self.p[6] else 'In Progress ○'}"
                )

            with Horizontal(id="btn-row"):
                yield Button("Close", id="btn-close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button event listener for closing the info window"""

        if event.button.id == "btn-close":
            self.dismiss()


class ProjectFormScreen(ModalScreen):
    """Form to create a new project. Receives project repository(queries)."""

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
            yield Label("Start Date")
            yield Input(placeholder="2026-04-30 (optional)", id="inp-sdate")
            yield Label("End Date")
            yield Input(placeholder="2026-05-30 (optional)", id="inp-edate")
            with Horizontal(id="btn-row"):
                yield Button("Create", variant="primary", id="btn-ok")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        # Button event listener:
            - Early exits if cancel.
            - Queries name, start date, end date.
            - Maps input values to querie and passes for db

        # Error handling for dates:
            - start date can't be earlier than today
            - end date can't be earlier than start date.
            - Notifys user with popup if error
        """

        if event.button.id == "btn-cancel":
            self.dismiss(None)
            return
        name = self.query_one("#inp-name", Input).value.strip()
        if not name:
            self.query_one("#inp-name", Input).focus()
            return

        s_val = self.query_one("#inp-sdate", Input).value.strip()
        e_val = self.query_one("#inp-edate", Input).value.strip()
        today = date.today()

        try:
            s_date = date.fromisoformat(s_val) if s_val else None
            e_date = date.fromisoformat(e_val) if e_val else None

            if s_date and s_date < today:
                self.notify(
                    f"Start date cannot be in the past! (Today is {today})",
                    severity="error",
                )
                return

            if s_date and e_date and e_date < s_date:
                self.notify("End date must be after the start date!", severity="error")

        except ValueError:
            self.notify("Invalid date format! Use YYYY-MM-DD", severity="error")
            return

        p = Project(
            project_name=name,
            project_description=self.query_one("#inp-desc", Input).value,
            date_start=s_date,
            date_end=e_date,
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
<<<<<<< HEAD
# Views
# ---------------------------------------------------------------------------


class ProjectView(ListView):
    """ListView for context aware key bindings"""

    BINDINGS = [
        Binding("n", "new_project", "New Project"),
        Binding("u", "update_project", "Update Project"),
        Binding("d", "delete_project", "Delete Project"),
        Binding("j", "cursor_down", "↓"),
        Binding("k", "cursor_up", "↑"),
    ]

    def action_new_project(self) -> None:
        self.app.action_new_project()

    def action_delete_project(self) -> None:
        self.app.action_delete_project()

    def action_update_project(self) -> None:
        self.app.action_update_project()


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
=======
# Main Controller
>>>>>>> 0f1e7ba
# ---------------------------------------------------------------------------


class SnekPMApp(App):
    """Wrapper for the applica"""

<<<<<<< HEAD
    ENABLE_COMMAND_PALETTE = False

=======
    CSS_PATH = "style.tcss"
>>>>>>> 0f1e7ba
    TITLE = "🐍 snekPM"

    BINDINGS = [
        Binding("H", "focus_previous", "← Panel"),
        Binding("L", "focus_next", "Panel →"),
        Binding("q", "quit", "Quit"),
        Binding("i", "show_project_info", "Project Info"),
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
        self.db_engine = db.Database()

        self.project_queries = db.ProjectQueries(self.db_engine)
        self.task_queries = db.TaskQueries(self.db_engine)
        self.milestone_queries = db.MilestoneQueries(self.db_engine)
        self.priority_queries = db.PriorityQueries(self.db_engine)

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

        p_row = self.project_queries.get_project(self.selected_project_id)
        if p_row:
            ms_rows = self.milestone_queries.fetch_milestones_by_project(
                self.selected_project_id
            )
            ms_text = ", ".join(m[3] for m in ms_rows) or "None"
            self.query_one("#tasks-title", Static).update(
                f" 📁 {p_row[2]} | Milestones: {ms_text}"
            )

        for row in self.task_queries.fetch_tasks_by_project(self.selected_project_id):
            done = "✓" if row[10] else "○"
            table.add_row(str(row[0]), row[6], str(row[4]), done, key=str(row[0]))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
<<<<<<< HEAD
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
        def _done(result: Project | None) -> None:
            if result:
                self._refresh_projects()
                self._set_status(f"Project '{result.project_name}' created.")

            self.push_screen(ProjectFormScreen(), _done)
=======
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
>>>>>>> 0f1e7ba

    def action_new_task(self) -> None:
        if self.selected_project_id:
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

<<<<<<< HEAD
    def _done(self, result: Task | None) -> None:
        if result:
            self._refresh_tasks()
            self._set_status(f"Task '{result.task_name}' added.")

        priorities = Priority.all()
        self.push_screen(TaskFormScreen(self.selected_project_id, priorities), _done)

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

=======
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

>>>>>>> 0f1e7ba
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

    def action_show_project_info(self) -> None:
        """Fetches data and shows the floating project info window."""
        if self.selected_project_id:
            project_row = self.project_queries.get_project(self.selected_project_id)
            ms_rows = self.milestone_queries.fetch_milestones_by_project(
                self.selected_project_id
            )

            if project_row:
                self.push_screen(ProjectDetailScreen(project_row, ms_rows))


if __name__ == "__main__":
    SnekPMApp().run()
