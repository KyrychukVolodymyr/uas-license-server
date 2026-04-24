import os
import sqlite3
from .config import DATABASE_URL

def get_conn():
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        raise RuntimeError("Postgres not yet configured")

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_email TEXT NOT NULL,
        license_key TEXT NOT NULL UNIQUE,
        tier TEXT NOT NULL,
        status TEXT NOT NULL,
        max_devices INTEGER NOT NULL,
        issued_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        terms_version TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT NOT NULL,
        device_id TEXT NOT NULL,
        hostname TEXT DEFAULT '',
        first_seen_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        UNIQUE(license_key, device_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS activations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        device_id TEXT NOT NULL,
        hostname TEXT DEFAULT '',
        activated_at TEXT NOT NULL,
        accepted_terms_version TEXT NOT NULL,
        app_version TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()
