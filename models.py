<<<<<<< HEAD
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from db import (
    MilestoneQueries,
    PriorityQueries,
    ProjectQueries,
    TagQueries,
    TaskQueries,
    TaskTagQueries,
    create_record,
    delete_record,
    fetch_record,
    update_record,
)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


@dataclass
class Project:
    project_name: str
    project_description: str = ""
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    is_complete: int = 0
    project_id: Optional[int] = None
    created_at: Optional[str] = None

    def save(self) -> None:
        """Insert a new project or update an existing one."""
        if self.project_id is None:
            create_record(
                ProjectQueries.INSERT_PROJECT,
                (
                    self.project_name,
                    self.project_description,
                    str(self.date_start) if self.date_start else None,
                    str(self.date_end) if self.date_end else None,
                ),
            )
        else:
            update_record(
                ProjectQueries.UPDATE_PROJECT,
                (
                    self.project_name,
                    self.project_description,
                    str(self.date_start) if self.date_start else None,
                    str(self.date_end) if self.date_end else None,
                    self.is_complete,
                    self.project_id,
                ),
            )

    def delete(self) -> None:
        if self.project_id is not None:
            delete_record(ProjectQueries.DELETE_PROJECT, (self.project_id,))
            self.project_id = None

    def complete(self) -> None:
        self.is_complete = 1
        self.save()

    @classmethod
    def get(cls, project_id: int) -> Optional["Project"]:
        rows = fetch_record(ProjectQueries.FETCH_PROJECT, (project_id,))
        return cls._from_row(rows[0]) if rows else None

    @classmethod
    def all(cls) -> list["Project"]:
        return [cls._from_row(r) for r in fetch_record(ProjectQueries.FETCH_PROJECT_ALL)]

    def tasks(self) -> list["Task"]:
        return Task.by_project(self.project_id)

    def milestones(self) -> list["Milestone"]:
        return Milestone.all_for_project(self.project_id)

    @classmethod
    def _from_row(cls, row: tuple) -> "Project":
        # project_id, created_at, project_name, project_description, date_start, date_end, is_complete
        return cls(
            project_id=row[0],
            created_at=row[1],
            project_name=row[2],
            project_description=row[3] or "",
            date_start=row[4],
            date_end=row[5],
            is_complete=row[6],
        )

    def __str__(self) -> str:
        status = "✓" if self.is_complete else "○"
        return f"[{status}] #{self.project_id} {self.project_name}"


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------


@dataclass
class Priority:
    priority_name: str
    priority_id: Optional[int] = None
    created_at: Optional[str] = None

    def save(self) -> None:
        if self.priority_id is None:
            create_record(PriorityQueries.INSERT_PRIORITY, (self.priority_name,))
        else:
            update_record(PriorityQueries.UPDATE_PRIORITY, (self.priority_name, self.priority_id))

    def delete(self) -> None:
        if self.priority_id is not None:
            delete_record(PriorityQueries.DELETE_PRIORITY, (self.priority_id,))
            self.priority_id = None

    @classmethod
    def get(cls, priority_id: int) -> Optional["Priority"]:
        rows = fetch_record(PriorityQueries.FETCH_PRIORITY, (priority_id,))
        return cls._from_row(rows[0]) if rows else None

    @classmethod
    def all(cls) -> list["Priority"]:
        return [cls._from_row(r) for r in fetch_record(PriorityQueries.FETCH_PRIORITY_ALL)]

    @classmethod
    def _from_row(cls, row: tuple) -> "Priority":
        return cls(priority_id=row[0], created_at=row[1], priority_name=row[2])

    def __str__(self) -> str:
        return f"Priority({self.priority_id}: {self.priority_name})"


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------


@dataclass
class Milestone:
    project_id: int
    milestone_name: str
    date: Optional[date] = None
    milestone_id: Optional[int] = None
    created_at: Optional[str] = None

    def save(self) -> None:
        if self.milestone_id is None:
            create_record(
                MilestoneQueries.INSERT_MILESTONE,
                (self.project_id, self.milestone_name, str(self.date) if self.date else None),
            )
        else:
            update_record(
                MilestoneQueries.UPDATE_MILESTONE,
                (
                    self.project_id,
                    self.milestone_name,
                    str(self.date) if self.date else None,
                    self.milestone_id,
                ),
            )

    def delete(self) -> None:
        if self.milestone_id is not None:
            delete_record(MilestoneQueries.DELETE_MILESTONE, (self.milestone_id,))
            self.milestone_id = None

    @classmethod
    def get(cls, milestone_id: int) -> Optional["Milestone"]:
        rows = fetch_record(MilestoneQueries.FETCH_MILESTONE, (milestone_id,))
        return cls._from_row(rows[0]) if rows else None

    @classmethod
    def all(cls) -> list["Milestone"]:
        return [cls._from_row(r) for r in fetch_record(MilestoneQueries.FETCH_MILESTONE_ALL)]

    @classmethod
    def all_for_project(cls, project_id: int) -> list["Milestone"]:
        return [m for m in cls.all() if m.project_id == project_id]

    @classmethod
    def _from_row(cls, row: tuple) -> "Milestone":
        # milestone_id, project_id, created_at, milestone_name, date
        return cls(
            milestone_id=row[0],
            project_id=row[1],
            created_at=row[2],
            milestone_name=row[3],
            date=row[4],
        )

    def __str__(self) -> str:
        return f"Milestone({self.milestone_id}: {self.milestone_name} @ {self.date})"


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


@dataclass
class Tag:
    tag_name: str
    tag_id: Optional[int] = None
    created_at: Optional[str] = None

    def save(self) -> None:
        if self.tag_id is None:
            create_record(TagQueries.INSERT_TAG, (self.tag_name,))
        else:
            update_record(TagQueries.UPDATE_TAG, (self.tag_name, self.tag_id))

    def delete(self) -> None:
        if self.tag_id is not None:
            delete_record(TagQueries.DELETE_TAG, (self.tag_id,))
            self.tag_id = None

    @classmethod
    def get(cls, tag_id: int) -> Optional["Tag"]:
        rows = fetch_record(TagQueries.FETCH_TAG, (tag_id,))
        return cls._from_row(rows[0]) if rows else None

    @classmethod
    def all(cls) -> list["Tag"]:
        return [cls._from_row(r) for r in fetch_record(TagQueries.FETCH_TAG_ALL)]

    @classmethod
    def _from_row(cls, row: tuple) -> "Tag":
        return cls(tag_id=row[0], created_at=row[1], tag_name=row[2])

    def __str__(self) -> str:
        return f"#{self.tag_name}"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


@dataclass
class Task:
    project_id: int
    priority_id: int
    task_name: str
    task_description: str = ""
    milestone_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    is_complete: int = 0
    task_id: Optional[int] = None
    created_at: Optional[str] = None

    def save(self) -> None:
        if self.task_id is None:
            create_record(
                TaskQueries.INSERT_TASK,
                (
                    self.project_id,
                    self.milestone_id,
                    self.parent_task_id,
                    self.priority_id,
                    self.task_name,
                    self.task_description,
                    str(self.date_start) if self.date_start else None,
                    str(self.date_end) if self.date_end else None,
                ),
            )
        else:
            update_record(
                TaskQueries.UPDATE_TASK,
                (
                    self.project_id,
                    self.milestone_id,
                    self.parent_task_id,
                    self.priority_id,
                    self.task_name,
                    self.task_description,
                    str(self.date_start) if self.date_start else None,
                    str(self.date_end) if self.date_end else None,
                    self.is_complete,
                    self.task_id,
                ),
            )

    def delete(self) -> None:
        if self.task_id is not None:
            delete_record(TaskQueries.DELETE_TASK, (self.task_id,))
            self.task_id = None

    def complete(self) -> None:
        self.is_complete = 1
        self.save()

    # Tag helpers
    def add_tag(self, tag: Tag) -> None:
        if tag.tag_id is not None and self.task_id is not None:
            create_record(TaskTagQueries.INSERT_TASK_TAG, (self.task_id, tag.tag_id))

    def remove_tag(self, tag: Tag) -> None:
        if tag.tag_id is not None and self.task_id is not None:
            delete_record(TaskTagQueries.DELETE_TASK_TAG, (self.task_id, tag.tag_id))

    def tags(self) -> list[Tag]:
        if self.task_id is None:
            return []
        rows = fetch_record(TaskTagQueries.FETCH_TAGS_FOR_TASK, (self.task_id,))
        return [Tag(tag_id=r[0], tag_name=r[1], created_at=r[2]) for r in rows]

    def subtasks(self) -> list["Task"]:
        return [t for t in Task.all() if t.parent_task_id == self.task_id]

    @classmethod
    def get(cls, task_id: int) -> Optional["Task"]:
        rows = fetch_record(TaskQueries.FETCH_TASK, (task_id,))
        return cls._from_row(rows[0]) if rows else None

    @classmethod
    def all(cls) -> list["Task"]:
        return [cls._from_row(r) for r in fetch_record(TaskQueries.FETCH_TASK_ALL)]

    @classmethod
    def by_project(cls, project_id: int) -> list["Task"]:
        return [cls._from_row(r) for r in fetch_record(TaskQueries.FETCH_TASKS_BY_PROJECT, (project_id,))]

    @classmethod
    def _from_row(cls, row: tuple) -> "Task":
        # task_id, project_id, milestone_id, parent_task_id, priority_id,
        # created_at, task_name, task_description, date_start, date_end, is_complete
        return cls(
            task_id=row[0],
            project_id=row[1],
            milestone_id=row[2],
            parent_task_id=row[3],
            priority_id=row[4],
            created_at=row[5],
            task_name=row[6],
            task_description=row[7] or "",
            date_start=row[8],
            date_end=row[9],
            is_complete=row[10],
        )

    def __str__(self) -> str:
        indent = "  " if self.parent_task_id else ""
        status = "✓" if self.is_complete else "○"
        return f"{indent}[{status}] #{self.task_id} {self.task_name}"
=======
import typer
from db import (
    create_record,
    fetch_record,
    update_record,
    delete_record,
    ProjectQueries,
    TaskQueries,
)

app = typer.Typer()


# PROJECTS 

@app.command()
def project_create(name: str, description: str = ""):
    create_record(
        ProjectQueries.INSERT_PROJECT,
        (name, description, None, None),
    )
    print("Project created")


@app.command()
def project_list():
    projects = fetch_record(ProjectQueries.FETCH_PROJECT_ALL)
    for p in projects:
        print(f"{p[0]} | {p[2]} | complete={p[6]}")


#TASKS 

@app.command()
def task_add(
    project_id: int,
    name: str,
    priority_id: int = 1,
    parent_task_id: int | None = None,
):
    create_record(
        TaskQueries.INSERT_TASK,
        (
            project_id,
            None,
            parent_task_id,
            priority_id,
            name,
            "",
            None,
            None,
        ),
    )
    print("Task added")


@app.command()
def task_list(project_id: int):
    tasks = fetch_record(TaskQueries.FETCH_TASKS_BY_PROJECT, (project_id,))
    for t in tasks:
        indent = "  " if t[3] else ""
        print(f"{indent}{t[0]} | {t[6]} | done={t[10]}")


@app.command()
def task_done(task_id: int):
    task = fetch_record(TaskQueries.FETCH_TASK, (task_id,))
    if not task:
        print("Task not found")
        return

    t = task[0]
    update_record(
        TaskQueries.UPDATE_TASK,
        (
            t[1], t[2], t[3], t[4],
            t[6], t[7], t[8], t[9],
            1,  # complete
            task_id,
        ),
    )
    print("Task marked complete")


if __name__ == "__main__":
    app()
>>>>>>> 183c9bda1d2ce7b1eb8d5271b3e13b10a7917492
