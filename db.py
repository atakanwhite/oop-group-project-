import sqlite3

DATABASE_FILE = "snekPM.db"


class Database:
    def __init__(self, db_file="DATABASE_FILE"):
        self.db = sqlite3.connect(db_file)
        self.cursor = self.db.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self) -> None:
        query = """
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                project_name TEXT NOT NULL,
                project_description TEXT,
                date_start DATE,
                date_end DATE,
                is_complete INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS milestones (
                milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                milestone_name TEXT NOT NULL,
                date DATE,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                UNIQUE(project_id, milestone_name)
            );

            CREATE TABLE IF NOT EXISTS priorities (
                priority_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                priority_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tags (
                tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tag_name TEXT NOT NULL UNIQUE
            );

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
            );

            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE
            );
        """

        self._run_query(query)

    def _run_query(self, query, *query_args) -> sqlite3.Cursor:
        result = self.cursor.execute(query, [*query_args])
        self.db.commit()
        return result


class ProjectQueries:
    def __init__(self, db):
        self.db = db

    def add_project(self, project: tuple) -> None:
        self.db._run_query(
            """
                INSERT INTO projects (
                project_name,
                project_description,
                date_start,
                date_end
            ) VALUES (?, ?, ?, ?)
        """,
            *project,
        )

    def update_project(self, project_data: tuple) -> None:
        self.db._run_query(
            """
            UPDATE projects
                SET project_name = ?,
                project_description = ?,
                date_start = ?,
                date_end = ?,
                is_complete = ?
            WHERE project_id = ?
        """,
            *project_data,
        )

    def delete_project(self, id: int) -> None:
        self.db._run_query(
            """
            DELETE FROM projects
            WHERE project_id = ?
        """,
            id,
        )

    def get_project(self, id: int):
        result = self.db._run_query(
            """
            SELECT *
            FROM projects
            WHERE project_id = ?
        """,
            id,
        )
        return result.fetchone()

    def get_all_projects(self) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT * FROM projects
        """
        )
        return result.fetchall()


class TaskQueries:
    def __init__(self, db) -> None:
        self.db = db

    def add_task(self, task: tuple) -> None:
        self.db._run_query(
            """
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
        """,
            *task,
        )

    def update_task(self, task_data: tuple) -> None:
        self.db._run_query(
            """
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
        """,
            *task_data,
        )

    def delete_task(self, id: int) -> None:
        self.db._run_query(
            """
            DELETE FROM tasks
            WHERE task_id = ?
        """,
            id,
        )

    def get_task(self, id: int):
        result = self.db._run_query(
            """
                SELECT *
                FROM tasks
                WHERE task_id = ?
            """,
            id,
        )
        return result.fetchone()

    def get_all_tasks(self) -> list[tuple]:
        result = self.db._run_query(
            """
                SELECT *
                FROM tasks
            """
        )
        return result.fetchall()

    def fetch_tasks_by_project(self, id: int) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM tasks
            WHERE project_id = ?
        """,
            id,
        )
        return result.fetchall()

    def fetch_subtasks(self, id: int) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM tasks
            WHERE parent_task_id = ?
        """,
            id,
        )
        return result.fetchall()


class MilestoneQueries:
    def __init__(self, db) -> None:
        self.db = db

    def add_milestone(self, milestone_data: tuple) -> None:
        self.db._run_query(
            """
            INSERT INTO milestones (
                project_id,
                milestone_name,
                date
            ) VALUES (?, ?, ?)
        """,
            *milestone_data,
        )

    def update_milestone(self, milestone_data: tuple) -> None:
        self.db._run_query(
            """
            UPDATE milestones
            SET project_id = ?,
                milestone_name = ?,
                date = ?
            WHERE milestone_id = ?
        """,
            *milestone_data,
        )

    def delete_milestone(self, id: int) -> None:
        self.db._run_query(
            """
            DELETE FROM milestones
            WHERE milestone_id = ?
        """,
            id,
        )

    def get_milestone(self, id: int):
        result = self.db._run_query(
            """
            SELECT *
            FROM milestones
            WHERE milestone_id = ?
        """,
            id,
        )
        return result.fetchone()

    def get_all_milestones(self) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM milestones
        """
        )
        return result.fetchall()

    def fetch_milestones_by_project(self, id: int) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM milestones
            WHERE project_id = ?
        """,
            id,
        )
        return result.fetchall()


class TagQueries:
    def __init__(self, db) -> None:
        self.db = db

    def add_tag(self, tag_data: tuple) -> None:
        self.db._run_query(
            """
            INSERT INTO tags (tag_name)
            VALUES (?)
        """,
            *tag_data,
        )

    def update_tag(self, tag_data: tuple) -> None:
        self.db._run_query(
            """
            UPDATE tags
            SET tag_name = ?
            WHERE tag_id = ?
        """,
            *tag_data,
        )

    def delete_tag(self, id: int) -> None:
        self.db._run_query(
            """
            DELETE FROM tags
            WHERE tag_id = ?
        """,
            id,
        )

    def get_tag(self, id: int):
        result = self.db._run_query(
            """
            SELECT *
            FROM tags
            WHERE tag_id = ?
        """,
            id,
        )
        return result.fetchone()

    def get_all_tags(self) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM tags
        """
        )
        return result.fetchall()


class PriorityQueries:
    def __init__(self, db) -> None:
        self.db = db

    def add_priority(self, priority_data: tuple) -> None:
        self.db._run_query(
            """
            INSERT INTO priorities (priority_name)
            VALUES (?)
        """,
            *priority_data,
        )

    def update_priority(self, priority_data: tuple) -> None:
        self.db._run_query(
            """
            UPDATE priorities
            SET priority_name = ?
            WHERE priority_id = ?
        """,
            *priority_data,
        )

    def delete_priority(self, id: int) -> None:
        self.db._run_query(
            """
            DELETE FROM priorities
            WHERE priority_id = ?
        """,
            id,
        )

    def get_priority(self, id: int):
        result = self.db._run_query(
            """
            SELECT *
            FROM priorities
            WHERE priority_id = ?
        """,
            id,
        )
        return result.fetchone()

    def get_all_priorities(self) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM priorities
        """
        )
        return result.fetchall()


class TaskTagQueries:
    def __init__(self, db) -> None:
        self.db = db

    def add_task_tag(self, task_tag_data: tuple) -> None:
        self.db._run_query(
            """
            INSERT INTO task_tags (task_id, tag_id)
            VALUES (?, ?)
        """,
            *task_tag_data,
        )

    def delete_task_tag(self, task_id: int, tag_id: int) -> None:
        self.db._run_query(
            """
            DELETE FROM task_tags
            WHERE task_id = ? AND tag_id = ?
        """,
            task_id,
            tag_id,
        )

    def get_tags_for_task(self, id: int) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM tags t
            JOIN task_tags tt ON t.tag_id = tt.tag_id
            WHERE tt.task_id = ?
        """,
            id,
        )
        return result.fetchall()

    def get_tasks_for_tag(self, id: int) -> list[tuple]:
        result = self.db._run_query(
            """
            SELECT *
            FROM tasks t
            JOIN task_tags tt ON t.task_id = tt.task_id
            WHERE tt.tag_id = ?
        """,
            id,
        )
        return result.fetchall()


if __name__ == "__main__":
    db = Database("snekPM.db")
