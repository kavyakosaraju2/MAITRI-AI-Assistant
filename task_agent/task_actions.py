from googleapiclient.discovery import build

def create_task(creds, title, due_date):

    service = build("tasks", "v1", credentials=creds)

    task = {
        "title": title
    }

    if due_date:
        task["due"] = due_date + "T00:00:00.000Z"

    service.tasks().insert(
        tasklist="@default",
        body=task
    ).execute()

    return "Task created."
def task_exists(creds, title):

    from googleapiclient.discovery import build

    service = build("tasks", "v1", credentials=creds)

    tasklists = service.tasklists().list().execute()
    tasklist_id = tasklists["items"][0]["id"]

    tasks = service.tasks().list(tasklist=tasklist_id).execute()

    for t in tasks.get("items", []):

        if title.lower() in t.get("title", "").lower():
            return True

    return False