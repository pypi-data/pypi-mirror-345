"""CLI entry point for PPCalendar tool."""

import sys

from .ppcalendar import main  # Original calendar rendering logic
from .events import interactive_add_event, get_today_events


def show_today_events() -> None:
    """Print today's events from the CSV database."""
    events = get_today_events()
    if events:
        print("\n📅 Events for today:")
        for time, desc in events:
            print(f" - {time or 'All day'}: {desc}")
    else:
        print("\n📅 No events for today.")


def main_cli() -> None:
    """CLI entry logic — handles subcommands."""
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        interactive_add_event()
    else:
        main()
        show_today_events()

