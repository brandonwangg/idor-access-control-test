import requests
import json

BASE_URL = "https://juice-shop.herokuapp.com"  # hosted Juice Shop

# Endpoints that should NOT return other users' data to unauthenticated callers.
ENDPOINTS = [
    "/api/Users",           # user profiles
    "/api/BasketItems",     # cart items
]

def load_test_ids():
    """fixtures.json: { "foreign_ids": ["1","2","3","4","5"] }"""
    with open("fixtures.json", "r") as f:
        return json.load(f).get("foreign_ids", [])

def probe(path, obj_id):
    url = f"{BASE_URL}{path}/{obj_id}"
    r = requests.get(url, timeout=10)          # <-- NO Authorization header
    return r.status_code, r.text[:200]

def main():
    ids = load_test_ids()
    if not ids:
        print("[!] No IDs in fixtures.json")
        return

    had_exposure = False
    print(f"\n--- Probing unauthenticated access to {len(ids)} IDs across {len(ENDPOINTS)} endpoints ---\n")
    for ep in ENDPOINTS:
        for oid in ids:
            code, preview = probe(ep, oid)
            if code == 200:
                had_exposure = True
                print(f"[⚠️  POSSIBLE PUBLIC EXPOSURE] GET {ep}/{oid} → 200")
            elif code in (401, 403, 404, 405, 500):
                print(f"[✅  Not exposed] {ep}/{oid} → {code} (endpoint/id not valid on this instance)")
            else:
                print(f"[ℹ️  Check] {ep}/{oid} → {code} | {preview}")

    if had_exposure:
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
