from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

def create_calendar_event(creds, title, start_time):

    service = build("calendar", "v3", credentials=creds)

    tz = pytz.timezone("Asia/Kolkata")

    start_dt = datetime.fromisoformat(start_time)

    if start_dt.tzinfo is None:
        start_dt = tz.localize(start_dt)
    else:
        start_dt = start_dt.astimezone(tz)

    end_dt = start_dt + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }

    service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return "Event created successfully."