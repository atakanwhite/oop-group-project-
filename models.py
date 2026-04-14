#insert models here
# models.py
# Defines the core data models for the Project Management App.
# Contains: Item (base), Task, Project classes with full OOP features.

from datetime import date


class Item:
    """
    Base class representing a generic trackable item.
    Provides shared attributes and interface for subclasses (Task, Project).
    Demonstrates: base class, polymorphism via status_summary().
    """

    def __init__(self, item_id: int, title: str, description: str):
        self.item_id = item_id
        self.title = title
        self.description = description
        self.completed = False  # shared state for all items

    def mark_complete(self):
        """Mark this item as completed."""
        self.completed = True

    def status_summary(self) -> str:
        """
        Return a human-readable status string.
        Overridden in subclasses (polymorphism).
        """
        status = "Complete" if self.completed else "Pending"
        return f"[{status}] {self.title}"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.item_id}, title='{self.title}')"


class Task(Item):
    """
    Represents a single task belonging to a project.
    Inherits from Item. Adds deadline and priority.
    Demonstrates: inheritance, method override (polymorphism), data stored in dict.
    """

    PRIORITIES = ("low", "medium", "high")  # tuple used as constant data structure

    def __init__(self, item_id: int, title: str, description: str,
                 deadline: date, priority: str = "medium"):
        super().__init__(item_id, title, description)  # call parent constructor

        if priority not in Task.PRIORITIES:
            raise ValueError(f"Priority must be one of {Task.PRIORITIES}")

        self.deadline = deadline
        self.priority = priority

    def is_overdue(self) -> bool:
        """Return True if the task deadline has passed and it is not completed."""
        return not self.completed and self.deadline < date.today()

    def status_summary(self) -> str:
        """
        Override base class method (polymorphism).
        Adds priority and deadline info to the status string.
        """
        base = super().status_summary()
        overdue = " ⚠ OVERDUE" if self.is_overdue() else ""
        return f"{base} | Priority: {self.priority} | Due: {self.deadline}{overdue}"

    def to_dict(self) -> dict:
        """Serialize task to a dictionary (data structure usage)."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "deadline": str(self.deadline),
            "priority": self.priority,
            "completed": self.completed,
        }


class Project(Item):
    """
    Represents a project that contains multiple Tasks.
    Inherits from Item. Associates with Task objects (association relationship).
    Demonstrates: inheritance, association, objects as function arguments,
                  list as data structure, polymorphism via status_summary().
    """

    def __init__(self, item_id: int, title: str, description: str, deadline: date):
        super().__init__(item_id, title, description)
        self.deadline = deadline
        self.tasks: list = []  # list of Task objects — association

    def add_task(self, task: Task):
        """
        Add a Task object to this project.
        Demonstrates: object passed as function argument.
        """
        if not isinstance(task, Task):
            raise TypeError("Only Task instances can be added to a Project.")
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by its ID. Returns True if found and removed."""
        for task in self.tasks:
            if task.item_id == task_id:
                self.tasks.remove(task)
                return True
        return False

    def get_task(self, task_id: int):
        """Return the Task with the given ID, or None if not found."""
        for task in self.tasks:
            if task.item_id == task_id:
                return task
        return None

    def completion_rate(self) -> float:
        """Return the fraction of tasks completed (0.0 to 1.0)."""
        if not self.tasks:
            return 0.0
        completed_count = sum(1 for t in self.tasks if t.completed)
        return completed_count / len(self.tasks)

    def upcoming_deadlines(self) -> list:
        """Return a list of incomplete tasks sorted by deadline (soonest first)."""
        pending = [t for t in self.tasks if not t.completed]
        return sorted(pending, key=lambda t: t.deadline)

    def recent_activity(self) -> list:
        """Return the last 5 tasks added to the project (most recent first)."""
        return list(reversed(self.tasks[-5:]))

    def status_summary(self) -> str:
        """
        Override base class method (polymorphism).
        Includes task count and completion percentage.
        """
        base = super().status_summary()
        pct = int(self.completion_rate() * 100)
        return f"{base} | Tasks: {len(self.tasks)} | Progress: {pct}%"

    def to_dict(self) -> dict:
        """Serialize project (without tasks) to a dictionary."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "deadline": str(self.deadline),
            "completed": self.completed,
        }
