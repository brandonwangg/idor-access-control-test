# IDOR Access Control Test

A simple, portable script to detect **Insecure Direct Object Reference (IDOR)** by testing
authorization boundaries in an API. Designed for developers and security engineers to run
locally or in CI as a quick **preventive** check.

> **Why this matters:** Authentication proves *who* you are. Authorization proves *what*
> you’re allowed to access. IDOR happens when an API returns another user’s object just
> because the requester knows/guesses the ID.

---

## What this checks

- Attempts to access **object IDs owned by another user/tenant**
- Confirms the API returns **401/403** (blocked) instead of **200** (leak)
- Keeps results simple and actionable for engineers

---

## Quick start

### 1) Install dependency
```bash
pip install -r requirements.txt
