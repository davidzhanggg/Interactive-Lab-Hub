import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]


COURSE_NAMES = {
    "CS 5424": "Interactive Device Design",
    "CS 5854": "Networks and Markets",
    "TECH 5900": "Product Studio",
    "TECHIE 5310": "Business Fundamentals",
    "CS 5650": "Virtual and Augmented Reality",
}


def get_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)

# Returns the events you have scheduled for a particular day
def get_events_for_day(day):
    service = get_service()

    # Beginning of requested day in local timezone
    start = datetime.datetime.combine(day, datetime.time.min).astimezone()
    
    # Beginning of following day
    end = start + datetime.timedelta(days=1)

    result = service.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return result.get("items", [])

def get_today_events():
    today = datetime.date.today()
    return get_events_for_day(today)

def get_tomorrow_events():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return get_events_for_day(tomorrow)

def get_next_event():


def find_event(name):


def get_event_location(event):
    return event.get("location", "No location specified")


def is_free(start, end):


def get_free_time_this_week():


def create_event(title, start, end):

# Convert the course code into the course name
def friendly_title(title):
    for code, name in COURSE_NAMES.items():
        if code in title:
            return name
    return title

# Formats the information of an event
def format_events(events, include_location=False):
    if not events:
        return "You don't have anything scheduled."

    parts = []

    for event in events:
        title = friendly_title(event.get("summary", "Untitled event"))
        start = event["start"]

        if "dateTime" in start:
            dt = datetime.datetime.fromisoformat(start["dateTime"])
            time_string = dt.strftime("%-I:%M %p")
        else:
            time_string = "all day"

        text = f"{title} at {time_string}"

        if include_location:
            location = event.get("location")
            if location:
                text += f" in {location}"
        parts.append(text)
    
    return ", ".join(parts)

# Formats the location of a given event
def format_location(event):
    location = event.get("location")
    if location:
        return location
    return "There is no location listed for that event."

if __name__ == "__main__":
    print("TODAY:")
    print(format_events(get_today_events()))

    print("\nTOMORROW:")
    print(format_events(get_tomorrow_events()))        
