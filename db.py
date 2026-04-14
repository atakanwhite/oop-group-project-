# db.py
# Database module for the Project Management App.
# Handles all SQLite operations: creating tables, saving, loading,
# updating and deleting Project and Task records.
# Demonstrates: separate module, use of data structures (dict, list).

import sqlite3
from datetime import date
from models import Project, Task

DB_FILE = "project_manager.db"


def get_connection() -> sqlite3.Connection:
    """Open and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # allows dict-like row access
    return conn


def initialize_db():
    """
    Create the projects and tasks tables if they don't already exist.
    Called once at application startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            deadline    TEXT    NOT NULL,
            completed   INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            description TEXT,
            deadline   TEXT    NOT NULL,
            priority   TEXT    NOT NULL DEFAULT 'medium',
            completed  INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(item_id)
        )
    """)

    conn.commit()
    conn.close()


# ── Project CRUD ────────────────────────────────────────────────────────────

def save_project(project: Project) -> int:
    """
    Insert a new Project into the database.
    Returns the auto-assigned item_id.
    Object passed as function argument (requirement j).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (title, description, deadline, completed) VALUES (?, ?, ?, ?)",
        (project.title, project.description, str(project.deadline), int(project.completed))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def load_all_projects() -> list:
    """
    Fetch all projects from the database.
    Returns a list of Project instances (list as data structure).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    conn.close()

    projects = []
    for row in rows:
        proj = Project(
            item_id=row["item_id"],
            title=row["title"],
            description=row["description"],
            deadline=date.fromisoformat(row["deadline"]),
        )
        proj.completed = bool(row["completed"])
        # load tasks belonging to this project
        proj.tasks = load_tasks_for_project(proj.item_id)
        projects.append(proj)
    return projects


def update_project(project: Project):
    """
    Update an existing project record in the database.
    Object passed as function argument.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE projects
           SET title=?, description=?, deadline=?, completed=?
           WHERE item_id=?""",
        (project.title, project.description, str(project.deadline),
         int(project.completed), project.item_id)
    )
    conn.commit()
    conn.close()


def delete_project(project_id: int):
    """Delete a project and all its tasks from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
    cursor.execute("DELETE FROM projects WHERE item_id=?", (project_id,))
    conn.commit()
    conn.close()


# ── Task CRUD ────────────────────────────────────────────────────────────────

def save_task(task: Task, project_id: int) -> int:
    """
    Insert a new Task linked to a project.
    Returns the auto-assigned item_id.
    Object passed as function argument.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tasks (project_id, title, description, deadline, priority, completed)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (project_id, task.title, task.description,
         str(task.deadline), task.priority, int(task.completed))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def load_tasks_for_project(project_id: int) -> list:
    """
    Fetch all tasks for a given project_id.
    Returns a list of Task instances.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE project_id=?", (project_id,))
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        task = Task(
            item_id=row["item_id"],
            title=row["title"],
            description=row["description"],
            deadline=date.fromisoformat(row["deadline"]),
            priority=row["priority"],
        )
        task.completed = bool(row["completed"])
        tasks.append(task)
    return tasks


def update_task(task: Task):
    """Update an existing task record. Object passed as function argument."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE tasks
           SET title=?, description=?, deadline=?, priority=?, completed=?
           WHERE item_id=?""",
        (task.title, task.description, str(task.deadline),
         task.priority, int(task.completed), task.item_id)
    )
    conn.commit()
    conn.close()


def delete_task(task_id: int):
    """Delete a single task from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE item_id=?", (task_id,))
    conn.commit()
    conn.close()

