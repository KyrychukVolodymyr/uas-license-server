from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException

from .config import ADMIN_API_KEY
from .models import IssueLicenseRequest, ActivateLicenseRequest, ValidateLicenseRequest, RevokeLicenseRequest
from .security import generate_license_key, verify_license_key, now_iso

app = FastAPI(title="License Server V1", version="0.1.1")


def parse_iso(value: str) -> datetime:
    if not value:
        raise HTTPException(status_code=400, detail="License missing expires_at")

    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid license expiration")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def verify_payload_for_request(payload: dict, email: str) -> dict:
    payload_email = str(payload.get("email", "")).strip().lower()
    request_email = str(email).strip().lower()

    if not payload_email:
        raise HTTPException(status_code=400, detail="License missing email")

    if payload_email != request_email:
        raise HTTPException(status_code=403, detail="License email does not match")

    status = str(payload.get("status", "")).strip().lower()
    if status != "active":
        raise HTTPException(status_code=403, detail=f"License status is {status or 'missing'}")

    expires_at_raw = str(payload.get("expires_at", "")).strip()
    expires_at_dt = parse_iso(expires_at_raw)

    if expires_at_dt < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="License expired")

    max_devices = int(payload.get("max_devices", 1))
    if max_devices < 1:
        raise HTTPException(status_code=400, detail="Invalid max_devices")

    return {
        "email": payload_email,
        "status": status,
        "tier": str(payload.get("tier", "basic")).strip().lower() or "basic",
        "expires_at": expires_at_raw,
        "max_devices": max_devices,
        "issued_at": str(payload.get("issued_at", "")).strip(),
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/issue-license")
def issue_license(req: IssueLicenseRequest):
    if req.admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    issued_at_dt = datetime.now(timezone.utc)
    expires_at_dt = issued_at_dt + timedelta(days=int(req.days_valid))

    payload = {
        "email": req.email.lower(),
        "issued_at": issued_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "max_devices": int(req.max_devices),
        "status": "active",
        "tier": req.tier.lower(),
    }

    license_key = generate_license_key(payload)

    return {
        "ok": True,
        "license_key": license_key,
        "issued_at": payload["issued_at"],
        "expires_at": payload["expires_at"],
        "email": payload["email"],
        "tier": payload["tier"],
        "status": payload["status"],
        "max_devices": payload["max_devices"],
    }


@app.post("/activate-license")
def activate_license(req: ActivateLicenseRequest):
    try:
        payload = verify_license_key(req.license_key)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid license key")

    info = verify_payload_for_request(payload, req.email)

    device_id = req.device_id.strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    if not req.accepted_terms_version.strip():
        raise HTTPException(status_code=400, detail="accepted_terms_version is required")

    return {
        "ok": True,
        "valid": True,
        "email": info["email"],
        "status": info["status"],
        "tier": info["tier"],
        "expires_at": info["expires_at"],
        "max_devices": info["max_devices"],
        "device_id": device_id,
    }


@app.post("/validate-license")
def validate_license(req: ValidateLicenseRequest):
    try:
        payload = verify_license_key(req.license_key)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid license key")

    info = verify_payload_for_request(payload, req.email)

    device_id = req.device_id.strip()
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    return {
        "ok": True,
        "valid": True,
        "email": info["email"],
        "status": info["status"],
        "tier": info["tier"],
        "expires_at": info["expires_at"],
        "max_devices": info["max_devices"],
        "device_id": device_id,
    }


@app.post("/revoke-license")
def revoke_license(req: RevokeLicenseRequest):
    if req.admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    return {
        "ok": True,
        "message": "MVP stateless license server: revocation requires persistent storage and will be added later.",
        "license_key": req.license_key,
        "new_status": req.new_status,
    }
