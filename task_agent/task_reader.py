from googleapiclient.discovery import build

def read_tasks(creds):
    service = build("tasks", "v1", credentials=creds)

    results = service.tasklists().list().execute()
    tasklists = results.get("items", [])

    all_tasks = []

    for tasklist in tasklists:
        tasks = service.tasks().list(tasklist=tasklist["id"]).execute()
        items = tasks.get("items", [])

        for task in items:
            title = task.get("title", "No Title")
            status = task.get("status", "unknown")
            due = task.get("due", "No due date")
            if due != "No due date":
                due = due[:10]

            #print(f"- {title} [{status}] | Due: {due}")
            all_tasks.append(task)

    return all_tasks

def create_task(creds, title, due_date):
    from googleapiclient.discovery import build

    service = build("tasks", "v1", credentials=creds)

    task = {
        "title": title,
    }

    if due_date:
        task["due"] = due_date.isoformat() + "Z"

    created_task = service.tasks().insert(
        tasklist="@default",
        body=task
    ).execute()

    return created_task.get("id")
