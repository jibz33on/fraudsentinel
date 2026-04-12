"""
scripts/seed_data.py
Populates realistic transaction history for all 6 users.

What it does:
  - Inserts 20-25 transactions per user directly into transactions table
  - Matches each user's normal behavior (location, amount, merchants, hours)
  - Spreads transactions over last 90 days
  - No pipeline, no agents, no LLM — just raw history data

Why:
  - INVESTIGATOR needs behavioral baseline to detect deviations
  - Without this, known_countries/merchants/hours are all empty

Run:
    conda activate fraudsentinel
    python scripts/seed_data.py
"""

import sys
import os
import random
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import supabase
from dotenv import load_dotenv

load_dotenv()


# ── User profiles — matches users table exactly ───────────────────────────────

USERS = [
    {
        "id":       "55472a7d-8980-4777-b98d-e8b65e65d33c",
        "name":     "Jimmy K",
        "location": "Kochi, India",
        "merchants":["Swiggy", "Amazon", "Flipkart", "BigBasket", "Zomato"],
        "amount":   (50, 150),      # normal spend range
        "hours":    (8, 20),        # active hours
        "currency": "INR",
    },
    {
        "id":       "67f045c9-658d-4e62-8300-877be9a006d1",
        "name":     "Mark T",
        "location": "Kochi, India",
        "merchants":["Swiggy", "Amazon", "Flipkart", "Zomato", "BookMyShow"],
        "amount":   (20, 100),
        "hours":    (9, 21),
        "currency": "INR",
    },
    {
        "id":       "720b0db6-e4b4-4ca1-9989-5693728d871a",
        "name":     "Sarah M",
        "location": "London, UK",
        "merchants":["Amazon UK", "Tesco", "ASOS", "Deliveroo", "Uber"],
        "amount":   (100, 400),
        "hours":    (8, 22),
        "currency": "GBP",
    },
    {
        "id":       "d5dbff76-59df-45d8-b92d-bfa4cd3a7748",
        "name":     "Priya S",
        "location": "Singapore",
        "merchants":["Lazada", "Grab", "Shopee", "FairPrice", "Netflix"],
        "amount":   (50, 350),
        "hours":    (7, 22),
        "currency": "SGD",
    },
    {
        "id":       "dce92994-825b-4264-8ece-67b4ca440cbe",
        "name":     "Alex R",
        "location": "Mumbai, India",
        "merchants":["Flipkart", "Swiggy", "Amazon", "Zomato", "MakeMyTrip"],
        "amount":   (80, 250),
        "hours":    (9, 23),
        "currency": "INR",
    },
    {
        "id":       "5f3bfd92-46d1-46b5-b82d-4bacbc42928d",
        "name":     "TechCorp Ltd",
        "location": "Dubai, UAE",
        "merchants":["AWS", "Google Cloud", "Microsoft Azure", "Salesforce", "Zoom"],
        "amount":   (5000, 15000),
        "hours":    (8, 18),        # business hours only
        "currency": "USD",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def random_date_in_last_90_days() -> str:
    """Returns a random datetime string within the last 90 days."""
    days_ago = random.randint(1, 90)
    dt = datetime.utcnow() - timedelta(days=days_ago)
    # randomise the time within the user's active hours (handled per user)
    return dt


def build_transaction(user: dict, created_at: datetime) -> dict:
    """Build one realistic transaction row for a user."""
    amount_min, amount_max = user["amount"]
    hour_min, hour_max     = user["hours"]

    # Set the hour to match user's normal active hours
    created_at = created_at.replace(
        hour=random.randint(hour_min, hour_max),
        minute=random.randint(0, 59),
        second=0,
    )

    return {
        "id":         f"seed-{uuid.uuid4().hex[:8]}",
        "user_id":    user["id"],
        "amount":     round(random.uniform(amount_min, amount_max), 2),
        "currency":   user["currency"],
        "merchant":   random.choice(user["merchants"]),
        "location":   user["location"],
        "ip_address": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
        "device":     random.choice(["iPhone", "Android", "MacBook", "Windows PC"]),
        "status":     "complete",
        "created_at": created_at.isoformat(),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def seed():
    print("FraudSentinel — Seed Data\n")

    total_inserted = 0

    for user in USERS:
        count = random.randint(20, 25)
        print(f"Seeding {count} transactions for {user['name']}...")

        rows = []
        for _ in range(count):
            base_date = random_date_in_last_90_days()
            row = build_transaction(user, base_date)
            rows.append(row)

        # Batch insert
        result = supabase.table("transactions").insert(rows).execute()

        inserted = len(result.data) if result.data else 0
        total_inserted += inserted
        print(f"  ✅ {inserted} rows inserted\n")

    print(f"Done. Total inserted: {total_inserted} transactions")


if __name__ == "__main__":
    seed()