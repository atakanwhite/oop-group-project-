# models.py
# Defines the core data models for the Project Management App.
# Contains: Item (base), Task, Project classes with full OOP features.

from __future__ import annotations

from datetime import date
from typing import Optional


class Item:
    """
    Base class representing a generic trackable item.
    Provides shared attributes and interface for subclasses (Task, Project).
    """

    def __init__(self, item_id: int, title: str, description: str = ""):
        if not isinstance(item_id, int):
            raise TypeError("item_id must be an integer.")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("title cannot be empty.")

        if description is None:
            description = ""
        if not isinstance(description, str):
            raise TypeError("description must be a string.")

        self.item_id = item_id
        self.title = title.strip()
        self.description = description.strip()
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this item as completed."""
        self.completed = True

    def status_summary(self) -> str:
        """
        Return a human-readable status string.
        Overridden in subclasses.
        """
        status = "Complete" if self.completed else "Pending"
        return f"[{status}] {self.title}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.item_id}, title={self.title!r})"


class Task(Item):
    """
    Represents a single task belonging to a project.
    Inherits from Item. Adds deadline and priority.
    """

    PRIORITIES = ("low", "medium", "high")

    def __init__(
        self,
        item_id: int,
        title: str,
        description: str,
        deadline: date,
        priority: str = "medium",
    ):
        super().__init__(item_id, title, description)

        if not isinstance(deadline, date):
            raise TypeError("deadline must be a date object.")

        if not isinstance(priority, str):
            raise TypeError("priority must be a string.")

        priority = priority.strip().lower()
        if priority not in Task.PRIORITIES:
            raise ValueError(f"Priority must be one of {Task.PRIORITIES}")

        self.deadline = deadline
        self.priority = priority

    def is_overdue(self) -> bool:
        """Return True if the task deadline has passed and it is not completed."""
        return not self.completed and self.deadline < date.today()

    def status_summary(self) -> str:
        """
        Override base class method.
        Adds priority and deadline info to the status string.
        """
        base = super().status_summary()
        overdue = " | OVERDUE" if self.is_overdue() else ""
        return f"{base} | Priority: {self.priority} | Due: {self.deadline}{overdue}"

    def to_dict(self) -> dict:
        """Serialize task to a dictionary."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "priority": self.priority,
            "completed": self.completed,
        }


class Project(Item):
    """
    Represents a project that contains multiple Tasks.
    Inherits from Item and associates with Task objects.
    """

    def __init__(self, item_id: int, title: str, description: str, deadline: date):
        super().__init__(item_id, title, description)

        if not isinstance(deadline, date):
            raise TypeError("deadline must be a date object.")

        self.deadline = deadline
        self.tasks: list[Task] = []

    def _sync_completion_from_tasks(self) -> None:
        """
        Keep project completion consistent with its tasks.
        A project is complete only if it has at least one task and all tasks are complete.
        """
        self.completed = bool(self.tasks) and all(task.completed for task in self.tasks)

    def add_task(self, task: Task) -> None:
        """Add a Task object to this project."""
        if not isinstance(task, Task):
            raise TypeError("Only Task instances can be added to a Project.")

        if any(existing.item_id == task.item_id for existing in self.tasks):
            raise ValueError(f"Task ID {task.item_id} already exists in this project.")

        self.tasks.append(task)
        self._sync_completion_from_tasks()

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by its ID. Returns True if found and removed."""
        for i, task in enumerate(self.tasks):
            if task.item_id == task_id:
                del self.tasks[i]
                self._sync_completion_from_tasks()
                return True
        return False

    def get_task(self, task_id: int) -> Optional[Task]:
        """Return the Task with the given ID, or None if not found."""
        for task in self.tasks:
            if task.item_id == task_id:
                return task
        return None

    def mark_complete(self) -> None:
        """
        Mark the project and all of its tasks as complete.
        """
        for task in self.tasks:
            task.mark_complete()
        self.completed = True

    def completion_rate(self) -> float:
        """Return the fraction of tasks completed (0.0 to 1.0)."""
        if not self.tasks:
            return 0.0
        completed_count = sum(1 for task in self.tasks if task.completed)
        return completed_count / len(self.tasks)

    def upcoming_deadlines(self) -> list[Task]:
        """
        Return incomplete tasks with deadlines today or later, sorted by deadline.
        """
        today = date.today()
        pending = [task for task in self.tasks if not task.completed and task.deadline >= today]
        return sorted(pending, key=lambda task: task.deadline)

    def recent_activity(self) -> list[Task]:
        """Return the last 5 tasks added to the project (most recent first)."""
        return list(reversed(self.tasks[-5:]))

    def status_summary(self) -> str:
        """
        Override base class method.
        Includes task count, progress, and project deadline.
        """
        self._sync_completion_from_tasks()
        base = super().status_summary()
        pct = int(self.completion_rate() * 100)
        return f"{base} | Tasks: {len(self.tasks)} | Progress: {pct}% | Due: {self.deadline}"

    def to_dict(self) -> dict:
        """Serialize project (without tasks) to a dictionary."""
        self._sync_completion_from_tasks()
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "completed": self.completed,
        }