"""
Ticket Log Analyzer

Reads a CSV export of support tickets and produces a summary report:
volume by category, breakdown by priority, average resolution time,
and daily ticket volume trend.

Usage:
    python3 analyze_tickets.py <path_to_csv>

Expected CSV columns (case-sensitive):
    TicketID, CreatedDate, ResolvedDate, Category, Priority, AssignedTo, Status
Dates should be in "YYYY-MM-DD HH:MM" format. If your real export uses
different column names or date formats, adjust the COLUMN_MAP and
DATE_FORMAT constants below to match.
"""

import sys
import csv
from datetime import datetime
from collections import Counter, defaultdict
import statistics

DATE_FORMAT = "%Y-%m-%d %H:%M"


def load_tickets(filepath):
    tickets = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets


def parse_date(value):
    try:
        return datetime.strptime(value.strip(), DATE_FORMAT)
    except (ValueError, AttributeError):
        return None


def analyze(tickets):
    total = len(tickets)
    by_category = Counter(t.get("Category", "Unknown") for t in tickets)
    by_priority = Counter(t.get("Priority", "Unknown") for t in tickets)
    by_technician = Counter(t.get("AssignedTo", "Unassigned") for t in tickets)

    resolution_hours = []
    daily_counts = defaultdict(int)

    for t in tickets:
        created = parse_date(t.get("CreatedDate", ""))
        resolved = parse_date(t.get("ResolvedDate", ""))

        if created:
            daily_counts[created.date()] += 1

        if created and resolved:
            hours = (resolved - created).total_seconds() / 3600
            if hours >= 0:
                resolution_hours.append(hours)

    avg_resolution = statistics.mean(resolution_hours) if resolution_hours else None
    median_resolution = statistics.median(resolution_hours) if resolution_hours else None

    busiest_days = sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total": total,
        "by_category": by_category,
        "by_priority": by_priority,
        "by_technician": by_technician,
        "avg_resolution_hours": avg_resolution,
        "median_resolution_hours": median_resolution,
        "busiest_days": busiest_days,
        "date_range": (min(daily_counts) if daily_counts else None,
                       max(daily_counts) if daily_counts else None),
    }


def print_report(stats):
    print("=" * 50)
    print("TICKET LOG ANALYSIS REPORT")
    print("=" * 50)

    start, end = stats["date_range"]
    if start and end:
        days = (end - start).days + 1
        print(f"\nPeriod: {start} to {end} ({days} days)")
        print(f"Total tickets: {stats['total']}")
        print(f"Average per day: {stats['total'] / days:.1f}")

    print("\n--- By Category ---")
    for category, count in stats["by_category"].most_common():
        pct = count / stats["total"] * 100
        print(f"  {category:<25} {count:>5}  ({pct:.1f}%)")

    print("\n--- By Priority ---")
    for priority, count in stats["by_priority"].most_common():
        pct = count / stats["total"] * 100
        print(f"  {priority:<25} {count:>5}  ({pct:.1f}%)")

    print("\n--- By Technician ---")
    for tech, count in stats["by_technician"].most_common():
        print(f"  {tech:<25} {count:>5}")

    print("\n--- Resolution Time ---")
    if stats["avg_resolution_hours"] is not None:
        print(f"  Average: {stats['avg_resolution_hours']:.1f} hours")
        print(f"  Median:  {stats['median_resolution_hours']:.1f} hours")
    else:
        print("  No resolution time data available.")

    print("\n--- Busiest Days ---")
    for day, count in stats["busiest_days"]:
        print(f"  {day}: {count} tickets")

    print("\n" + "=" * 50)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_tickets.py <path_to_csv>")
        sys.exit(1)

    filepath = sys.argv[1]
    tickets = load_tickets(filepath)

    if not tickets:
        print("No tickets found in the file.")
        sys.exit(1)

    stats = analyze(tickets)
    print_report(stats)


if __name__ == "__main__":
    main()
