import os
from datetime import timedelta


class Config:
    # Use environment variable for secret key in production
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Vercel serverless: /tmp is the only writable directory.
    # Locally falls back to static/uploads.
    _is_vercel = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    UPLOAD_FOLDER = "/tmp/uploads" if _is_vercel else os.environ.get("UPLOAD_FOLDER", "static/uploads")

    # 50 MB max upload size
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "json", "txt"}

    # Files live for 1 hour (relevant in local / persistent server mode)
    FILE_LIFETIME = timedelta(hours=1)

    # Cleaning defaults
    DEFAULT_MISSING_THRESHOLD = 0.5
    DEFAULT_DUPLICATE_ACTION = "drop"
    DEFAULT_DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]

    @staticmethod
    def init_app(app):
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)