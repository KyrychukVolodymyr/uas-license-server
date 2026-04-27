from datetime import datetime, timezone
from .config import DATABASE_URL

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    UniqueConstraint,
    select,
    insert,
    update,
    delete,
)

def clean_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url

ENGINE_URL = clean_database_url(DATABASE_URL)

connect_args = {}
if ENGINE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(ENGINE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("full_name", String, default=""),
    Column("created_at", String, nullable=False),
)

licenses = Table(
    "licenses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_email", String, nullable=False),
    Column("license_key", String, nullable=False, unique=True),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("max_devices", Integer, nullable=False),
    Column("issued_at", String, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("terms_version", String, nullable=False),
)

devices = Table(
    "devices",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("license_key", String, nullable=False),
    Column("device_id", String, nullable=False),
    Column("hostname", String, default=""),
    Column("app_version", String, default=""),
    Column("first_seen_at", String, nullable=False),
    Column("last_seen_at", String, nullable=False),
    UniqueConstraint("license_key", "device_id", name="uq_devices_license_device"),
)

activations = Table(
    "activations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("license_key", String, nullable=False),
    Column("customer_email", String, nullable=False),
    Column("device_id", String, nullable=False),
    Column("hostname", String, default=""),
    Column("activated_at", String, nullable=False),
    Column("accepted_terms_version", String, nullable=False),
    Column("app_version", String, default=""),
)

validations = Table(
    "validations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("license_key", String, nullable=False),
    Column("customer_email", String, nullable=False),
    Column("device_id", String, nullable=False),
    Column("hostname", String, default=""),
    Column("validated_at", String, nullable=False),
    Column("app_version", String, default=""),
)

admin_audit_logs = Table(
    "admin_audit_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("action", String, nullable=False),
    Column("license_key", String, default=""),
    Column("customer_email", String, default=""),
    Column("details", String, default=""),
    Column("created_at", String, nullable=False),
)

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def init_db():
    metadata.create_all(engine)

def row_to_dict(row):
    if row is None:
        return None
    return dict(row._mapping)

def upsert_customer(email: str, full_name: str = ""):
    email = email.strip().lower()
    created_at = now_iso()
    with engine.begin() as conn:
        existing = conn.execute(select(customers).where(customers.c.email == email)).first()
        if existing:
            conn.execute(
                update(customers)
                .where(customers.c.email == email)
                .values(full_name=full_name or existing._mapping.get("full_name", ""))
            )
        else:
            conn.execute(
                insert(customers).values(
                    email=email,
                    full_name=full_name or "",
                    created_at=created_at,
                )
            )

def create_or_update_license(record: dict):
    with engine.begin() as conn:
        existing = conn.execute(
            select(licenses).where(licenses.c.license_key == record["license_key"])
        ).first()

        if existing:
            conn.execute(
                update(licenses)
                .where(licenses.c.license_key == record["license_key"])
                .values(
                    customer_email=record["customer_email"],
                    tier=record["tier"],
                    status=record["status"],
                    max_devices=int(record["max_devices"]),
                    issued_at=record["issued_at"],
                    expires_at=record["expires_at"],
                    terms_version=record.get("terms_version", ""),
                )
            )
        else:
            conn.execute(insert(licenses).values(**record))

def get_license(license_key: str):
    with engine.begin() as conn:
        row = conn.execute(
            select(licenses).where(licenses.c.license_key == license_key)
        ).first()
        return row_to_dict(row)

def set_license_status(license_key: str, new_status: str):
    with engine.begin() as conn:
        result = conn.execute(
            update(licenses)
            .where(licenses.c.license_key == license_key)
            .values(status=new_status)
        )
        return result.rowcount

def ensure_license_from_payload(license_key: str, payload: dict, terms_version: str = ""):
    existing = get_license(license_key)
    if existing:
        return existing

    email = str(payload.get("email", "")).strip().lower()
    if not email:
        return None

    upsert_customer(email, "")
    record = {
        "customer_email": email,
        "license_key": license_key,
        "tier": str(payload.get("tier", "basic")).strip().lower() or "basic",
        "status": str(payload.get("status", "active")).strip().lower() or "active",
        "max_devices": int(payload.get("max_devices", 1)),
        "issued_at": str(payload.get("issued_at", "")).strip(),
        "expires_at": str(payload.get("expires_at", "")).strip(),
        "terms_version": terms_version or "",
    }
    create_or_update_license(record)
    return get_license(license_key)

def count_devices_for_license(license_key: str):
    with engine.begin() as conn:
        rows = conn.execute(
            select(devices.c.device_id).where(devices.c.license_key == license_key)
        ).fetchall()
        return len(rows)

def get_device(license_key: str, device_id: str):
    with engine.begin() as conn:
        row = conn.execute(
            select(devices).where(
                devices.c.license_key == license_key,
                devices.c.device_id == device_id,
            )
        ).first()
        return row_to_dict(row)

def upsert_device(license_key: str, device_id: str, hostname: str = "", app_version: str = ""):
    current_time = now_iso()
    with engine.begin() as conn:
        existing = conn.execute(
            select(devices).where(
                devices.c.license_key == license_key,
                devices.c.device_id == device_id,
            )
        ).first()

        if existing:
            conn.execute(
                update(devices)
                .where(
                    devices.c.license_key == license_key,
                    devices.c.device_id == device_id,
                )
                .values(
                    hostname=hostname or existing._mapping.get("hostname", ""),
                    app_version=app_version or existing._mapping.get("app_version", ""),
                    last_seen_at=current_time,
                )
            )
        else:
            conn.execute(
                insert(devices).values(
                    license_key=license_key,
                    device_id=device_id,
                    hostname=hostname or "",
                    app_version=app_version or "",
                    first_seen_at=current_time,
                    last_seen_at=current_time,
                )
            )

def add_activation(license_key: str, customer_email: str, device_id: str, hostname: str, accepted_terms_version: str, app_version: str):
    with engine.begin() as conn:
        conn.execute(
            insert(activations).values(
                license_key=license_key,
                customer_email=customer_email,
                device_id=device_id,
                hostname=hostname or "",
                activated_at=now_iso(),
                accepted_terms_version=accepted_terms_version or "",
                app_version=app_version or "",
            )
        )

def add_validation(license_key: str, customer_email: str, device_id: str, hostname: str, app_version: str):
    with engine.begin() as conn:
        conn.execute(
            insert(validations).values(
                license_key=license_key,
                customer_email=customer_email,
                device_id=device_id,
                hostname=hostname or "",
                validated_at=now_iso(),
                app_version=app_version or "",
            )
        )

def reset_devices_for_license(license_key: str):
    with engine.begin() as conn:
        result = conn.execute(delete(devices).where(devices.c.license_key == license_key))
        return result.rowcount

def list_licenses(limit: int = 200):
    with engine.begin() as conn:
        rows = conn.execute(
            select(licenses).order_by(licenses.c.id.desc()).limit(limit)
        ).fetchall()
        return [row_to_dict(row) for row in rows]

def list_devices_for_license(license_key: str):
    with engine.begin() as conn:
        rows = conn.execute(
            select(devices).where(devices.c.license_key == license_key).order_by(devices.c.id.desc())
        ).fetchall()
        return [row_to_dict(row) for row in rows]

def audit_log(action: str, license_key: str = "", customer_email: str = "", details: str = ""):
    with engine.begin() as conn:
        conn.execute(
            insert(admin_audit_logs).values(
                action=action,
                license_key=license_key or "",
                customer_email=customer_email or "",
                details=details or "",
                created_at=now_iso(),
            )
        )

def list_audit_logs(limit: int = 200):
    with engine.begin() as conn:
        rows = conn.execute(
            select(admin_audit_logs).order_by(admin_audit_logs.c.id.desc()).limit(limit)
        ).fetchall()
        return [row_to_dict(row) for row in rows]

def list_activations_for_license(license_key: str, limit: int = 100):
    with engine.begin() as conn:
        rows = conn.execute(
            select(activations)
            .where(activations.c.license_key == license_key)
            .order_by(activations.c.id.desc())
            .limit(limit)
        ).fetchall()
        return [row_to_dict(row) for row in rows]

def list_validations_for_license(license_key: str, limit: int = 100):
    with engine.begin() as conn:
        rows = conn.execute(
            select(validations)
            .where(validations.c.license_key == license_key)
            .order_by(validations.c.id.desc())
            .limit(limit)
        ).fetchall()
        return [row_to_dict(row) for row in rows]

def dashboard_stats():
    with engine.begin() as conn:
        license_rows = conn.execute(select(licenses)).fetchall()
        device_rows = conn.execute(select(devices)).fetchall()
        customer_rows = conn.execute(select(customers)).fetchall()

    license_list = [row_to_dict(row) for row in license_rows]
    device_list = [row_to_dict(row) for row in device_rows]
    customer_list = [row_to_dict(row) for row in customer_rows]

    by_status = {}
    by_tier = {}

    for lic in license_list:
        status = str(lic.get("status", "") or "unknown").lower()
        tier = str(lic.get("tier", "") or "unknown").lower()
        by_status[status] = by_status.get(status, 0) + 1
        by_tier[tier] = by_tier.get(tier, 0) + 1

    return {
        "total_customers": len(customer_list),
        "total_licenses": len(license_list),
        "total_devices": len(device_list),
        "by_status": by_status,
        "by_tier": by_tier,
    }
