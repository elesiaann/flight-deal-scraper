"""
SQLite-backed store for sent alerts.
Prevents duplicate emails for the same deal.
"""
import sqlite3
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
DB_PATH = "flights.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def bootstrap_schema():
    """Create the sent_alerts table if it does not exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_alerts (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                origin         TEXT    NOT NULL,
                destination    TEXT    NOT NULL,
                out_date       TEXT    NOT NULL,
                price_found    REAL    NOT NULL,
                currency       TEXT    NOT NULL,
                alerted_at     TEXT    NOT NULL,
                UNIQUE(origin, destination, out_date, price_found)
            )
        """)
        conn.commit()
    logger.debug("Database schema ready at %s", DB_PATH)


def has_alert_been_sent(origin: str, destination: str, out_date: str, price: float) -> bool:
    """Return True if this exact deal has already triggered an alert."""
    with _connect() as conn:
        row = conn.execute(
            """SELECT 1 FROM sent_alerts
               WHERE origin=? AND destination=? AND out_date=? AND price_found=?""",
            (origin, destination, out_date, price),
        ).fetchone()
    return row is not None


def record_alert(origin: str, destination: str, out_date: str, price: float, currency: str):
    """Persist a deal so it is not alerted again."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO sent_alerts
               (origin, destination, out_date, price_found, currency, alerted_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (origin, destination, out_date, price, currency, now),
        )
        conn.commit()
    logger.debug("Recorded alert: %s→%s %s%.2f on %s", origin, destination, currency, price, out_date)
