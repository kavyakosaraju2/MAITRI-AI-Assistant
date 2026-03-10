from datetime import datetime


def check_calendar_conflict(new_time, events):
    try:
        new_event_time = datetime.fromisoformat(new_time)

        if new_event_time.tzinfo is not None:
            new_event_time = new_event_time.replace(tzinfo=None)

    except:
        new_event_time = datetime.strptime(new_time, "%Y-%m-%d %H:%M")

    for event in events:

        start = event.get("start", {})
        start_time = start.get("dateTime") or start.get("date")

        if not start_time:
            continue

        try:
            existing_time = datetime.fromisoformat(start_time)

            if existing_time.tzinfo is not None:
                existing_time = existing_time.replace(tzinfo=None)

            difference = abs((existing_time - new_event_time).total_seconds())

            if difference < 3600:
                return event

        except Exception:
            continue

        