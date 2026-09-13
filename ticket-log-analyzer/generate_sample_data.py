"""
Generates a realistic fake ticket export CSV for testing the ticket analyzer.
Not part of the actual analysis tool - this just creates sample data to
develop and demo against, standing in for a real ITSM export.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible output

CATEGORIES = ["Hardware Fault", "Account/Access", "Application Support",
              "Network Connectivity", "Printer/Device"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
TECHNICIANS = ["W. Thurkle", "J. Smith", "A. Patel", "M. Chen"]

# Roughly matches real-world weighting: account/access and hardware faults
# are the most common, critical/hardware issues take longer to resolve.
CATEGORY_WEIGHTS = [0.30, 0.28, 0.22, 0.12, 0.08]
PRIORITY_WEIGHTS = [0.40, 0.35, 0.20, 0.05]

RESOLUTION_HOURS_BY_PRIORITY = {
    "Low": (2, 24),
    "Medium": (1, 12),
    "High": (0.5, 6),
    "Critical": (0.25, 3),
}

def generate_tickets(num_tickets=900, days_back=30):
    start_date = datetime.now() - timedelta(days=days_back)
    tickets = []

    for i in range(1, num_tickets + 1):
        created = start_date + timedelta(
            days=random.uniform(0, days_back),
            hours=random.uniform(8, 18)  # business hours skew
        )
        category = random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0]
        priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
        low, high = RESOLUTION_HOURS_BY_PRIORITY[priority]
        resolution_hours = random.uniform(low, high)
        resolved = created + timedelta(hours=resolution_hours)

        tickets.append({
            "TicketID": f"TICK-{1000 + i}",
            "CreatedDate": created.strftime("%Y-%m-%d %H:%M"),
            "ResolvedDate": resolved.strftime("%Y-%m-%d %H:%M"),
            "Category": category,
            "Priority": priority,
            "AssignedTo": random.choice(TECHNICIANS),
            "Status": "Resolved",
        })

    return tickets

if __name__ == "__main__":
    tickets = generate_tickets()
    with open("sample_tickets.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
        writer.writeheader()
        writer.writerows(tickets)

    print(f"Generated {len(tickets)} sample tickets -> sample_tickets.csv")
