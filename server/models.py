from pydantic import BaseModel, EmailStr

class IssueLicenseRequest(BaseModel):
    admin_api_key: str
    email: EmailStr
    full_name: str = ""
    tier: str
    days: int = 30
    days_valid: int | None = None
    max_devices: int = 1
    terms_version: str = "2026-04-21-v2"

class ActivateLicenseRequest(BaseModel):
    email: EmailStr
    license_key: str
    device_id: str
    hostname: str = ""
    accepted_terms_version: str
    app_version: str = ""

class ValidateLicenseRequest(BaseModel):
    email: EmailStr
    license_key: str
    device_id: str
    hostname: str = ""
    app_version: str = ""

class RevokeLicenseRequest(BaseModel):
    admin_api_key: str
    license_key: str
    new_status: str

class ResetDevicesRequest(BaseModel):
    admin_api_key: str
    license_key: str
