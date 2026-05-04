import os

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev_key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./license_server.db")
LICENSE_SIGNING_SECRET = os.getenv("LICENSE_SIGNING_SECRET", "dev_signing_secret")

if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    DB_PATH = None

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_BASIC_PRICE_ID = os.getenv("STRIPE_BASIC_PRICE_ID", "")
APP_SUCCESS_URL = os.getenv("APP_SUCCESS_URL", "https://uas-generator-website.onrender.com/public/download.html?success=1")
APP_CANCEL_URL = os.getenv("APP_CANCEL_URL", "https://uas-generator-website.onrender.com/public/download.html?canceled=1")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "UAS Generator <onboarding@resend.dev>")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "")
PUBLIC_WEBSITE_URL = os.getenv("PUBLIC_WEBSITE_URL", "https://uas-generator-website.onrender.com")
DOWNLOAD_MAC_PATH = os.getenv("DOWNLOAD_MAC_PATH", "/public/UAS_Generator_Mac_v019.zip")
DOWNLOAD_WINDOWS_PATH = os.getenv("DOWNLOAD_WINDOWS_PATH", "/public/UAS_Generator_Windows_v7.zip")

