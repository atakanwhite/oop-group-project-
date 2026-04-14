# app.py
# Main entry point for the Project Management App.
# Provides a command-line interface for managing projects and tasks.
# Demonstrates: multiple module imports, creating multiple instances,
#               passing objects as arguments, use of data structures.

from datetime import date
from models import Project, Task
import db


def print_separator():
    """Print a divider line for readability."""
    print("-" * 55)


def parse_date(date_str: str) -> date:
    """
    Parse a date string in YYYY-MM-DD format.
    Returns a date object, or None on invalid input.
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        print("  Invalid date format. Please use YYYY-MM-DD.")
        return None


# ── Dashboard ────────────────────────────────────────────────────────────────

def show_dashboard(projects: list):
    """
    Display the dashboard: overview, upcoming deadlines, recent activity.
    Accepts a list of Project objects (list as data structure, objects as args).
    """
    print_separator()
    print("  DASHBOARD — OVERVIEW")
    print_separator()

    if not projects:
        print("  No projects yet. Create one to get started!")
        return

    # overview: use polymorphic status_summary() on all items
    for proj in projects:
        print(" ", proj.status_summary())  # polymorphism: Project.status_summary()
        for task in proj.tasks:
            print("    •", task.status_summary())  # polymorphism: Task.status_summary()

    print_separator()
    print("  UPCOMING DEADLINES (all projects)")
    all_upcoming = []
    for proj in projects:
        all_upcoming.extend(proj.upcoming_deadlines())  # list extension
    all_upcoming.sort(key=lambda t: t.deadline)
    if all_upcoming:
        for task in all_upcoming[:5]:
            print(f"    {task.deadline}  {task.title}")
    else:
        print("  No upcoming tasks.")

    print_separator()
    print("  RECENT ACTIVITY (last added tasks)")
    for proj in projects:
        recent = proj.recent_activity()
        if recent:
            print(f"  [{proj.title}]")
            for task in recent:
                print(f"    • {task.title}")


# ── Project actions ──────────────────────────────────────────────────────────

def create_project(projects: list):
    """Prompt the user to create a new project and save it to the database."""
    print_separator()
    print("  CREATE PROJECT")
    title = input("  Title: ").strip()
    description = input("  Description: ").strip()
    deadline_str = input("  Deadline (YYYY-MM-DD): ").strip()
    deadline = parse_date(deadline_str)
    if not deadline:
        return

    # create a new Project instance (multiple instances requirement)
    proj = Project(item_id=0, title=title, description=description, deadline=deadline)
    proj.item_id = db.save_project(proj)  # persist and get real ID
    projects.append(proj)
    print(f"  ✓ Project '{title}' created (ID {proj.item_id}).")


def view_projects(projects: list):
    """List all projects with their status summaries."""
    print_separator()
    print("  ALL PROJECTS")
    if not projects:
        print("  No projects found.")
        return
    for proj in projects:
        print(f"  [{proj.item_id}] {proj.status_summary()}")


def edit_project(projects: list):
    """Edit the title, description or deadline of an existing project."""
    view_projects(projects)
    try:
        pid = int(input("  Enter project ID to edit: "))
    except ValueError:
        print("  Invalid ID.")
        return

    proj = next((p for p in projects if p.item_id == pid), None)
    if not proj:
        print("  Project not found.")
        return

    print(f"  Editing '{proj.title}' (leave blank to keep current value)")
    new_title = input(f"  Title [{proj.title}]: ").strip() or proj.title
    new_desc = input(f"  Description [{proj.description}]: ").strip() or proj.description
    new_dl_str = input(f"  Deadline [{proj.deadline}]: ").strip()
    new_deadline = parse_date(new_dl_str) if new_dl_str else proj.deadline

    proj.title = new_title
    proj.description = new_desc
    proj.deadline = new_deadline
    db.update_project(proj)
    print("  ✓ Project updated.")


def delete_project(projects: list):
    """Delete a project and all its tasks."""
    view_projects(projects)
    try:
        pid = int(input("  Enter project ID to delete: "))
    except ValueError:
        print("  Invalid ID.")
        return

    proj = next((p for p in projects if p.item_id == pid), None)
    if not proj:
        print("  Project not found.")
        return

    confirm = input(f"  Delete '{proj.title}' and all its tasks? (y/n): ").strip().lower()
    if confirm == "y":
        db.delete_project(proj.item_id)
        projects.remove(proj)
        print("  ✓ Project deleted.")


# ── Task actions ─────────────────────────────────────────────────────────────

def select_project(projects: list):
    """Helper: prompt user to pick a project by ID. Returns Project or None."""
    view_projects(projects)
    try:
        pid = int(input("  Enter project ID: "))
    except ValueError:
        return None
    return next((p for p in projects if p.item_id == pid), None)


def create_task(projects: list):
    """Create a new task inside a chosen project."""
    print_separator()
    print("  CREATE TASK")
    proj = select_project(projects)
    if not proj:
        print("  Project not found.")
        return

    title = input("  Task title: ").strip()
    description = input("  Description: ").strip()
    deadline_str = input("  Deadline (YYYY-MM-DD): ").strip()
    deadline = parse_date(deadline_str)
    if not deadline:
        return
    priority = input("  Priority (low/medium/high) [medium]: ").strip() or "medium"

    try:
        # create a new Task instance and pass it as argument to add_task (req i)
        task = Task(item_id=0, title=title, description=description,
                    deadline=deadline, priority=priority)
        task.item_id = db.save_task(task, proj.item_id)
        proj.add_task(task)  # object passed as function argument
        print(f"  ✓ Task '{title}' added to '{proj.title}' (ID {task.item_id}).")
    except ValueError as e:
        print(f"  Error: {e}")


def delete_task(projects: list):
    """Delete a task from a project."""
    print_separator()
    print("  DELETE TASK")
    proj = select_project(projects)
    if not proj:
        print("  Project not found.")
        return

    if not proj.tasks:
        print("  This project has no tasks.")
        return

    for t in proj.tasks:
        print(f"    [{t.item_id}] {t.title}")
    try:
        tid = int(input("  Enter task ID to delete: "))
    except ValueError:
        print("  Invalid ID.")
        return

    if proj.remove_task(tid):
        db.delete_task(tid)
        print("  ✓ Task deleted.")
    else:
        print("  Task not found.")


def track_progress(projects: list):
    """Show completion progress for a selected project."""
    print_separator()
    print("  TRACK PROGRESS")
    proj = select_project(projects)
    if not proj:
        print("  Project not found.")
        return

    pct = int(proj.completion_rate() * 100)
    print(f"\n  Project : {proj.title}")
    print(f"  Progress: {'█' * (pct // 5)}{'░' * (20 - pct // 5)} {pct}%")
    print(f"  Tasks   : {sum(1 for t in proj.tasks if t.completed)}/{len(proj.tasks)} completed\n")
    for task in proj.tasks:
        print(" ", task.status_summary())


def mark_complete(projects: list):
    """Mark a task or an entire project as complete."""
    print_separator()
    print("  MARK COMPLETE")
    print("  1. Mark a task complete")
    print("  2. Mark entire project complete")
    choice = input("  Choose (1/2): ").strip()

    proj = select_project(projects)
    if not proj:
        print("  Project not found.")
        return

    if choice == "1":
        for t in proj.tasks:
            print(f"    [{t.item_id}] {t.title} {'✓' if t.completed else ''}")
        try:
            tid = int(input("  Enter task ID: "))
        except ValueError:
            print("  Invalid ID.")
            return
        task = proj.get_task(tid)
        if task:
            task.mark_complete()
            db.update_task(task)
            print("  ✓ Task marked complete.")
        else:
            print("  Task not found.")
    elif choice == "2":
        proj.mark_complete()
        db.update_project(proj)
        print("  ✓ Project marked complete.")


# ── Main menu ─────────────────────────────────────────────────────────────────

def main():
    """
    Application entry point.
    Initializes the database, loads data, and runs the main menu loop.
    """
    db.initialize_db()
    projects = db.load_all_projects()  # list of Project instances

    menu = {
        "1": ("Dashboard",        lambda: show_dashboard(projects)),
        "2": ("View Projects",    lambda: view_projects(projects)),
        "3": ("Create Project",   lambda: create_project(projects)),
        "4": ("Edit Project",     lambda: edit_project(projects)),
        "5": ("Delete Project",   lambda: delete_project(projects)),
        "6": ("Create Task",      lambda: create_task(projects)),
        "7": ("Delete Task",      lambda: delete_task(projects)),
        "8": ("Track Progress",   lambda: track_progress(projects)),
        "9": ("Mark Complete",    lambda: mark_complete(projects)),
        "0": ("Exit",             None),
    }

    print("\n  Welcome to Project Manager!\n")

    while True:
        print_separator()
        print("  MAIN MENU")
        print_separator()
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")
        print_separator()

        choice = input("  Select option: ").strip()

        if choice == "0":
            print("  Goodbye!")
            break
        elif choice in menu:
            _, action = menu[choice]
            action()
        else:
            print("  Invalid option, try again.")


if __name__ == "__main__":
    main()

