from calendar_client import (
    get_today_events,
    get_tomorrow_events,
    format_events,
)

print("Hello! I am your personal calendar assistant. I can help you check your schedule, find free time, and create new events. How can I help you today?")

while True:
    question = input("\nYou: ").lower()

    if "today" in question:
        events = get_today_events()
        print("Assistant: ", format_events(events))

    elif "tomorrow" in question:
        events = get_tomorrow_events()
        print("Assistant: ", format_events(events))

    elif question in ["quit", "exit", "bye", "that's all"]:
        print("Assistant: Goodbye!")
        break

    # elif "where" in question:
    #     events = get_tommo