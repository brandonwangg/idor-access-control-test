# IDOR Access Control Test

A simple, portable script to detect **Insecure Direct Object Reference (IDOR)** by probing authorization boundaries in an API. Designed for developers and security engineers to run locally or in CI as a quick **preventive** check.

> **Why this matters:**  
> Authentication proves *who* you are. Authorization proves *what* you’re allowed to access.  
> IDOR occurs when an API leaks another user's object simply because the requester *knows or guesses the ID*.

---

## What this checks

- Attempts to access **object IDs owned by another user/tenant**
- Verifies the API returns **401 / 403** (blocked) instead of **200** (leak)
- Keeps results clear, concise, and developer-friendly

---

## Quick Start

### 🔍 Unauthenticated Access Probe (No Login Required)

Use this mode to detect whether private API endpoints are accessible without authentication at all (a critical IDOR risk).

```bash
python idor_noauth_probe.py
```
