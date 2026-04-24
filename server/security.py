import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from .config import LICENSE_SIGNING_SECRET

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def b64d(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)

def dumps_payload(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sign_payload(payload: dict) -> str:
    sig = hmac.new(LICENSE_SIGNING_SECRET.encode("utf-8"), dumps_payload(payload), hashlib.sha256).digest()
    return b64e(sig)

def generate_license_key(payload: dict) -> str:
    return f"{b64e(dumps_payload(payload))}.{sign_payload(payload)}"

def verify_license_key(key: str) -> dict:
    if "." not in key:
        raise ValueError("Invalid key format")
    payload_b64, sig_b64 = key.split(".", 1)
    payload = json.loads(b64d(payload_b64).decode("utf-8"))
    expected = sign_payload(payload)
    if not hmac.compare_digest(sig_b64, expected):
        raise ValueError("Invalid key signature")
    return payload
