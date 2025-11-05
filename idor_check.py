import requests
import json

# === CONFIGURATION ===
# Replace these values with the API you want to test

BASE_URL = "https://api.example.com"   # The API base endpoint
TOKEN = "YOUR_TOKEN_HERE"              # Token for a normal user (not admin)

# The script will load a list of object IDs to test from fixtures.json
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def load_test_ids():
    """Load test object IDs from fixtures.json."""
    try:
        with open("fixtures.json", "r") as f:
            data = json.load(f)
            return data.get("foreign_ids", [])
    except FileNotFoundError:
        print("[!] fixtures.json not found.")
        return []


def test_idor(object_id):
    """Send a request for a specific object ID and return the status."""
    url = f"{BASE_URL}/v1/items/{object_id}"
    response = requests.get(url, headers=HEADERS, timeout=5)
    return response.status_code, response.text[:200]


def main():
    test_ids = load_test_ids()

    if not test_ids:
        print("[!] No test IDs provided in fixtures.json")
        return

    print(f"\n--- Testing {len(test_ids)} object IDs for IDOR ---\n")

    for oid in test_ids:
        status, preview = test_idor(oid)

        if status == 200:
            print(f"[⚠️  POSSIBLE IDOR] Access to {oid} succeeded (status {status})")
        elif status in (401, 403):
            print(f"[✅  Access correctly blocked] {oid} → {status}")
        else:
            print(f"[ℹ️  Unexpected response] {oid} → {status}")
            print(f"Response preview: {preview}\n")


if __name__ == "__main__":
    main()
