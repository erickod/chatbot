from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current UTC time as timezone-naive datetime for PostgreSQL storage.

    PostgreSQL TIMESTAMP columns don't store timezone info — using naive UTC avoids
    SQLAlchemy warnings and maintains consistent storage behavior.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
