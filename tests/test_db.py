import sqlite3

import pytest

import db


def test_tables_created_successfully(setup_test_db):
    """
    Verifies that all required tables exist in the database schema
    after initialization.
    """
    expected_tables = {
        "projects",
        "milestones",
        "priorities",
        "tags",
        "tasks",
        "task_tags",
    }

    with sqlite3.connect(db.DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        actual_tables = {row[0] for row in cursor.fetchall()}

    assert expected_tables.issubset(actual_tables), (
        f"Missing tables! Expected: {expected_tables}, Found: {actual_tables}"
    )


def test_project_insert(setup_test_db):
    """something really descriptive about inserting a row"""
    db.create_record(
        db.ProjectQueries.INSERT_PROJECT,
        ("Test Project", "Testing the DB", "2026-01-01", "2026-12-31"),
    )
    projects = db.fetch_record(db.ProjectQueries.FETCH_PROJECT_ALL)

    assert len(projects) == 1
    assert projects[0][2] == "Test Project"
