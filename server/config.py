import os

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev_key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./license_server.db")

LICENSE_SIGNING_SECRET = os.getenv("LICENSE_SIGNING_SECRET", "dev_signing_secret")

if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    DB_PATH = None
