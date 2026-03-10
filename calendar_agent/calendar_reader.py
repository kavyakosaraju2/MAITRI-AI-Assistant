from googleapiclient.discovery import build
from datetime import datetime


def read_upcoming_events(creds, max_results=10):

    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    return events


def delete_calendar_event(creds, event_id):

    service = build("calendar", "v3", credentials=creds)

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()

    return "The meeting has been deleted from your calendar."



def find_event_for_deletion(events, query):

    query = query.lower()

    # 1️⃣ Exact title match
    for event in events:
        title = event.get("summary", "").lower()

        if title in query:
            return event

    # 2️⃣ Partial match
    for event in events:
        title = event.get("summary", "").lower()

        if any(word in title for word in query.split()):
            return event

    # 3️⃣ If user only says "the meeting", return most recent meeting
    if "meeting" in query and events:
        return events[0]

    return None

def update_calendar_event(creds, event_id, new_time):

    from googleapiclient.discovery import build
    from datetime import datetime, timedelta

    service = build("calendar", "v3", credentials=creds)

    event = service.events().get(
        calendarId="primary",
        eventId=event_id
    ).execute()

    start_time = datetime.fromisoformat(new_time)
    end_time = start_time + timedelta(hours=1)

    event["start"]["dateTime"] = start_time.isoformat()
    event["end"]["dateTime"] = end_time.isoformat()

    service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()

    return "The meeting has been rescheduled."
def rename_calendar_event(creds, event_id, new_title):
    service = build("calendar", "v3", credentials=creds)

    event = service.events().get(
        calendarId="primary",
        eventId=event_id
    ).execute()

    event["summary"] = new_title

    service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()

    return "The meeting title has been updated."