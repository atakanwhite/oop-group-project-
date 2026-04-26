import sqlite3
from enum import Enum

DATABASE_FILE = "snekPM.db"


class CreateTables(Enum):
    CREATE_TABLE_PROJECTS = """
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            project_name TEXT NOT NULL,
            project_description TEXT,
            date_start DATE,
            date_end DATE,
            is_complete INTEGER DEFAULT 0
        )
    """

    CREATE_TABLE_MILESTONES = """
        CREATE TABLE IF NOT EXISTS milestones (
            milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            milestone_name TEXT NOT NULL,
            date DATE,
            FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
            UNIQUE(project_id, milestone_name)
        )
    """

    CREATE_TABLE_PRIORITIES = """
        CREATE TABLE IF NOT EXISTS priorities (
            priority_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            priority_name TEXT NOT NULL
        )
    """

    CREATE_TABLE_TAGS = """
        CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tag_name TEXT NOT NULL UNIQUE
        )
    """

    CREATE_TABLE_TASKS = """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            milestone_id INTEGER,
            parent_task_id INTEGER,
            priority_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            task_name TEXT NOT NULL,
            task_description TEXT,
            date_start DATE,
            date_end DATE,
            is_complete INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
            FOREIGN KEY (milestone_id) REFERENCES milestones (milestone_id) ON DELETE SET NULL,
            FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
            FOREIGN KEY (priority_id) REFERENCES priorities (priority_id)
        )
    """

    CREATE_TABLE_TASK_TAGS = """
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (task_id, tag_id),
            FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE
        );
    """


class ProjectQueries(Enum):
    INSERT_PROJECT = """
        INSERT INTO projects (
            project_name,
            project_description,
            date_start,
            date_end
        ) VALUES (?, ?, ?, ?)
    """
    UPDATE_PROJECT = """
        UPDATE projects
        SET project_name = ?,
            project_description = ?,
            date_start = ?,
            date_end = ?,
            is_complete = ?
        WHERE project_id = ?
    """
    DELETE_PROJECT = """
        DELETE FROM projects
        WHERE project_id = ?
    """
    FETCH_PROJECT = """
        SELECT project_id, created_at, project_name, project_description, date_start, date_end, is_complete
        FROM projects
        WHERE project_id = ?
    """
    FETCH_PROJECT_ALL = """
        SELECT project_id, created_at, project_name, project_description, date_start, date_end, is_complete
        FROM projects
    """


class TaskQueries(Enum):
    INSERT_TASK = """
        INSERT INTO tasks (
            project_id,
            milestone_id,
            parent_task_id,
            priority_id,
            task_name,
            task_description,
            date_start,
            date_end
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    UPDATE_TASK = """
        UPDATE tasks
        SET project_id = ?,
            milestone_id = ?,
            parent_task_id = ?,
            priority_id = ?,
            task_name = ?,
            task_description = ?,
            date_start = ?,
            date_end = ?,
            is_complete = ?
        WHERE task_id = ?
    """
    DELETE_TASK = """
        DELETE FROM tasks
        WHERE task_id = ?
    """
    FETCH_TASK = """
        SELECT task_id, project_id, milestone_id, parent_task_id, priority_id,
               created_at, task_name, task_description, date_start, date_end, is_complete
        FROM tasks
        WHERE task_id = ?
    """
    FETCH_TASK_ALL = """
        SELECT task_id, project_id, milestone_id, parent_task_id, priority_id,
               created_at, task_name, task_description, date_start, date_end, is_complete
        FROM tasks
    """
    FETCH_TASKS_BY_PROJECT = """
        SELECT task_id, project_id, milestone_id, parent_task_id, priority_id,
               created_at, task_name, task_description, date_start, date_end, is_complete
        FROM tasks
        WHERE project_id = ?
    """


class MilestoneQueries(Enum):
    INSERT_MILESTONE = """
        INSERT INTO milestones (
            project_id,
            milestone_name,
            date
        ) VALUES (?, ?, ?)
    """
    UPDATE_MILESTONE = """
        UPDATE milestones
        SET project_id = ?,
            milestone_name = ?,
            date = ?
        WHERE milestone_id = ?
    """
    DELETE_MILESTONE = """
        DELETE FROM milestones
        WHERE milestone_id = ?
    """
    FETCH_MILESTONE = """
        SELECT milestone_id, project_id, created_at, milestone_name, date
        FROM milestones
        WHERE milestone_id = ?
    """
    FETCH_MILESTONE_ALL = """
        SELECT milestone_id, project_id, created_at, milestone_name, date
        FROM milestones
    """


class TagQueries(Enum):
    INSERT_TAG = """
        INSERT INTO tags (tag_name)
        VALUES (?)
    """
    UPDATE_TAG = """
        UPDATE tags
        SET tag_name = ?
        WHERE tag_id = ?
    """
    DELETE_TAG = """
        DELETE FROM tags
        WHERE tag_id = ?
    """
    FETCH_TAG = """
        SELECT tag_id, created_at, tag_name
        FROM tags
        WHERE tag_id = ?
    """
    FETCH_TAG_ALL = """
        SELECT tag_id, created_at, tag_name
        FROM tags
    """


class PriorityQueries(Enum):
    INSERT_PRIORITY = """
        INSERT INTO priorities (priority_name)
        VALUES (?)
    """
    UPDATE_PRIORITY = """
        UPDATE priorities
        SET priority_name = ?
        WHERE priority_id = ?
    """
    DELETE_PRIORITY = """
        DELETE FROM priorities
        WHERE priority_id = ?
    """
    FETCH_PRIORITY = """
        SELECT priority_id, created_at, priority_name
        FROM priorities
        WHERE priority_id = ?
    """
    FETCH_PRIORITY_ALL = """
        SELECT priority_id, created_at, priority_name
        FROM priorities
    """


class TaskTagQueries(Enum):
    INSERT_TASK_TAG = """
        INSERT INTO task_tags (task_id, tag_id)
        VALUES (?, ?)
    """
    DELETE_TASK_TAG = """
        DELETE FROM task_tags
        WHERE task_id = ? AND tag_id = ?
    """
    FETCH_TAGS_FOR_TASK = """
        SELECT t.tag_id, t.tag_name, tt.created_at
        FROM tags t
        JOIN task_tags tt ON t.tag_id = tt.tag_id
        WHERE tt.task_id = ?
    """
    FETCH_TASKS_FOR_TAG = """
        SELECT t.task_id, t.task_name
        FROM tasks t
        JOIN task_tags tt ON t.task_id = tt.task_id
        WHERE tt.tag_id = ?
    """


def init_db() -> None:
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            for c in CreateTables:
                cursor.execute(c.value)
        print("Database initialized successfully.")
    except sqlite3.OperationalError as e:
        print(f"Failed to initialize Database: {e}")


def create_record(query: Enum, data: tuple = ()) -> int | None:
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute(query.value, data)
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Failed to create record: {e}")


def delete_record(query: Enum, data: tuple = ()) -> None:
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute(query.value, data)
    except sqlite3.Error as e:
        print(f"Failed to delete record: {e}")


def update_record(query: Enum, data: tuple = ()) -> None:
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute(query.value, data)
    except sqlite3.Error as e:
        print(f"Failed to update record: {e}")


def fetch_record(query: Enum, data: tuple = ()) -> list:
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute(query.value, data)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Failed to fetch record(s): {e}")
        return []


if __name__ == "__main__":
    init_db()
