from googleapiclient.discovery import build
from datetime import datetime

def read_upcoming_events(creds, max_results=5):
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

    #print("\n📅 Upcoming Calendar Events:\n")

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        title = event.get("summary", "No Title")

        #print(f"Event: {title}")
        #print(f"Starts at: {start}")
        #print("-" * 40)

    return events

from datetime import timedelta


from datetime import datetime

def create_calendar_event(creds, title, event_datetime):

    service = build("calendar", "v3", credentials=creds)

    # 🔥 Convert string to datetime if needed
    if isinstance(event_datetime, str):
        event_datetime = datetime.strptime(event_datetime, "%Y-%m-%d %H:%M")

    event = {
        "summary": title,
        "start": {
            "dateTime": event_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": event_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    service.events().insert(calendarId="primary", body=event).execute()

    print("📅 Calendar event created successfully.")

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return created_event.get("htmlLink")
