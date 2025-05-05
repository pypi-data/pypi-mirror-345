"""Creates csv/(database in the future) and returns events for current day."""

import csv
import re

from datetime import date
from pathlib import Path

EVENTS_CSV = Path.home() / ".local/share/ppcalendar/db/events.csv"
EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
EVENTS_CSV.touch(exist_ok=True)


def get_today_events() -> list[tuple[str, str]]:
    """Return a sorted list of (time, description) tuples for today."""
    today = date.today()
    matches = []

    with EVENTS_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_date = row["date"]
            raw_time = row["time"]
            event = row["event"]

            if (
                raw_date == today.isoformat() or
                raw_date == f"--{today.month:02}-{today.day:02}" or
                raw_date == f"--XX-{today.day:02}"
            ):
                matches.append((raw_time, event))

    matches.sort(key=lambda x: (x[0] != "", x[0]))  # All day first, then time
    return matches


def interactive_add_event() -> None:
    """Prompt user for event details and append to CSV."""
    print("📝 Add new event:")
    event = input(" > Event description (Enter to end): ").strip()
    if not event:
        print("❌ Event description required.")
        return

    time_raw = input(" > Time (13:00 or 1300): ").strip()
    match time_raw:
        case "":
            time_fmt = ""
        case t if re.fullmatch(r"\d{2}:\d{2}", t):
            time_fmt = t
        case t if re.fullmatch(r"\d{4}", t):
            time_fmt = f"{t[:2]}:{t[2:]}"
        case _:
            print("❌ Invalid time format.")
            return

    date_raw = input(" > Date (YYYY-MM-DD / MM-DD / DD): ").strip()
    match date_raw:
        case "":
            date_fmt = date.today().isoformat()
        case d if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            date_fmt = d
        case d if re.fullmatch(r"\d{2}-\d{2}", d):
            date_fmt = f"--{d}"
        case d if re.fullmatch(r"\d{1,2}", d):
            day = d.zfill(2)
            date_fmt = f"--XX-{day}"
        case _:
            print("❌ Invalid date format.")
            return

    with EVENTS_CSV.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if EVENTS_CSV.stat().st_size == 0:
            writer.writerow(["date", "time", "event"])
        writer.writerow([date_fmt, time_fmt, event])
    print("✅ Event saved.")

