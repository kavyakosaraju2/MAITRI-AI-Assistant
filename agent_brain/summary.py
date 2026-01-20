def generate_summary(emails, events, tasks):
    print("\n DAILY SUMMARY\n")

    email_count = len(emails)
    event_count = len(events)
    pending_tasks = [task for task in tasks if task["status"] != "completed"]
    task_count = len(pending_tasks)

    print(f"📧 You have {email_count} recent emails")
    print(f"📅 You have {event_count} upcoming calendar events")
    print(f"📋 You have {task_count} pending tasks")

    # Create spoken summary text
    summary_text = (
        f"You have {email_count} emails, "
        f"{event_count} calendar events, "
        f"and {task_count} pending tasks."
    )

    return summary_text
