import typer
from db import (
    create_record,
    fetch_record,
    update_record,
    delete_record,
    ProjectQueries,
    TaskQueries,
)

app = typer.Typer()


# PROJECTS 

@app.command()
def project_create(name: str, description: str = ""):
    create_record(
        ProjectQueries.INSERT_PROJECT,
        (name, description, None, None),
    )
    print("Project created")


@app.command()
def project_list():
    projects = fetch_record(ProjectQueries.FETCH_PROJECT_ALL)
    for p in projects:
        print(f"{p[0]} | {p[2]} | complete={p[6]}")


#TASKS 

@app.command()
def task_add(
    project_id: int,
    name: str,
    priority_id: int = 1,
    parent_task_id: int | None = None,
):
    create_record(
        TaskQueries.INSERT_TASK,
        (
            project_id,
            None,
            parent_task_id,
            priority_id,
            name,
            "",
            None,
            None,
        ),
    )
    print("Task added")


@app.command()
def task_list(project_id: int):
    tasks = fetch_record(TaskQueries.FETCH_TASKS_BY_PROJECT, (project_id,))
    for t in tasks:
        indent = "  " if t[3] else ""
        print(f"{indent}{t[0]} | {t[6]} | done={t[10]}")


@app.command()
def task_done(task_id: int):
    task = fetch_record(TaskQueries.FETCH_TASK, (task_id,))
    if not task:
        print("Task not found")
        return

    t = task[0]
    update_record(
        TaskQueries.UPDATE_TASK,
        (
            t[1], t[2], t[3], t[4],
            t[6], t[7], t[8], t[9],
            1,  # complete
            task_id,
        ),
    )
    print("Task marked complete")


if __name__ == "__main__":
    app()
