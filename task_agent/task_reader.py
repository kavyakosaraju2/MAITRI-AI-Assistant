from googleapiclient.discovery import build
from datetime import datetime

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

    service = build("tasks", "v1", credentials=creds)

    task_body = {
        "title": title
    }

    # 🔥 Only add due date if it exists
    if due_date:
        if isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d")
                task_body["due"] = due_date.isoformat() + "Z"
            except:
                pass
        elif isinstance(due_date, datetime):
            task_body["due"] = due_date.isoformat() + "Z"

    service.tasks().insert(
        tasklist="@default",
        body=task_body
    ).execute()

    print("📝 Task created successfully.")
