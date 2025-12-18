from __future__ import annotations

import sqlite3
from pathlib import Path

from .errors import DatabaseError


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL UNIQUE,
    room_type TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    price_per_night_cents INTEGER NOT NULL CHECK (price_per_night_cents >= 0),
    status TEXT NOT NULL CHECK (status IN ('active', 'maintenance'))
);

CREATE TABLE IF NOT EXISTS guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    guest_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    price_per_night_cents INTEGER NOT NULL CHECK (price_per_night_cents >= 0),
    status TEXT NOT NULL CHECK (status IN ('reserved', 'cancelled')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE RESTRICT,
    CHECK (start_date < end_date)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_guests_email_nocase
    ON guests (lower(email));

CREATE INDEX IF NOT EXISTS idx_bookings_room_dates
    ON bookings (room_id, start_date, end_date, status);

CREATE INDEX IF NOT EXISTS idx_bookings_room_status_dates
    ON bookings (room_id, status, start_date, end_date);
"""

CURRENT_SCHEMA_VERSION = 2


def _get_user_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version;").fetchone()[0])


def _set_user_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(f"PRAGMA user_version = {int(version)};")


def _table_has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return any(str(r["name"]) == column for r in rows)


def _migrate_legacy_schema(conn: sqlite3.Connection) -> None:
    """
    迁移逻辑必须“可重复执行”（idempotent），以兼容：
    - 老版本未设置 user_version（值为 0）的数据库
    - 用户复制/迁移数据库文件导致版本号不可信的情况
    """
    if not _table_has_column(conn, "bookings", "price_per_night_cents"):
        conn.execute(
            """
            ALTER TABLE bookings
                ADD COLUMN price_per_night_cents INTEGER NOT NULL DEFAULT 0
                    CHECK (price_per_night_cents >= 0);
            """
        )
        # 尽量用当前房价回填（历史价格无法还原，但至少避免 0 造成误导）
        conn.execute(
            """
            UPDATE bookings
            SET price_per_night_cents = (
                SELECT r.price_per_night_cents
                FROM rooms r
                WHERE r.id = bookings.room_id
            )
            WHERE price_per_night_cents = 0;
            """
        )

    # guests 邮箱历史上可能存在大小写重复；这里强制建立约束，失败则给出可行动提示。
    try:
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_guests_email_nocase
                ON guests (lower(email));
            """
        )
    except sqlite3.IntegrityError as e:  # pragma: no cover
        raise DatabaseError(
            "检测到 guests.email 存在大小写重复，无法升级为不区分大小写的唯一约束。"
            "请先清理重复数据（保留一个邮箱记录），再重试。"
        ) from e


def connect(db_path: str) -> sqlite3.Connection:
    if db_path != ":memory:":
        path = Path(db_path).expanduser()
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        db_path = str(path)

    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    if db_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    _migrate_legacy_schema(conn)

    current = _get_user_version(conn)
    if current == 0:
        _set_user_version(conn, CURRENT_SCHEMA_VERSION)
    elif current > CURRENT_SCHEMA_VERSION:  # pragma: no cover
        raise DatabaseError(
            f"数据库 schema 版本过新（user_version={current} > {CURRENT_SCHEMA_VERSION}），"
            "当前程序无法保证兼容，请升级 HotelManager。"
        )
    else:
        _set_user_version(conn, CURRENT_SCHEMA_VERSION)
    conn.commit()
