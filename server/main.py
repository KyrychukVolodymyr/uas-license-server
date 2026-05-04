from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import ADMIN_API_KEY, LICENSE_SIGNING_SECRET, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_BASIC_PRICE_ID, APP_SUCCESS_URL, APP_CANCEL_URL, RESEND_API_KEY, FROM_EMAIL, SUPPORT_EMAIL, PUBLIC_WEBSITE_URL, DOWNLOAD_MAC_PATH, DOWNLOAD_WINDOWS_PATH
from .models import (
    IssueLicenseRequest,
    ActivateLicenseRequest,
    ValidateLicenseRequest,
    RevokeLicenseRequest,
    ResetDevicesRequest,
)
from .security import generate_license_key, verify_license_key
from .admin_page import ADMIN_HTML
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
    list_audit_logs,
    list_activations_for_license,
    list_validations_for_license,
    dashboard_stats,
    get_latest_license_for_email,
)

app = FastAPI(title="License Server V1", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://uas-generator-website.onrender.com",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return ADMIN_HTML

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


@app.get("/admin/stats")
def admin_stats(admin_api_key: str):
    require_admin_key(admin_api_key)

    return {
        "ok": True,
        "stats": dashboard_stats(),
    }

@app.get("/admin/logs")
def admin_logs(admin_api_key: str, limit: int = 200):
    require_admin_key(admin_api_key)

    rows = list_audit_logs(limit)
    return {
        "ok": True,
        "count": len(rows),
        "logs": rows,
    }

@app.get("/admin/license-history")
def admin_license_history(admin_api_key: str, license_key: str, limit: int = 100):
    require_admin_key(admin_api_key)

    license_record = get_license(license_key)
    if not license_record:
        raise HTTPException(status_code=404, detail="License not found")

    activation_rows = list_activations_for_license(license_key, limit)
    validation_rows = list_validations_for_license(license_key, limit)

    return {
        "ok": True,
        "license": license_record,
        "activations": activation_rows,
        "validations": validation_rows,
    }


@app.post("/admin/renew-license")
def admin_renew_license(req: dict):
    require_admin_key(str(req.get("admin_api_key", "")))

    license_key = str(req.get("license_key", "")).strip()
    if not license_key:
        raise HTTPException(status_code=400, detail="license_key is required")

    try:
        days = int(req.get("days", 30))
    except Exception:
        raise HTTPException(status_code=400, detail="days must be a number")

    if days < 1:
        raise HTTPException(status_code=400, detail="days must be at least 1")

    existing = get_license(license_key)
    if not existing:
        raise HTTPException(status_code=404, detail="License not found")

    current_raw = str(existing.get("expires_at", "")).strip()
    now_dt = datetime.now(timezone.utc)

    try:
        current_dt = datetime.fromisoformat(current_raw.replace("Z", "+00:00")) if current_raw else now_dt
    except Exception:
        current_dt = now_dt

    if current_dt.tzinfo is None:
        current_dt = current_dt.replace(tzinfo=timezone.utc)

    base_dt = current_dt if current_dt > now_dt else now_dt
    new_expires = (base_dt + timedelta(days=days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    from .db import update_license_expiration_status

    changed = update_license_expiration_status(license_key, new_expires, "active")
    audit_log("renew_license", license_key, existing.get("customer_email", ""), f"days={days} new_expires={new_expires}")

    return {
        "ok": True,
        "license_key": license_key,
        "changed": changed,
        "expires_at": new_expires,
        "status": "active",
    }

@app.post("/admin/update-max-devices")
def admin_update_max_devices(req: dict):
    require_admin_key(str(req.get("admin_api_key", "")))

    license_key = str(req.get("license_key", "")).strip()
    if not license_key:
        raise HTTPException(status_code=400, detail="license_key is required")

    try:
        max_devices = int(req.get("max_devices", 1))
    except Exception:
        raise HTTPException(status_code=400, detail="max_devices must be a number")

    if max_devices < 1:
        raise HTTPException(status_code=400, detail="max_devices must be at least 1")

    existing = get_license(license_key)
    if not existing:
        raise HTTPException(status_code=404, detail="License not found")

    from .db import update_license_max_devices

    changed = update_license_max_devices(license_key, max_devices)
    audit_log("update_max_devices", license_key, existing.get("customer_email", ""), f"max_devices={max_devices}")

    return {
        "ok": True,
        "license_key": license_key,
        "changed": changed,
        "max_devices": max_devices,
    }


def b64_url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

def b64_url_decode(raw: str) -> bytes:
    pad = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + pad)

def make_download_token(email: str, platform: str, seconds_valid: int = 1800) -> str:
    payload = {
        "email": email.strip().lower(),
        "platform": platform,
        "exp": int(time.time()) + int(seconds_valid),
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig = hmac.new(LICENSE_SIGNING_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    return b64_url_encode(body) + "." + b64_url_encode(sig)

def verify_download_token(token: str) -> dict:
    if "." not in token:
        raise HTTPException(status_code=403, detail="Invalid download token")

    body_b64, sig_b64 = token.split(".", 1)
    body = b64_url_decode(body_b64)
    expected = hmac.new(LICENSE_SIGNING_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    received = b64_url_decode(sig_b64)

    if not hmac.compare_digest(expected, received):
        raise HTTPException(status_code=403, detail="Invalid download token")

    payload = json.loads(body.decode("utf-8"))

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=403, detail="Download link expired")

    return payload

def active_license_for_email(email: str):
    lic = get_latest_license_for_email(email)
    if not lic:
        return None

    if str(lic.get("status", "")).strip().lower() != "active":
        return None

    try:
        expires_at = parse_iso(str(lic.get("expires_at", "")))
    except Exception:
        return None

    if expires_at < datetime.now(timezone.utc):
        return None

    return lic

def create_paid_license_for_email(email: str, full_name: str = ""):
    email = email.strip().lower()
    existing = active_license_for_email(email)

    if existing:
        return existing

    issued_at_dt = datetime.now(timezone.utc)
    expires_at_dt = issued_at_dt + timedelta(days=32)

    payload = {
        "email": email,
        "issued_at": issued_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "max_devices": 1,
        "status": "active",
        "tier": "basic",
    }

    license_key = generate_license_key(payload)

    upsert_customer(email, full_name or "")

    create_or_update_license(
        {
            "customer_email": email,
            "license_key": license_key,
            "tier": "basic",
            "status": "active",
            "max_devices": 1,
            "issued_at": payload["issued_at"],
            "expires_at": payload["expires_at"],
            "terms_version": "2026-04-21-v2",
        }
    )

    audit_log("stripe_issue_license", license_key, email, "tier=basic max_devices=1")
    return get_license(license_key)

def send_resend_email(to_email: str, subject: str, html: str):
    if not RESEND_API_KEY:
        audit_log("email_not_sent", "", to_email, "RESEND_API_KEY missing")
        return {"ok": False, "reason": "RESEND_API_KEY missing"}

    payload = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html,
    }

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + RESEND_API_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            audit_log("email_sent", "", to_email, "resend ok")
            return {"ok": True, "body": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        audit_log("email_failed", "", to_email, body[:500])
        return {"ok": False, "reason": body}
    except Exception as e:
        audit_log("email_failed", "", to_email, str(e))
        return {"ok": False, "reason": str(e)}

def send_license_download_email(email: str, license_key: str):
    mac_token = make_download_token(email, "mac")
    windows_token = make_download_token(email, "windows")

    mac_link = PUBLIC_WEBSITE_URL.rstrip("/") + "/download-file?token=" + urllib.parse.quote(mac_token)
    windows_link = PUBLIC_WEBSITE_URL.rstrip("/") + "/download-file?token=" + urllib.parse.quote(windows_token)

    if "uas-license-server.onrender.com" not in PUBLIC_WEBSITE_URL:
        license_server_base = "https://uas-license-server.onrender.com"
        mac_link = license_server_base + "/download-file?token=" + urllib.parse.quote(mac_token)
        windows_link = license_server_base + "/download-file?token=" + urllib.parse.quote(windows_token)
    else:
        mac_link = PUBLIC_WEBSITE_URL.rstrip("/") + "/download-file?token=" + urllib.parse.quote(mac_token)
        windows_link = PUBLIC_WEBSITE_URL.rstrip("/") + "/download-file?token=" + urllib.parse.quote(windows_token)

    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #111827;">
      <h2>UAS Generator Access</h2>
      <p>Your UAS Generator license is ready.</p>

      <h3>License Key</h3>
      <div style="word-break: break-all; background: #f3f4f6; padding: 12px; border-radius: 8px; border: 1px solid #e5e7eb;">
        {license_key}
      </div>

      <h3>Download Links</h3>
      <p>These links are time-limited. If they expire, return to the download page and use “Already Paid?” to request new links.</p>

      <p>
        <a href="{mac_link}" style="display:inline-block;background:#2563eb;color:white;padding:12px 16px;border-radius:8px;text-decoration:none;font-weight:bold;">Download for Mac</a>
      </p>

      <p>
        <a href="{windows_link}" style="display:inline-block;background:#2563eb;color:white;padding:12px 16px;border-radius:8px;text-decoration:none;font-weight:bold;">Download for Windows</a>
      </p>

      <h3>Activation</h3>
      <ol>
        <li>Download the correct app for your device.</li>
        <li>Unzip the file first.</li>
        <li>Open the app.</li>
        <li>Enter your email and license key when prompted.</li>
        <li>Run System Check before generating documents.</li>
      </ol>

      <p style="color:#6b7280;font-size:13px;">Do not share your license key. One device is included with this subscription.</p>
    </div>
    """

    return send_resend_email(email, "Your UAS Generator license and download links", html)

def stripe_api_post(path: str, data: dict):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="STRIPE_SECRET_KEY is not configured")

    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        "https://api.stripe.com" + path,
        data=encoded,
        headers={
            "Authorization": "Bearer " + STRIPE_SECRET_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise HTTPException(status_code=500, detail="Stripe API error: " + body)

def stripe_api_get(path: str):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="STRIPE_SECRET_KEY is not configured")

    req = urllib.request.Request(
        "https://api.stripe.com" + path,
        headers={"Authorization": "Bearer " + STRIPE_SECRET_KEY},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}

def verify_stripe_signature(raw_body: bytes, signature_header: str):
    if not STRIPE_WEBHOOK_SECRET:
        return True

    parts = {}
    for item in signature_header.split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            parts.setdefault(k, []).append(v)

    timestamps = parts.get("t", [])
    signatures = parts.get("v1", [])

    if not timestamps or not signatures:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature header")

    signed_payload = timestamps[0].encode("utf-8") + b"." + raw_body
    expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

    if expected not in signatures:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    return True

def email_from_stripe_event_object(obj: dict) -> str:
    email = ""

    customer_details = obj.get("customer_details") or {}
    email = customer_details.get("email") or obj.get("customer_email") or obj.get("receipt_email") or ""

    if email:
        return str(email).strip().lower()

    customer_id = obj.get("customer") or ""
    if customer_id:
        customer = stripe_api_get("/v1/customers/" + urllib.parse.quote(str(customer_id)))
        email = customer.get("email") or ""

    return str(email).strip().lower()

@app.post("/stripe/create-checkout-session")
def create_checkout_session(req: dict):
    if not STRIPE_BASIC_PRICE_ID:
        raise HTTPException(status_code=500, detail="STRIPE_BASIC_PRICE_ID is not configured")

    data = {
        "mode": "subscription",
        "line_items[0][price]": STRIPE_BASIC_PRICE_ID,
        "line_items[0][quantity]": "1",
        "success_url": APP_SUCCESS_URL,
        "cancel_url": APP_CANCEL_URL,
        "metadata[plan]": "basic",
        "allow_promotion_codes": "false",
    }

    session = stripe_api_post("/v1/checkout/sessions", data)

    return {
        "ok": True,
        "url": session.get("url"),
        "id": session.get("id"),
    }

@app.post("/request-download-link")
def request_download_link(req: dict):
    email = str(req.get("email", "")).strip().lower()

    if not email or "@" not in email:
        return {"ok": True, "message": "If this email has an active subscription, instructions will be sent."}

    lic = active_license_for_email(email)

    if lic:
        send_license_download_email(email, lic.get("license_key", ""))
        audit_log("request_download_link", lic.get("license_key", ""), email, "active license found")
    else:
        audit_log("request_download_link_no_match", "", email, "no active license")

    return {"ok": True, "message": "If this email has an active subscription, instructions will be sent."}

@app.get("/download-file")
def download_file(token: str):
    payload = verify_download_token(token)
    platform = str(payload.get("platform", "")).lower()

    if platform == "mac":
        target = PUBLIC_WEBSITE_URL.rstrip("/") + DOWNLOAD_MAC_PATH
    elif platform == "windows":
        target = PUBLIC_WEBSITE_URL.rstrip("/") + DOWNLOAD_WINDOWS_PATH
    else:
        raise HTTPException(status_code=400, detail="Unknown download platform")

    return RedirectResponse(target, status_code=302)

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    raw = await request.body()
    signature = request.headers.get("stripe-signature", "")

    verify_stripe_signature(raw, signature)

    try:
        event = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook JSON")

    event_type = event.get("type", "")
    obj = (event.get("data") or {}).get("object") or {}

    if event_type in ("checkout.session.completed", "invoice.payment_succeeded"):
        email = email_from_stripe_event_object(obj)

        if email:
            lic = create_paid_license_for_email(email)
            send_license_download_email(email, lic.get("license_key", ""))
            audit_log("stripe_payment_success", lic.get("license_key", ""), email, event_type)
        else:
            audit_log("stripe_payment_success_no_email", "", "", event_type)

    elif event_type in ("invoice.payment_failed",):
        email = email_from_stripe_event_object(obj)
        if email:
            lic = active_license_for_email(email)
            if lic:
                set_license_status(lic.get("license_key", ""), "past_due")
                audit_log("stripe_payment_failed", lic.get("license_key", ""), email, event_type)

    elif event_type in ("customer.subscription.deleted",):
        email = email_from_stripe_event_object(obj)
        if email:
            lic = active_license_for_email(email)
            if lic:
                set_license_status(lic.get("license_key", ""), "canceled")
                audit_log("stripe_subscription_deleted", lic.get("license_key", ""), email, event_type)

    elif event_type in ("customer.subscription.updated",):
        audit_log("stripe_subscription_updated", "", "", event_type)

    return {"ok": True}

