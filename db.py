# db.py
# Database module for the Project Management App.
# Handles all SQLite operations: creating tables, saving, loading,
# updating and deleting Project and Task records.

import sqlite3
from datetime import date

from models import Project, Task

DB_FILE = "project_manager.db"


def get_connection() -> sqlite3.Connection:
    """Open and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db() -> None:
    """
    Create the projects and tasks tables if they don't already exist.
    Called once at application startup.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                item_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                description  TEXT,
                deadline     TEXT NOT NULL,
                completed    INTEGER NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                item_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id   INTEGER NOT NULL,
                title        TEXT NOT NULL,
                description  TEXT,
                deadline     TEXT NOT NULL,
                priority     TEXT NOT NULL DEFAULT 'medium',
                completed    INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (project_id)
                    REFERENCES projects(item_id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()


# ── Project CRUD ────────────────────────────────────────────────────────────

def save_project(project: Project) -> int:
    """
    Insert a new Project into the database.
    Returns the auto-assigned item_id.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (title, description, deadline, completed)
            VALUES (?, ?, ?, ?)
            """,
            (
                project.title,
                project.description,
                project.deadline.isoformat(),
                int(project.completed),
            ),
        )
        conn.commit()

        last_id = cursor.lastrowid
        if last_id is None:
            raise RuntimeError("Failed to retrieve last inserted project ID")

        return last_id


def load_all_projects() -> list[Project]:
    """
    Fetch all projects from the database.
    Returns a list of Project instances.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY item_id")
        rows = cursor.fetchall()

    projects: list[Project] = []
    for row in rows:
        proj = Project(
            item_id=row["item_id"],
            title=row["title"],
            description=row["description"] or "",
            deadline=date.fromisoformat(row["deadline"]),
        )
        proj.completed = bool(row["completed"])
        proj.tasks = load_tasks_for_project(proj.item_id)
        projects.append(proj)

    return projects


def update_project(project: Project) -> None:
    """Update an existing project record in the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE projects
            SET title = ?, description = ?, deadline = ?, completed = ?
            WHERE item_id = ?
            """,
            (
                project.title,
                project.description,
                project.deadline.isoformat(),
                int(project.completed),
                project.item_id,
            ),
        )
        conn.commit()


def delete_project(project_id: int) -> None:
    """Delete a project and all its tasks from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE item_id = ?", (project_id,))
        conn.commit()


# ── Task CRUD ────────────────────────────────────────────────────────────────

def save_task(task: Task, project_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (
                project_id, title, description, deadline, priority, completed
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                task.title,
                task.description,
                task.deadline.isoformat(),
                task.priority,
                int(task.completed),
            ),
        )
        conn.commit()

        last_id = cursor.lastrowid
        if last_id is None:
            raise RuntimeError("Failed to retrieve last inserted ID")

        return last_id

def load_tasks_for_project(project_id: int) -> list[Task]:
    """
    Fetch all tasks for a given project_id.
    Returns a list of Task instances.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY item_id",
            (project_id,),
        )
        rows = cursor.fetchall()

    tasks: list[Task] = []
    for row in rows:
        task = Task(
            item_id=row["item_id"],
            title=row["title"],
            description=row["description"] or "",
            deadline=date.fromisoformat(row["deadline"]),
            priority=row["priority"],
        )
        task.completed = bool(row["completed"])
        tasks.append(task)

    return tasks


def update_task(task: Task) -> None:
    """Update an existing task record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, deadline = ?, priority = ?, completed = ?
            WHERE item_id = ?
            """,
            (
                task.title,
                task.description,
                task.deadline.isoformat(),
                task.priority,
                int(task.completed),
                task.item_id,
            ),
        )
        conn.commit()


def delete_task(task_id: int) -> None:
    """Delete a single task from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE item_id = ?", (task_id,))
        conn.commit()