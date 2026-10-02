import datetime
import re
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/New_York")

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
}


def parse_intent(text):
    text = text.lower().strip()

    # Exit
    if text in ["quit", "exit", "bye", "goodbye", "that's all", "thats all"]:
        return {
            "intent": "exit"
        }

    # Location questions should come before "next"
    # because "Where is my next event?" contains both.
    if "where" in text or "location" in text:
        return {
            "intent": "event_location"
        }

    # Creating an event should come before today/tomorrow,
    # because "schedule something tomorrow" contains "tomorrow".
    if ("schedule" in text or "create" in text or "add" in text):
        return {
            "intent": "create_event"
        }

    # Weekly free time
    if ("free" in text and "week" in text
        and (
            "how many hours" in text
            or "how much time" in text
        )
    ):
        return {
            "intent": "free_hours_week"
        }

    # Ask when free during a particular day
    if "free" in text and (
        "when" in text
        or "what time" in text
        or "what times" in text
    ):
        if "tomorrow" in text:
            return {
                "intent": "free_intervals_day",
                "day": "tomorrow"
            }

        if "today" in text:
            return {
                "intent": "free_intervals_day",
                "day": "today"
            }

    # Next event/class
    if (
        "next event" in text
        or "next class" in text
        or "what's next" in text
        or "whats next" in text
    ):
        return {
            "intent": "next_event"
        }

    # Tomorrow
    if "tomorrow" in text:
        return {
            "intent": "tomorrow_events"
        }

    # Today
    if "today" in text:
        return {
            "intent": "today_events"
        }

    return {
        "intent": "unknown"
    }


def parse_create_event(text):
    """
    Example supported input:

    Schedule a two-hour study session tomorrow at 6 PM
    Create a one hour gym session tomorrow at 7:30 PM
    Add a 2 hour meeting today at 4 PM
    """

    text = text.lower().strip()

    pattern = (
        r"(?:schedule|create|add)"
        r"(?: me)?"
        r"(?: a| an)?\s+"
        r"(?P<duration>\d+|one|two|three|four|five|six)"
        r"[- ]?hour(?:s)?"
        r"[- ]*"
        r"(?P<title>.+?)\s+"
        r"(?P<day>today|tomorrow)\s+"
        r"(?:at|after)\s+"
        r"(?P<hour>\d{1,2})"
        r"(?::(?P<minute>\d{2}))?\s*"
        r"(?P<ampm>am|pm)"
    )

    match = re.search(pattern, text)

    if not match:
        return None

    # Duration
    duration_text = match.group("duration")

    if duration_text.isdigit():
        duration_hours = int(duration_text)
    else:
        duration_hours = NUMBER_WORDS[duration_text]

    # Day
    today = datetime.date.today()

    if match.group("day") == "tomorrow":
        day = today + datetime.timedelta(days=1)
    else:
        day = today

    # Time
    hour = int(match.group("hour"))
    minute = int(match.group("minute") or 0)
    ampm = match.group("ampm")

    if ampm == "pm" and hour != 12:
        hour += 12

    if ampm == "am" and hour == 12:
        hour = 0

    start = datetime.datetime.combine(
        day,
        datetime.time(hour, minute),
        tzinfo=TIMEZONE
    )

    end = start + datetime.timedelta(hours=duration_hours)

    return {
        "title": match.group("title").strip().title(),
        "start": start,
        "end": end,
    }