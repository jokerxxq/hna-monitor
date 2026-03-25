import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from app.config import settings


def _db_path_from_url(database_url: str) -> str:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this project.")
    path = database_url.replace("sqlite:///", "", 1)
    return os.path.abspath(path)


def ensure_db_dir() -> str:
    db_path = _db_path_from_url(settings.database_url)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path


@contextmanager
def get_conn():
    db_path = ensure_db_dir()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                travel_date TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                target_price REAL NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                last_price REAL,
                last_notified_price REAL,
                last_checked_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_task(travel_date: str, origin: str, destination: str, target_price: float) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO tasks (travel_date, origin, destination, target_price, enabled, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (travel_date, origin.strip().upper(), destination.strip().upper(), target_price, now_str()),
        )


def list_tasks(limit: int = 10) -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()


def delete_task(task_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def toggle_task(task_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET enabled = CASE WHEN enabled = 1 THEN 0 ELSE 1 END
            WHERE id = ?
            """,
            (task_id,),
        )


def get_enabled_tasks() -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM tasks WHERE enabled = 1 ORDER BY id DESC")
        return cur.fetchall()


def update_task_check_result(task_id: int, price: float) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET last_price = ?, last_checked_at = ?
            WHERE id = ?
            """,
            (price, now_str(), task_id),
        )


def update_task_notified(task_id: int, notified_price: float) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET last_notified_price = ?, last_checked_at = ?
            WHERE id = ?
            """,
            (notified_price, now_str(), task_id),
        )


def add_log(level: str, message: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO logs (created_at, level, message) VALUES (?, ?, ?)",
            (now_str(), level.upper(), message),
        )


def list_logs(limit: int = 200) -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM logs ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()
