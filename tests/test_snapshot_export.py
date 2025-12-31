from __future__ import annotations

import json
import unittest
from datetime import date

from hotelmanager import __version__
from hotelmanager.services import SNAPSHOT_SCHEMA_VERSION, HotelManagerService


class SnapshotExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.svc = HotelManagerService.open(":memory:")
        self.svc.init_db()

        self.svc.add_room(
            number="101",
            room_type="single",
            capacity=1,
            price_per_night_cents=10000,
            status="active",
        )
        self.svc.add_guest(full_name="Alice", email="alice@example.com", phone=None)

    def tearDown(self) -> None:
        self.svc.close()

    def test_export_snapshot_schema_and_counts(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 23),
        )

        snapshot = self.svc.export_snapshot()
        json.dumps(snapshot)

        self.assertEqual(snapshot["schema_version"], SNAPSHOT_SCHEMA_VERSION)
        self.assertEqual(snapshot["app_version"], __version__)
        self.assertTrue(str(snapshot["generated_at"]).endswith("Z"))

        stats = snapshot["stats"]
        self.assertEqual(stats["room_count"], 1)
        self.assertEqual(stats["guest_count"], 1)
        self.assertEqual(stats["booking_count"], 1)
        self.assertEqual(stats["reserved_booking_count"], 1)

        rooms = snapshot["rooms"]
        self.assertEqual(len(rooms), 1)
        self.assertEqual(rooms[0]["number"], "101")

        guests = snapshot["guests"]
        self.assertEqual(len(guests), 1)
        self.assertEqual(guests[0]["email"], "alice@example.com")
        self.assertTrue(str(guests[0]["created_at"]).endswith("Z"))

        bookings = snapshot["bookings"]
        self.assertEqual(len(bookings), 1)
        self.assertEqual(bookings[0]["id"], booking.id)
        self.assertEqual(bookings[0]["nights"], 3)
        self.assertEqual(bookings[0]["total_cents"], 3 * booking.price_per_night_cents)
