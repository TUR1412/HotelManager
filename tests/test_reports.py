from __future__ import annotations

import unittest
from datetime import date

from hotelmanager.services import HotelManagerService


class ReportTests(unittest.TestCase):
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

    def test_revenue_report_counts_overlap_nights(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 23),  # 3 nights
        )
        self.assertEqual(booking.price_per_night_cents, 10000)

        full = self.svc.get_revenue_report(
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 23),
        )
        self.assertEqual(full.booking_count, 1)
        self.assertEqual(full.room_nights, 3)
        self.assertEqual(full.revenue_cents, 30000)

        partial = self.svc.get_revenue_report(
            start_date=date(2025, 12, 21),
            end_date=date(2025, 12, 22),
        )
        self.assertEqual(partial.booking_count, 1)
        self.assertEqual(partial.room_nights, 1)
        self.assertEqual(partial.revenue_cents, 10000)

    def test_revenue_report_excludes_cancelled(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 23),
        )
        self.svc.cancel_booking(booking.id)

        report = self.svc.get_revenue_report(
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 23),
        )
        self.assertEqual(report.booking_count, 0)
        self.assertEqual(report.room_nights, 0)
        self.assertEqual(report.revenue_cents, 0)
