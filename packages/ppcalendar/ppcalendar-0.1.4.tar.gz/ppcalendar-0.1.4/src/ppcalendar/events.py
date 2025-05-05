"""Creates csv/(database in the future) and returns events for current day."""

import csv
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".local" / "share" / "ppcalendar" / "db"
CSV_FILE = DB_PATH / "events.csv"

def ensure_csv_exists() -> None:
    """Ensure the database CSV file exists with headers."""
    if not DB_PATH.exists():
        DB_PATH.mkdir(parents=True)
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "time", "event"])

def parse_date_input(raw: str) -> str:
    """Parse various date formats into full YYYY-MM-DD."""
    now = datetime.now()
    match raw.strip().count("-"):
        case 0:  # monthly recurring like "05"
            month = int(raw)
            return f"*-{month:02d}-*"
        case 1:  # yearly recurring like "05-13"
            month, day = map(int, raw.split("-"))
            return f"*-{month:02d}-{day:02d}"
        case 2:  # full date
            return raw.strip()
        case _:  # empty input
            return now.strftime("%Y-%m-%d")

def parse_time_input(raw: str) -> str:
    """Parse time in HH:MM or HHMM or return current time."""
    raw = raw.strip()
    if not raw:
        return datetime.now().strftime("%H:%M")
    if ":" in raw:
        return raw
    if len(raw) == 4:
        return f"{raw[:2]}:{raw[2:]}"
    return raw  # fallback, assume already correct

def interactive_add_event() -> None:
    """Prompt user to add a new event interactively."""
    ensure_csv_exists()

    desc = input("📌 Event description (Enter to end): ").strip()
    if not desc:
        print("❗ No description. Cancelled.")
        return

    raw_time = input("⏰ Time (13:00 / 1300) [Enter = now]: ")
    time = parse_time_input(raw_time)

    raw_date = input("📅 Date (YYYY-MM-DD / MM-DD / DD) "
                     "[Enter = today]: ")
    date = parse_date_input(raw_date)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, time, desc])

    print(f"✅ Event added: {date} {time} - {desc}")

def get_today_events() -> list[tuple[str, str]]:
    """Return list of (time, event) tuples for today."""
    ensure_csv_exists()
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    month_day = now.strftime("-%m-%d")
    day_only = now.strftime("-%d")

    results = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = row["date"]
            if (
                row_date == today_str
                or row_date.endswith(month_day)
                or row_date.endswith(day_only)
            ):
                results.append((row["time"], row["event"]))

    # Sort: All-day (no time) first, then by time
    return sorted(results, key=lambda x: (x[0] != "", x[0]))

