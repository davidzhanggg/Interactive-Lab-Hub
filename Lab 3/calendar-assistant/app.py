import datetime

from calendar_client import (
    get_today_events,
    get_tomorrow_events,
    get_next_event,
    get_free_hours_this_week,
    get_free_intervals_for_day,
    is_free,
    create_event,
    format_events,
    format_location,
    friendly_title,
)

from intent_parser import parse_intent, parse_create_event


pending_event = None
last_event = None

print(
    "Hello! I am your personal calendar assistant. "
    "I can help you check your schedule, find free time, "
    "and create new events. How can I help you today?"
)


while True:
    question = input("\nYou: ").strip().lower()

    # --------------------------------------------------
    # 1. Handle confirmation for a pending event
    # --------------------------------------------------
    if pending_event is not None:

        if question in ["yes", "yeah", "yep", "sure", "ok", "okay",]:
            create_event(pending_event["title"], pending_event["start"], pending_event["end"],)

            print("Assistant:", f"Done. I created {pending_event['title']}.")
            pending_event = None
            continue

        elif question in ["no", "nope", "cancel", "never mind",]:
            print("Assistant:", "Okay, I won't create it.")
            pending_event = None
            continue

        else:
            print("Assistant:", "Please say yes or no.")
            continue

    # --------------------------------------------------
    # 2. Understand what the user wants
    # --------------------------------------------------
    result = parse_intent(question)
    intent = result["intent"]

    # --------------------------------------------------
    # Today's schedule
    # --------------------------------------------------
    if intent == "today_events":
        events = get_today_events()

        print("Assistant:", format_events(events))

        if len(events) == 1:
            last_event = events[0]
        else:
            last_event = None

    # --------------------------------------------------
    # Tomorrow's schedule
    # --------------------------------------------------
    elif intent == "tomorrow_events":
        events = get_tomorrow_events()
        print("Assistant:", format_events(events))

        if len(events) == 1:
            last_event = events[0]
        else:
            last_event = None

    # --------------------------------------------------
    # Next event
    # --------------------------------------------------
    elif intent == "next_event":
        event = get_next_event()

        if event:
            print("Assistant:", format_events([event], include_date=True, include_location=True))
            last_event = event
        else:
            print("Assistant:", "You don't have any upcoming events.")

    # --------------------------------------------------
    # Location
    # --------------------------------------------------
    elif intent == "event_location":

        if last_event:
            title = friendly_title(last_event.get("summary", "Untitled event"))
            location = last_event.get("location")

            if location:
                print("Assistant:", f"{title} is in {location}.")
            else:
                print("Assistant:", f"There is no location listed for {title}.")

        else:
            print("Assistant:", "I'm not sure which event you're asking about.")

    # --------------------------------------------------
    # Free hours this week
    # --------------------------------------------------
    elif intent == "free_hours_week":
        hours = get_free_hours_this_week()

        print("Assistant:", f"You have approximately {hours:.1f} free hours this week between 9 AM and 9 PM.")

    # --------------------------------------------------
    # When am I free today/tomorrow?
    # --------------------------------------------------
    elif intent == "free_intervals_day":
        if result["day"] == "tomorrow":
            day = (datetime.date.today() + datetime.timedelta(days=1))
            day_name = "tomorrow"

        else:
            day = datetime.date.today()
            day_name = "today"

        free_intervals = get_free_intervals_for_day(day)

        if not free_intervals:
            print("Assistant:", f"You don't have any free time {day_name} between 9 AM and 9 PM.")

        else:
            formatted_intervals = []

            for start, end in free_intervals:
                formatted_intervals.append(f"{start.strftime('%-I:%M %p')} to {end.strftime('%-I:%M %p')}")

            print(
                "Assistant:",
                f"You are free {day_name} from "
                + ", ".join(formatted_intervals)
                + "."
            )

    # --------------------------------------------------
    # Create event
    # --------------------------------------------------
    elif intent == "create_event":

        event_data = parse_create_event(question)

        if event_data is None:
            print("Assistant: Sorry, I couldn't understand the event details.")
            continue

        start = event_data["start"]
        end = event_data["end"]

        if is_free(start, end):
            # Do NOT create it yet.
            # Wait until the user confirms.
            pending_event = event_data

            print(
                "Assistant:",
                f"You're free from "
                f"{start.strftime('%-I:%M %p')} to "
                f"{end.strftime('%-I:%M %p')}. "
                f"Would you like me to create "
                f"{event_data['title']}?"
            )

        else:
            print("Assistant: You already have something scheduled during that time.")

    # --------------------------------------------------
    # Exit
    # --------------------------------------------------
    elif intent == "exit":
        print("Assistant: Goodbye!")
        break

    # --------------------------------------------------
    # Unknown
    # --------------------------------------------------
    else:
        print("Assistant: Sorry, I didn't understand that.")