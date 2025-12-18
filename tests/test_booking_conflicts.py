from __future__ import annotations

import unittest
from datetime import date

from hotelmanager.errors import BookingConflictError, NotFoundError, ValidationError
from hotelmanager.services import HotelManagerService


class BookingConflictTests(unittest.TestCase):
    def setUp(self) -> None:
        self.svc = HotelManagerService.open(":memory:")
        self.svc.init_db()

        self.svc.add_room(
            number="101",
            room_type="single",
            capacity=1,
            price_per_night_cents=39900,
            status="active",
        )
        self.svc.add_guest(full_name="Alice", email="alice@example.com", phone=None)

    def tearDown(self) -> None:
        self.svc.close()

    def test_booking_conflict_is_detected(self) -> None:
        self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )

        with self.assertRaises(BookingConflictError):
            self.svc.create_booking(
                room_number="101",
                guest_email="alice@example.com",
                start_date=date(2025, 12, 21),
                end_date=date(2025, 12, 23),
            )

    def test_cancel_makes_slot_available(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        self.svc.cancel_booking(booking.id)

        self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 21),
            end_date=date(2025, 12, 23),
        )

    def test_requires_existing_guest(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.create_booking(
                room_number="101",
                guest_email="missing@example.com",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 22),
            )

    def test_end_date_must_be_after_start_date(self) -> None:
        with self.assertRaises(ValidationError):
            self.svc.create_booking(
                room_number="101",
                guest_email="alice@example.com",
                start_date=date(2025, 12, 22),
                end_date=date(2025, 12, 22),
            )

    def test_booking_views_include_room_and_guest(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        views = self.svc.list_booking_views()
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0].id, booking.id)
        self.assertEqual(views[0].room_number, "101")
        self.assertEqual(views[0].guest_email, "alice@example.com")

