import os
import sys

# Remove the local 'supabase/' folder from the path so the installed package is found
sys.path = [p for p in sys.path if not p == os.path.dirname(os.path.abspath(__file__))]

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

try:
    import requests

    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }

    # The REST root returns the OpenAPI spec listing all exposed tables
    response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers, timeout=10)
    response.raise_for_status()

    spec = response.json()
    tables = list(spec.get("definitions", {}).keys())

    print("✅ Supabase connected")
    if tables:
        print(f"   Tables found: {', '.join(sorted(tables))}")
    else:
        print("   No tables yet (schema not created)")

except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
