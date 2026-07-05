import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "multiwire-secret-key")

    DRIVER = "ODBC Driver 18 for SQL Server"

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://@{os.getenv('DATABASE_SERVER')}/"
        f"{os.getenv('DATABASE_NAME')}"
        f"?driver={quote_plus(DRIVER)}"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False