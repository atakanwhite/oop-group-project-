import sqlite3

create_tables = [
    """
    CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY,
    created_at DATE NOT NULL,
    project_name TEXT,
    project_description TEXT,
    date_start DATE,
    date_end DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS milestones (
    milestone_id INTEGER PRIMARY KEY,
    project_id INTEGER,
    created_at DATE,
    milestone_name TEXT,
    date_start DATE,
    date_end DATE,
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY,
    project_id INTEGER,
    milestone_id INTEGER,
    parent_task_id INTEGER,
    created_at DATE,
    task_name TEXT,
    task_description TEXT,
    date_start DATE,
    date_end DATE,
    FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
    FOREIGN KEY (milestone_id) REFERENCES milestones (milestone_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE
    )
    """,
]


def init_db() -> None:
    try:
        with sqlite3.connect("snek.db") as conn:
            cursor = conn.cursor()
            for c in create_tables:
                cursor.execute(c)
        print("Database initialized successfully.")
    except sqlite3.OperationalError as e:
        print(f"Failed to initialize Database: {e}")


init_db()
