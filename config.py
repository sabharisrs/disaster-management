import os


class Config:
    """Base configuration for the Flask application.

    This prefers a `DATABASE_URL` (e.g. Render Postgres). If not set,
    it falls back to a local SQLite database for development.
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # SQLAlchemy expects the postgresql+psycopg2 scheme. Some providers
        # (including older Render URLs) return 'postgres://...' which is
        # accepted by most drivers but SQLAlchemy raises a warning - normalize it.
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
