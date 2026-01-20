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

    print("\n📅 Upcoming Calendar Events:\n")

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        title = event.get("summary", "No Title")

        print(f"Event: {title}")
        print(f"Starts at: {start}")
        print("-" * 40)

    return events
