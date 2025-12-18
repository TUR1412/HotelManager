from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from datetime import date

from hotelmanager.services import HotelManagerService


LEGACY_SCHEMA_V1 = """
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

-- 注意：legacy 版本的 bookings 没有 price_per_night_cents
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    guest_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('reserved', 'cancelled')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE RESTRICT,
    CHECK (start_date < end_date)
);
"""


def create_legacy_db_v1(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(LEGACY_SCHEMA_V1)

        cur_room = conn.execute(
            """
            INSERT INTO rooms (number, room_type, capacity, price_per_night_cents, status)
            VALUES ('101', 'single', 1, 39900, 'active')
            """
        )
        room_id = int(cur_room.lastrowid)

        cur_guest = conn.execute(
            """
            INSERT INTO guests (full_name, email, phone, created_at)
            VALUES ('Alice', 'alice@example.com', NULL, '2025-12-18T00:00:00')
            """
        )
        guest_id = int(cur_guest.lastrowid)

        conn.execute(
            """
            INSERT INTO bookings (room_id, guest_id, start_date, end_date, status, created_at)
            VALUES (?, ?, ?, ?, 'reserved', '2025-12-18T00:00:00')
            """,
            (room_id, guest_id, "2025-12-20", "2025-12-22"),
        )
        conn.commit()
    finally:
        conn.close()


class MigrationTests(unittest.TestCase):
    def test_init_db_migrates_legacy_schema_v1(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = os.path.join(td, "legacy.db")
            create_legacy_db_v1(db_path)

            svc = HotelManagerService.open(db_path)
            try:
                # 迁移应可重复执行（幂等）
                svc.init_db()
                svc.init_db()

                view = svc.get_booking_view(1)
                self.assertEqual(view.room_number, "101")
                self.assertEqual(view.guest_email, "alice@example.com")

                # legacy 没有 price_per_night_cents，迁移后应至少回填为当前房价
                self.assertEqual(view.price_per_night_cents, 39900)

                # 预订区间仍然正确
                self.assertEqual(view.start_date, date(2025, 12, 20))
                self.assertEqual(view.end_date, date(2025, 12, 22))

                info = svc.get_db_info()
                self.assertGreaterEqual(info.user_version, 2)
            finally:
                svc.close()

