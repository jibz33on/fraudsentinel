#!/usr/bin/env python
"""
FraudSentinel Demo Setup Script
────────────────────────────────
Prepares a clean, compelling demo dataset for the FraudSentinel dashboard.

Usage:
    conda activate fraudsentinel
    python scripts/demo.py

What it does:
    1. Clears all existing transactions and decisions
    2. Seeds realistic historical baselines per user (7 days old, not shown in activity feed)
    3. Runs 4 handpicked demo transactions through the live pipeline
    4. Prints a summary and dashboard URL

Demo Story:
    Act 1 — Two normal transactions → APPROVE  (shows explainability)
    Act 2 — Clear fraud case        → REJECT   (shows multi-signal detection)
    Act 3 — Borderline case         → REVIEW   (shows human-in-the-loop)
"""

import sys
import os
import time
import uuid
import json
import urllib.request
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import supabase

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[2m"

def banner(text, color=CYAN):
    width = 60
    print(f"\n{color}{BOLD}{'─' * width}{RESET}")
    print(f"{color}{BOLD}  {text}{RESET}")
    print(f"{color}{BOLD}{'─' * width}{RESET}")

def ok(text):    print(f"  {GREEN}✓{RESET}  {text}")
def warn(text):  print(f"  {YELLOW}⚠{RESET}  {text}")
def err(text):   print(f"  {RED}✗{RESET}  {text}")
def info(text):  print(f"  {DIM}{text}{RESET}")

# ── User IDs ──────────────────────────────────────────────────────────────────
USERS = {
    "mark_t":   "67f045c9-658d-4e62-8300-877be9a006d1",  # avg $45, Kochi India
    "jimmy_k":  "55472a7d-8980-4777-b98d-e8b65e65d33c",  # avg $85, Kochi India
    "sarah_m":  "720b0db6-e4b4-4ca1-9989-5693728d871a",  # avg $200, London UK
    "alex_r":   "dce92994-825b-4264-8ece-67b4ca440cbe",  # avg $150, Mumbai India
    "techcorp": "5f3bfd92-46d1-46b5-b82d-4bacbc42928d",  # avg $9500, Dubai UAE
}

# ── Step 1: Clear all data ────────────────────────────────────────────────────
CHUNK = 100  # Supabase in_ limit per request

def _chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]

def _fetch_all_ids(table: str, id_col: str = "id") -> list[str]:
    """Paginate through all rows — PostgREST returns max 1000 per request."""
    all_ids = []
    offset  = 0
    while True:
        r = supabase.table(table).select(id_col).range(offset, offset + CHUNK - 1).execute()
        batch = [row[id_col] for row in r.data]
        all_ids.extend(batch)
        if len(batch) < CHUNK:
            break
        offset += CHUNK
    return all_ids


def clear_all_data():
    banner("STEP 1 — Clearing existing data", YELLOW)

    txn_ids = _fetch_all_ids("transactions")
    info(f"Found {len(txn_ids)} transactions to delete")

    if not txn_ids:
        ok("Nothing to clear")
        return

    # Delete ALL agent_decisions first (FK + vector memory), in chunks
    deleted_decisions = 0
    for batch in _chunk(txn_ids, CHUNK):
        r = supabase.table("agent_decisions").delete().in_("transaction_id", batch).execute()
        deleted_decisions += len(r.data)

    # Also catch any orphaned agent_decisions not linked to fetched txns
    orphan_ids = _fetch_all_ids("agent_decisions")
    if orphan_ids:
        for batch in _chunk(orphan_ids, CHUNK):
            supabase.table("agent_decisions").delete().in_("id", batch).execute()
        deleted_decisions += len(orphan_ids)

    ok(f"Cleared {deleted_decisions} agent decisions (vector memory wiped)")

    # Delete all transactions in chunks
    deleted_txns = 0
    for batch in _chunk(txn_ids, CHUNK):
        r = supabase.table("transactions").delete().in_("id", batch).execute()
        deleted_txns += len(r.data)
    ok(f"Cleared {deleted_txns} transactions")

# ── Step 2: Seed historical baselines ────────────────────────────────────────
# These are 7 days old — below the profiler's 30-txn window but not recent
# enough to show on the activity feed. They give the investigator a solid
# behaviour baseline for each user.

HISTORY = {
    "mark_t": [
        dict(merchant="Swiggy",   amount=42,  currency="INR", location="Kochi, India",  device="Chrome/Mac"),
        dict(merchant="Netflix",  amount=15,  currency="INR", location="Kochi, India",  device="Chrome/Mac"),
        dict(merchant="Flipkart", amount=38,  currency="INR", location="Kochi, India",  device="iPhone"),
        dict(merchant="Uber",     amount=12,  currency="INR", location="Kochi, India",  device="iPhone"),
        dict(merchant="Swiggy",   amount=55,  currency="INR", location="Kochi, India",  device="Chrome/Mac"),
        dict(merchant="Zomato",   amount=48,  currency="INR", location="Kochi, India",  device="Chrome/Mac"),
        dict(merchant="Amazon",   amount=89,  currency="INR", location="Kochi, India",  device="Chrome/Mac"),
        dict(merchant="Hotstar",  amount=10,  currency="INR", location="Kochi, India",  device="iPhone"),
    ],
    "jimmy_k": [
        dict(merchant="Amazon",      amount=75,  currency="INR", location="Kochi, India", device="Chrome/Mac"),
        dict(merchant="Flipkart",    amount=110, currency="INR", location="Kochi, India", device="Chrome/Mac"),
        dict(merchant="Netflix",     amount=15,  currency="INR", location="Kochi, India", device="Samsung TV"),
        dict(merchant="Zomato",      amount=65,  currency="INR", location="Kochi, India", device="iPhone"),
        dict(merchant="Google Play", amount=8,   currency="INR", location="Kochi, India", device="iPhone"),
        dict(merchant="Steam",       amount=60,  currency="INR", location="Kochi, India", device="Chrome/Mac"),
        dict(merchant="Amazon",      amount=95,  currency="INR", location="Kochi, India", device="Chrome/Mac"),
        dict(merchant="Airtel",      amount=20,  currency="INR", location="Kochi, India", device="iPhone"),
    ],
    "sarah_m": [
        dict(merchant="Tesco",           amount=180, currency="GBP", location="London, UK", device="Chrome/Mac"),
        dict(merchant="John Lewis",      amount=250, currency="GBP", location="London, UK", device="Chrome/Mac"),
        dict(merchant="Netflix",         amount=18,  currency="GBP", location="London, UK", device="Chrome/Mac"),
        dict(merchant="Amazon UK",       amount=145, currency="GBP", location="London, UK", device="Chrome/Mac"),
        dict(merchant="Uber",            amount=22,  currency="GBP", location="London, UK", device="iPhone"),
        dict(merchant="Marks & Spencer", amount=190, currency="GBP", location="London, UK", device="Chrome/Mac"),
        dict(merchant="Waitrose",        amount=165, currency="GBP", location="London, UK", device="Chrome/Mac"),
        dict(merchant="Costa Coffee",    amount=8,   currency="GBP", location="London, UK", device="iPhone"),
    ],
    "alex_r": [
        dict(merchant="Amazon",      amount=130, currency="INR", location="Mumbai, India", device="Chrome/Mac"),
        dict(merchant="Swiggy",      amount=55,  currency="INR", location="Mumbai, India", device="iPhone"),
        dict(merchant="BookMyShow",  amount=25,  currency="INR", location="Mumbai, India", device="iPhone"),
        dict(merchant="Flipkart",    amount=180, currency="INR", location="Mumbai, India", device="Chrome/Mac"),
        dict(merchant="Ola",         amount=18,  currency="INR", location="Mumbai, India", device="iPhone"),
        dict(merchant="Netflix",     amount=15,  currency="INR", location="Mumbai, India", device="Samsung TV"),
        dict(merchant="Amazon",      amount=160, currency="INR", location="Mumbai, India", device="Chrome/Mac"),
        dict(merchant="Hotstar",     amount=10,  currency="INR", location="Mumbai, India", device="iPhone"),
    ],
    "techcorp": [
        dict(merchant="Microsoft Azure", amount=9200,  currency="USD", location="Dubai, UAE", device="Chrome/Win"),
        dict(merchant="AWS",             amount=11500, currency="USD", location="Dubai, UAE", device="Chrome/Win"),
        dict(merchant="Google Cloud",    amount=8800,  currency="USD", location="Dubai, UAE", device="Chrome/Win"),
        dict(merchant="Salesforce",      amount=9600,  currency="USD", location="Dubai, UAE", device="Chrome/Win"),
        dict(merchant="Microsoft Azure", amount=10200, currency="USD", location="Dubai, UAE", device="Chrome/Win"),
        dict(merchant="AWS",             amount=8400,  currency="USD", location="Dubai, UAE", device="Chrome/Win"),
    ],
}

def seed_history():
    banner("STEP 2 — Seeding historical baselines", YELLOW)
    base_time = datetime.now(timezone.utc) - timedelta(days=7)
    total = 0

    for user_key, txns in HISTORY.items():
        user_id = USERS[user_key]
        for i, t in enumerate(txns):
            ts = (base_time + timedelta(hours=i * 6)).isoformat()
            supabase.table("transactions").insert({
                "id":         f"seed-{user_key}-{i + 1:02d}",
                "user_id":    user_id,
                "amount":     t["amount"],
                "currency":   t["currency"],
                "merchant":   t["merchant"],
                "location":   t["location"],
                "ip_address": "10.0.0.1",
                "device":     t["device"],
                "status":     "APPROVED",
                "created_at": ts,
            }).execute()
            total += 1

    ok(f"Seeded {total} historical transactions across {len(HISTORY)} users")

# ── Step 3: Demo transactions ─────────────────────────────────────────────────

DEMO_TRANSACTIONS = [
    # ── Act 1a: Normal domestic transaction ──────────────────────────────────
    {
        "act":      "ACT 1a — NORMAL TRANSACTION",
        "color":    GREEN,
        "label":    "Mark T  •  $42  •  Swiggy  •  Kochi, India",
        "talking_point": (
            "Regular $42 Swiggy order in Kochi — matches his baseline perfectly.\n"
            "  Notice the PATTERN / DEVIATION / RISK breakdown from the Investigator."
        ),
        "payload": {
            "user_id":    USERS["mark_t"],
            "amount":     42,
            "currency":   "INR",
            "merchant":   "Swiggy",
            "location":   "Kochi, India",
            "country":    "IN",
            "hour":       11,
            "method":     "card",
            "ip_address": "103.21.58.10",
            "ip_country": "IN",
            "device":     "Chrome/Mac",
        },
        "expected": "APPROVED",
    },

    # ── Act 1b: Normal international transaction ──────────────────────────────
    {
        "act":      "ACT 1b — NORMAL TRANSACTION",
        "color":    GREEN,
        "label":    "Sarah M  •  £185  •  Waitrose  •  London, UK",
        "talking_point": (
            "Routine grocery shop — well within her £200 average, known location.\n"
            "  Investigator confirms no deviations from baseline."
        ),
        "payload": {
            "user_id":    USERS["sarah_m"],
            "amount":     185,
            "currency":   "GBP",
            "merchant":   "Waitrose",
            "location":   "London, UK",
            "country":    "GB",
            "hour":       14,
            "method":     "card",
            "ip_address": "92.40.1.10",
            "ip_country": "GB",
            "device":     "Chrome/Mac",
        },
        "expected": "APPROVED",
    },

    # ── Act 2: Clear fraud ────────────────────────────────────────────────────
    {
        "act":      "ACT 2 — FRAUD DETECTED",
        "color":    RED,
        "label":    "Jimmy K  •  $3,500  •  Crypto Exchange XY  •  Lagos, Nigeria  •  3am",
        "talking_point": (
            "41× above average spend, crypto merchant, Nigeria, 3am — classic account takeover.\n"
            "  Walk through each agent: Detector fired 5 rules, Investigator shows exact deviation,\n"
            "  Decision explains which combination of signals drove the rejection."
        ),
        "payload": {
            "user_id":    USERS["jimmy_k"],
            "amount":     3500,
            "currency":   "USD",
            "merchant":   "Crypto Exchange XY",
            "location":   "Lagos, Nigeria",
            "country":    "NG",
            "hour":       3,
            "method":     "crypto",
            "ip_address": "41.203.64.10",
            "ip_country": "NG",
            "device":     "Unknown",
        },
        "expected": "REJECTED",
    },

    # ── Act 3: Borderline — analyst decides ───────────────────────────────────
    {
        "act":      "ACT 3 — ANALYST DECISION NEEDED",
        "color":    YELLOW,
        "label":    "Sarah M  •  $650  •  Apple Store  •  New York, US",
        "talking_point": (
            "3.25× above average, new country — but Apple Store is low-risk and hour is normal.\n"
            "  Could be legitimate travel. System flags it for review.\n"
            "  Click Approve or Reject — the human stays in the loop."
        ),
        "payload": {
            "user_id":    USERS["sarah_m"],
            "amount":     650,
            "currency":   "USD",
            "merchant":   "Apple Store",
            "location":   "New York, US",
            "country":    "US",
            "hour":       15,
            "method":     "card",
            "ip_address": "74.125.68.10",
            "ip_country": "US",
            "device":     "iPhone",
        },
        "expected": "REVIEW",
    },
]


def run_demo_transactions():
    banner("STEP 3 — Running demo transactions", CYAN)
    results = []

    for i, demo in enumerate(DEMO_TRANSACTIONS, 1):
        color = demo["color"]
        print(f"\n{color}{BOLD}── {demo['act']} ──{RESET}")
        print(f"  {BOLD}{demo['label']}{RESET}")
        for line in demo["talking_point"].split("\n"):
            info(line.lstrip())

        txn_id = f"demo-{i:02d}-{str(uuid.uuid4())[:6]}"
        payload = {**demo["payload"], "transaction_id": txn_id}

        try:
            req = urllib.request.Request(
                "http://localhost:8000/analyze",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                r = json.loads(resp.read())
                verdict    = r["verdict"]
                confidence = r["confidence"]
                v_color    = GREEN if verdict == "APPROVED" else (RED if verdict == "REJECTED" else YELLOW)
                match      = verdict == demo["expected"]
                icon       = f"{GREEN}✓{RESET}" if match else f"{YELLOW}⚠{RESET}"
                print(f"\n  {icon}  {v_color}{BOLD}{verdict}{RESET}  •  {confidence}% confidence")
                print(f"  {DIM}ID: {txn_id}{RESET}")
                results.append({"id": txn_id, "label": demo["label"], "verdict": verdict, "expected": demo["expected"]})

        except Exception as e:
            err(f"Pipeline error: {e}")
            results.append({"id": txn_id, "label": demo["label"], "verdict": "ERROR", "expected": demo["expected"]})

        if i < len(DEMO_TRANSACTIONS):
            time.sleep(2)

    return results


def print_summary(results):
    banner("DEMO READY", GREEN)
    all_ok = all(r["verdict"] == r["expected"] for r in results)

    for r in results:
        match  = r["verdict"] == r["expected"]
        icon   = f"{GREEN}✓{RESET}" if match else f"{YELLOW}⚠ (expected {r['expected']}){RESET}"
        v_color = GREEN if r["verdict"] == "APPROVED" else (RED if r["verdict"] == "REJECTED" else YELLOW)
        print(f"  {icon}  {v_color}{r['verdict']}{RESET}  —  {r['label']}")

    print()
    if all_ok:
        ok("All 4 transactions landed as expected")
    else:
        warn("Some verdicts differ from expected — check detector thresholds")

    print(f"\n  {CYAN}{BOLD}Open: http://localhost:3000{RESET}")
    print(f"  {DIM}4 demo transactions + historical baselines loaded{RESET}")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    banner("FraudSentinel  —  Demo Setup", CYAN)
    info("Preparing a clean, compelling dataset for your Stockholm demo...")

    clear_all_data()
    seed_history()

    print(f"\n  {DIM}Baselines seeded. Starting pipeline in 2s...{RESET}")
    time.sleep(2)

    results = run_demo_transactions()
    print_summary(results)
