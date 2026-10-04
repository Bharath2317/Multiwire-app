import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


def _database_uri():
    """DATABASE_URL wins (any SQLAlchemy URL); otherwise build the SQL Server URL."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    driver = os.getenv("ODBC_DRIVER", "ODBC Driver 18 for SQL Server")
    user = os.getenv("DATABASE_USER")
    if user:
        auth = f"{quote_plus(user)}:{quote_plus(os.getenv('DATABASE_PASSWORD', ''))}@"
        trusted = ""
    else:
        auth = "@"
        trusted = "&trusted_connection=yes"

    return (
        f"mssql+pyodbc://{auth}{os.getenv('DATABASE_SERVER')}/"
        f"{os.getenv('DATABASE_NAME')}"
        f"?driver={quote_plus(driver)}{trusted}&TrustServerCertificate=yes"
    )


class Config:
    ENV = os.getenv("APP_ENV", "development")
    IS_PRODUCTION = ENV == "production"

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key")

    # Single shared login. Leave unset only for local development.
    APP_PASSWORD = os.getenv("APP_PASSWORD")

    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PRODUCTION and os.getenv("COOKIE_SECURE", "1") == "1"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
