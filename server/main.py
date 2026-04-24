from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from .config import ADMIN_API_KEY
from .db import get_conn, init_db
from .models import IssueLicenseRequest, ActivateLicenseRequest, ValidateLicenseRequest, RevokeLicenseRequest
from .security import generate_license_key, verify_license_key, now_iso

app = FastAPI(title="License Server V1")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/issue-license")
def issue_license(req: IssueLicenseRequest):
    if req.admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    issued_at = now_iso()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=req.days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    payload = {
        "email": req.email.lower(),
        "tier": req.tier.lower(),
        "status": "active",
        "max_devices": int(req.max_devices),
        "issued_at": issued_at,
        "expires_at": expires_at
    }

    license_key = generate_license_key(payload)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT OR IGNORE INTO customers (email, full_name, created_at) VALUES (?, ?, ?)", (
        req.email.lower(), req.full_name.strip(), issued_at
    ))

    cur.execute("INSERT INTO licenses (customer_email, license_key, tier, status, max_devices, issued_at, expires_at, terms_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
        req.email.lower(), license_key, req.tier.lower(), "active", int(req.max_devices), issued_at, expires_at, req.terms_version
    ))

    conn.commit()
    conn.close()

    return {
        "ok": True,
        "license_key": license_key,
        "issued_at": issued_at,
        "expires_at": expires_at
    }

@app.post("/activate-license")
def activate_license(req: ActivateLicenseRequest):
    try:
        payload = verify_license_key(req.license_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    license_email = str(payload.get("email", "")).strip().lower()
    if req.email.lower() != license_email:
        raise HTTPException(status_code=400, detail="License email does not match onboarding email")

    if str(payload.get("status", "")).lower() != "active":
        raise HTTPException(status_code=400, detail="License is not active")

    expires_at = str(payload.get("expires_at", "")).strip()
    if expires_at:
        exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if exp < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="License is expired")

    max_devices = int(payload.get("max_devices", 1) or 1)

    conn = get_conn()
    cur = conn.cursor()

    row = cur.execute("SELECT status, max_devices FROM licenses WHERE license_key = ?", (req.license_key,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="License not found on server")

    if row["status"] != "active":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Server license status is {row['status']}")

    devices = cur.execute("SELECT COUNT(*) AS c FROM devices WHERE license_key = ?", (req.license_key,)).fetchone()["c"]
    existing = cur.execute("SELECT id FROM devices WHERE license_key = ? AND device_id = ?", (req.license_key, req.device_id)).fetchone()

    if not existing and devices >= max_devices:
        conn.close()
        raise HTTPException(status_code=400, detail="Device limit reached")

    ts = now_iso()

    if not existing:
        cur.execute("INSERT INTO devices (license_key, device_id, hostname, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?)", (
            req.license_key, req.device_id, req.hostname.strip(), ts, ts
        ))
    else:
        cur.execute("UPDATE devices SET hostname = ?, last_seen_at = ? WHERE license_key = ? AND device_id = ?", (
            req.hostname.strip(), ts, req.license_key, req.device_id
        ))

    cur.execute("INSERT INTO activations (license_key, customer_email, device_id, hostname, activated_at, accepted_terms_version, app_version) VALUES (?, ?, ?, ?, ?, ?, ?)", (
        req.license_key, req.email.lower(), req.device_id, req.hostname.strip(), ts, req.accepted_terms_version, req.app_version.strip()
    ))

    conn.commit()
    conn.close()

    return {
        "ok": True,
        "status": "active",
        "tier": payload.get("tier"),
        "expires_at": payload.get("expires_at"),
        "max_devices": payload.get("max_devices")
    }

@app.post("/validate-license")
def validate_license(req: ValidateLicenseRequest):
    try:
        payload = verify_license_key(req.license_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    license_email = str(payload.get("email", "")).strip().lower()
    if req.email.lower() != license_email:
        raise HTTPException(status_code=400, detail="License email does not match onboarding email")

    conn = get_conn()
    cur = conn.cursor()

    row = cur.execute("SELECT status, expires_at, max_devices FROM licenses WHERE license_key = ?", (req.license_key,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="License not found on server")

    if row["status"] != "active":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Server license status is {row['status']}")

    existing = cur.execute("SELECT id FROM devices WHERE license_key = ? AND device_id = ?", (req.license_key, req.device_id)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=400, detail="This device is not activated for that license")

    conn.close()

    return {
        "ok": True,
        "status": row["status"],
        "expires_at": row["expires_at"],
        "max_devices": row["max_devices"]
    }

@app.post("/revoke-license")
def revoke_license(req: RevokeLicenseRequest):
    if req.admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    if req.new_status not in {"paused", "revoked", "active", "expired"}:
        raise HTTPException(status_code=400, detail="Invalid new status")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE licenses SET status = ? WHERE license_key = ?", (req.new_status, req.license_key))
    changed = cur.rowcount
    conn.commit()
    conn.close()

    if not changed:
        raise HTTPException(status_code=404, detail="License not found")

    return {"ok": True, "new_status": req.new_status}
