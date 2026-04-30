from __future__ import annotations

from dataclasses import dataclass
from datetime import date

"""Data layer model"""


@dataclass(kw_only=True)
class BaseModel:
    """
    Base model for all other data layer objects,
    easily extendable when more classes come into play and share information
    """

    created_at: str | None = None


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Project(BaseModel):
    project_name: str
    project_description: str = ""
    date_start: date | None = None
    date_end: date | None = None
    is_complete: int = 0
    project_id: int | None = None

    def __str__(self) -> str:
        status = "✓" if self.is_complete else "○"
        return f"[{status}] #{self.project_id} {self.project_name}"


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Priority(BaseModel):
    priority_name: str
    priority_id: int | None = None

    def __str__(self) -> str:
        return f"Priority({self.priority_id}: {self.priority_name})"


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Milestone(BaseModel):
    project_id: int
    milestone_name: str
    date: date | None = None
    milestone_id: int | None = None

    def __str__(self) -> str:
        return f"Milestone({self.milestone_id}: {self.milestone_name} @ {self.date})"


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Tag(BaseModel):
    tag_name: str
    tag_id: int | None = None

    def __str__(self) -> str:
        return f"#{self.tag_name}"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


@dataclass(kw_only=True)
class Task(BaseModel):
    project_id: int
    priority_id: int
    task_name: str
    task_description: str = ""
    milestone_id: int | None = None
    parent_task_id: int | None = None
    date_start: date | None = None
    date_end: date | None = None
    is_complete: int = 0
    task_id: int | None = None

    def __str__(self) -> str:
        indent = "  " if self.parent_task_id else ""
        status = "✓" if self.is_complete else "○"
        return f"{indent}[{status}] #{self.task_id} {self.task_name}"
