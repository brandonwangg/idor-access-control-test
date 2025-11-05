> **Portfolio Project — Preventive Security Engineering**  
> Demonstrates how to *detect, analyze, and prevent* authorization design flaws using the OWASP Juice Shop application as a controlled environment.  
> Focus: **Secure-by-default access control**, not just vulnerability discovery.

# IDOR Access Control Test

A simple, portable script to detect **Insecure Direct Object Reference (IDOR)** by probing authorization boundaries in an API. Designed for preventive security and secure-by-design engineering workflows.

> **Why this matters:**  
> Authentication proves *who* you are. Authorization proves *what* you’re allowed to access.  
> IDOR occurs when a system exposes another user's object just because the requester knows or guesses its ID.

---

## What this checks

- Attempts to access **object IDs owned by other users**
- Verifies expected **401 / 403** instead of **200**
- Produces **clear developer-facing output** suitable for CI pipelines

---

## Quick Start

### 🔍 Unauthenticated Access Probe (No Login Required)

Detect whether private API endpoints are exposed publicly.

```bash
python idor_noauth_probe.py
```

#### Example Output

```
--- Probing unauthenticated access to 3 IDs across 2 endpoints ---

[✅  Not exposed] /api/Users/12345 → 401
[✅  Not exposed] /api/Users/12346 → 401
[✅  Not exposed] /api/Users/12347 → 401
```

If you ever see:
```
[⚠️  POSSIBLE EXPOSURE] /api/Orders/12345 → 200
```
→ **Private data is exposed without authentication.**

---

### 🔐 Authenticated IDOR Probe (Single User Account)

Use **one** normal user account to test whether foreign user objects are accessible.

```bash
python idor_check.py \
  --base https://juice-shop.herokuapp.com \
  --email <your-email> \
  --password <your-password> \
  --start 1 --end 20 --delay 0.4 --out idor_report.json
```

This checks whether the system enforces **object ownership** for authenticated requests.

---

## 🛡️ Why This Matters (Secure-by-Design Perspective)

This project demonstrates an *authenticated* IDOR — the most common real-world variant.

### Key Insight
**IDOR is not a “bug” — it’s an access control design flaw.**

The underlying issue:  
The system trusts user-supplied object IDs **without verifying ownership**.

### Real-World Impact

- Identity & profile data leakage  
- Unauthorized account access  
- Privilege escalation  
- **GDPR / PDPA reportable incidents**

---

### Preventive Security Principles Demonstrated

| Security Principle | What Secure Systems Do | What Vulnerable Systems Do |
|---|---|---|
| **Least Privilege** | Users access *only their own* data | Any user can read any user’s data |
| **Server-Side Authorization** | Check ownership in business logic | Trusts client-provided object IDs |
| **Deny by Default** | Block unless explicitly allowed | Allows unless explicitly blocked |

---

## ✅ Developer-Focused Remediation Guidance

> Fix the **design**, not just the endpoint.

1. **Verify Ownership, Not Just Authentication**
   ```python
   if request.user.id != resource.owner_id:
       return 403
   ```

2. **Enforce Access Control in Business Logic Layer**
   Not only in controllers / routes.

3. **Use Object-Scoped Access Helpers**
   e.g., `can_view(user, resource)` abstraction.

4. **Add Negative Access Tests**
   Include “cross-user access must fail” in CI.

---

## Output Artifacts

| File | Purpose |
|---|---|
| `idor_noauth_probe.py` | Detects **public exposure** (missing authN) |
| `idor_check.py` | Detects **cross-user access** (missing authZ) |
| `idor_report.json` | Stores reproducible evidence for triage & remediation |

---
