import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Iterable, Dict, Any, List, Iterator, Sequence

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "store.sqlite"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _execute(conn: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> None:
    conn.execute(sql, params)


def _fetchall(conn: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> List[sqlite3.Row]:
    cur = conn.execute(sql, params)
    return cur.fetchall()


def init_db() -> None:
    with db() as conn:
        conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            ip_address TEXT,
            latitude REAL,
            longitude REAL,
            location TEXT,
            user_agent TEXT,
            device_id TEXT,
            resource TEXT NOT NULL,
            action TEXT NOT NULL,
            success INTEGER NOT NULL,
            mfa_used INTEGER,
            failure_reason TEXT,
            privilege_level TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_events_user_time ON events(user_id, timestamp);

        CREATE TABLE IF NOT EXISTS features (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            hour INTEGER,
            day_of_week INTEGER,
            geo_distance_km REAL,
            geo_velocity_kmh REAL,
            failure_burst REAL,
            resource_rarity REAL,
            new_device INTEGER,
            off_hours INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_features_user_time ON features(user_id, timestamp);

        CREATE TABLE IF NOT EXISTS anomalies (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            score REAL NOT NULL,
            risk REAL NOT NULL,
            reasons TEXT NOT NULL,
            contributions TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_anomalies_user_time ON anomalies(user_id, timestamp);

        CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            risk REAL NOT NULL,
            created_at TEXT NOT NULL,
            channel TEXT NOT NULL,
            payload TEXT NOT NULL
        );
        """
    )


def insert_events(rows: Iterable[Dict[str, Any]]) -> List[str]:
    sql = """
        INSERT OR REPLACE INTO events(
            event_id, user_id, timestamp, ip_address, latitude, longitude, location,
            user_agent, device_id, resource, action, success, mfa_used,
            failure_reason, privilege_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = []
    ids = []
    for r in rows:
        ids.append(r["event_id"])
        params.append(
            (
                r["event_id"],
                r["user_id"],
                r["timestamp"],
                r.get("ip_address"),
                r.get("latitude"),
                r.get("longitude"),
                r.get("location"),
                r.get("user_agent"),
                r.get("device_id"),
                r["resource"],
                r["action"],
                int(r["success"]),
                (None if r.get("mfa_used") is None else int(r["mfa_used"])),
                r.get("failure_reason"),
                r.get("privilege_level"),
            )
        )
    with db() as conn:
        conn.executemany(sql, params)
    return ids


def insert_features(rows: Iterable[Dict[str, Any]]) -> None:
    sql = """
        INSERT OR REPLACE INTO features(
            event_id, user_id, timestamp, hour, day_of_week, geo_distance_km,
            geo_velocity_kmh, failure_burst, resource_rarity, new_device, off_hours
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = [
        (
            r["event_id"],
            r["user_id"],
            r["timestamp"],
            r.get("hour"),
            r.get("day_of_week"),
            r.get("geo_distance_km"),
            r.get("geo_velocity_kmh"),
            r.get("failure_burst"),
            r.get("resource_rarity"),
            int(r.get("new_device") or 0),
            int(r.get("off_hours") or 0),
        )
        for r in rows
    ]
    with db() as conn:
        conn.executemany(sql, params)


def insert_anomaly(event_id: str, user_id: str, timestamp: str, score: float, risk: float, reasons: str, contributions: str) -> None:
    with db() as conn:
        _execute(
            conn,
        """
        INSERT OR REPLACE INTO anomalies(event_id, user_id, timestamp, score, risk, reasons, contributions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (event_id, user_id, timestamp, score, risk, reasons, contributions),
    )


def insert_alert(alert_id: str, event_id: str, user_id: str, risk: float, created_at: str, channel: str, payload: str) -> None:
    with db() as conn:
        _execute(
            conn,
        """
        INSERT OR REPLACE INTO alerts(alert_id, event_id, user_id, risk, created_at, channel, payload)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (alert_id, event_id, user_id, risk, created_at, channel, payload),
    )


def fetch_recent_events(limit: int = 100) -> List[sqlite3.Row]:
    with db() as conn:
        return _fetchall(conn, "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))


def fetch_anomalies(limit: int = 100) -> List[sqlite3.Row]:
    with db() as conn:
        return _fetchall(conn, "SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT ?", (limit,))


def fetch_user_events(user_id: str, limit: int = 1000) -> List[sqlite3.Row]:
    with db() as conn:
        return _fetchall(
            conn,
            "SELECT * FROM events WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit),
        )


def fetch_users(limit: int = 1000) -> List[sqlite3.Row]:
    with db() as conn:
        return _fetchall(
            conn,
            "SELECT user_id, COUNT(*) as c FROM events GROUP BY user_id ORDER BY c DESC LIMIT ?",
            (limit,),
        )
