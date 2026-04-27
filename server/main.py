from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException

from .config import ADMIN_API_KEY
from .models import (
    IssueLicenseRequest,
    ActivateLicenseRequest,
    ValidateLicenseRequest,
    RevokeLicenseRequest,
    ResetDevicesRequest,
)
from .security import generate_license_key, verify_license_key
from .db import (
    init_db,
    upsert_customer,
    create_or_update_license,
    ensure_license_from_payload,
    get_license,
    set_license_status,
    count_devices_for_license,
    get_device,
    upsert_device,
    add_activation,
    add_validation,
    reset_devices_for_license,
    list_licenses,
    list_devices_for_license,
    audit_log,
)

app = FastAPI(title="License Server V1", version="0.2.0")

@app.on_event("startup")
def startup_event():
    init_db()

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

def require_admin_key(admin_api_key: str):
    if admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

def verify_payload_for_request(payload: dict, email: str) -> dict:
    payload_email = str(payload.get("email", "")).strip().lower()
    request_email = str(email).strip().lower()

    if not payload_email:
        raise HTTPException(status_code=400, detail="License missing email")

    if payload_email != request_email:
        raise HTTPException(status_code=403, detail="License email does not match")

    expires_at_raw = str(payload.get("expires_at", "")).strip()
    expires_at_dt = parse_iso(expires_at_raw)

    if expires_at_dt < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="License expired")

    max_devices = int(payload.get("max_devices", 1))
    if max_devices < 1:
        raise HTTPException(status_code=400, detail="Invalid max_devices")

    return {
        "email": payload_email,
        "tier": str(payload.get("tier", "basic")).strip().lower() or "basic",
        "expires_at": expires_at_raw,
        "max_devices": max_devices,
        "issued_at": str(payload.get("issued_at", "")).strip(),
    }

def require_license_usable(license_record: dict):
    if not license_record:
        raise HTTPException(status_code=403, detail="License not found in database")

    status = str(license_record.get("status", "")).strip().lower()

    if status != "active":
        raise HTTPException(status_code=403, detail=f"License status is {status or 'missing'}")

    expires_at_raw = str(license_record.get("expires_at", "")).strip()
    expires_at_dt = parse_iso(expires_at_raw)

    if expires_at_dt < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="License expired")

def register_or_update_device(license_key: str, device_id: str, hostname: str, app_version: str, max_devices: int):
    existing_device = get_device(license_key, device_id)
    if not existing_device:
        current_count = count_devices_for_license(license_key)
        if current_count >= int(max_devices):
            raise HTTPException(status_code=403, detail="Device limit reached for this license")

    upsert_device(
        license_key=license_key,
        device_id=device_id,
        hostname=hostname,
        app_version=app_version,
    )

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/issue-license")
def issue_license(req: IssueLicenseRequest):
    require_admin_key(req.admin_api_key)

    issued_at_dt = datetime.now(timezone.utc)
    expires_at_dt = issued_at_dt + timedelta(days=int(getattr(req, "days_valid", None) or getattr(req, "days", 30)))

    payload = {
        "email": req.email.lower(),
        "issued_at": issued_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "max_devices": int(req.max_devices),
        "status": "active",
        "tier": req.tier.lower(),
    }

    license_key = generate_license_key(payload)

    upsert_customer(req.email.lower(), req.full_name)

    create_or_update_license(
        {
            "customer_email": req.email.lower(),
            "license_key": license_key,
            "tier": payload["tier"],
            "status": payload["status"],
            "max_devices": payload["max_devices"],
            "issued_at": payload["issued_at"],
            "expires_at": payload["expires_at"],
            "terms_version": req.terms_version,
        }
    )

    audit_log("issue_license", license_key, req.email.lower(), f"tier={payload['tier']} max_devices={payload['max_devices']}")

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

    license_record = ensure_license_from_payload(
        req.license_key,
        payload,
        req.accepted_terms_version,
    )
    require_license_usable(license_record)

    max_devices = int(license_record.get("max_devices", info["max_devices"]))

    register_or_update_device(
        license_key=req.license_key,
        device_id=device_id,
        hostname=req.hostname,
        app_version=req.app_version,
        max_devices=max_devices,
    )

    add_activation(
        license_key=req.license_key,
        customer_email=info["email"],
        device_id=device_id,
        hostname=req.hostname,
        accepted_terms_version=req.accepted_terms_version,
        app_version=req.app_version,
    )

    audit_log("activate_license", req.license_key, info["email"], f"device_id={device_id}")

    return {
        "ok": True,
        "valid": True,
        "email": info["email"],
        "status": "active",
        "tier": license_record.get("tier", info["tier"]),
        "expires_at": license_record.get("expires_at", info["expires_at"]),
        "max_devices": max_devices,
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

    license_record = ensure_license_from_payload(
        req.license_key,
        payload,
        "",
    )
    require_license_usable(license_record)

    max_devices = int(license_record.get("max_devices", info["max_devices"]))

    register_or_update_device(
        license_key=req.license_key,
        device_id=device_id,
        hostname=req.hostname,
        app_version=req.app_version,
        max_devices=max_devices,
    )

    add_validation(
        license_key=req.license_key,
        customer_email=info["email"],
        device_id=device_id,
        hostname=req.hostname,
        app_version=req.app_version,
    )

    return {
        "ok": True,
        "valid": True,
        "email": info["email"],
        "status": "active",
        "tier": license_record.get("tier", info["tier"]),
        "expires_at": license_record.get("expires_at", info["expires_at"]),
        "max_devices": max_devices,
        "device_id": device_id,
    }

@app.post("/revoke-license")
def revoke_license(req: RevokeLicenseRequest):
    require_admin_key(req.admin_api_key)

    allowed = {"active", "revoked", "suspended", "expired", "trial", "canceled"}
    new_status = req.new_status.strip().lower()

    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {', '.join(sorted(allowed))}")

    existing = get_license(req.license_key)
    if not existing:
        raise HTTPException(status_code=404, detail="License not found")

    changed = set_license_status(req.license_key, new_status)
    audit_log("set_license_status", req.license_key, existing.get("customer_email", ""), f"new_status={new_status}")

    return {
        "ok": True,
        "license_key": req.license_key,
        "new_status": new_status,
        "changed_rows": changed,
    }

@app.post("/reset-devices")
def reset_devices(req: ResetDevicesRequest):
    require_admin_key(req.admin_api_key)

    existing = get_license(req.license_key)
    if not existing:
        raise HTTPException(status_code=404, detail="License not found")

    deleted = reset_devices_for_license(req.license_key)
    audit_log("reset_devices", req.license_key, existing.get("customer_email", ""), f"deleted_devices={deleted}")

    return {
        "ok": True,
        "license_key": req.license_key,
        "deleted_devices": deleted,
    }

@app.get("/admin/licenses")
def admin_licenses(admin_api_key: str, limit: int = 200):
    require_admin_key(admin_api_key)

    rows = list_licenses(limit)
    return {
        "ok": True,
        "count": len(rows),
        "licenses": rows,
    }

@app.get("/admin/license")
def admin_license_detail(admin_api_key: str, license_key: str):
    require_admin_key(admin_api_key)

    license_record = get_license(license_key)
    if not license_record:
        raise HTTPException(status_code=404, detail="License not found")

    device_rows = list_devices_for_license(license_key)

    return {
        "ok": True,
        "license": license_record,
        "devices": device_rows,
    }
