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

    def test_booking_allows_case_insensitive_guest_email(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="ALICE@EXAMPLE.COM",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        self.assertEqual(booking.room_id, 1)

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

    def test_invalid_email_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.svc.add_guest(full_name="Bob", email="not-an-email", phone=None)

    def test_duplicate_email_is_case_insensitive(self) -> None:
        with self.assertRaises(ValidationError):
            self.svc.add_guest(full_name="Alice2", email="ALICE@EXAMPLE.COM", phone=None)

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

    def test_get_guest_by_email_case_insensitive(self) -> None:
        g = self.svc.get_guest_by_email("ALICE@EXAMPLE.COM")
        self.assertEqual(g.email, "alice@example.com")

    def test_guest_list_search(self) -> None:
        self.svc.add_guest(full_name="Bob Builder", email="bob@example.com", phone=None)
        self.assertEqual(len(self.svc.list_guests_filtered("alice")), 1)
        self.assertEqual(len(self.svc.list_guests_filtered("BOB")), 1)
        self.assertEqual(len(self.svc.list_guests_filtered("example.com")), 2)

    def test_get_room_by_number(self) -> None:
        r = self.svc.get_room_by_number("101")
        self.assertEqual(r.number, "101")
        self.assertEqual(r.status, "active")

    def test_set_room_price(self) -> None:
        updated = self.svc.set_room_price(number="101", price_per_night_cents=49900)
        self.assertEqual(updated.price_per_night_cents, 49900)

    def test_room_list_filter_by_status(self) -> None:
        self.svc.add_room(
            number="201",
            room_type="suite",
            capacity=2,
            price_per_night_cents=99900,
            status="maintenance",
        )
        active_rooms = self.svc.list_rooms_filtered(status="active")
        self.assertEqual([r.number for r in active_rooms], ["101"])

        maintenance_rooms = self.svc.list_rooms_filtered(status="maintenance")
        self.assertEqual([r.number for r in maintenance_rooms], ["201"])

    def test_room_list_can_filter_by_capacity_and_type(self) -> None:
        self.svc.add_room(
            number="201",
            room_type="suite",
            capacity=2,
            price_per_night_cents=99900,
            status="active",
        )
        self.svc.add_room(
            number="202",
            room_type="double",
            capacity=2,
            price_per_night_cents=59900,
            status="active",
        )

        cap2 = self.svc.list_rooms_filtered(status="active", min_capacity=2)
        self.assertCountEqual([r.number for r in cap2], ["201", "202"])

        suites = self.svc.list_rooms_filtered(status=None, room_type="SUITE")
        self.assertEqual([r.number for r in suites], ["201"])

    def test_maintenance_room_rejects_booking(self) -> None:
        self.svc.set_room_status(number="101", status="maintenance")
        with self.assertRaises(ValidationError):
            self.svc.create_booking(
                room_number="101",
                guest_email="alice@example.com",
                start_date=date(2025, 12, 20),
                end_date=date(2025, 12, 22),
            )

    def test_stats_counts(self) -> None:
        stats = self.svc.get_stats()
        self.assertEqual(stats.room_count, 1)
        self.assertEqual(stats.guest_count, 1)
        self.assertEqual(stats.booking_count, 0)
        self.assertEqual(stats.reserved_booking_count, 0)

        self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        stats2 = self.svc.get_stats()
        self.assertEqual(stats2.booking_count, 1)
        self.assertEqual(stats2.reserved_booking_count, 1)

    def test_booking_views_can_be_filtered(self) -> None:
        self.svc.add_room(
            number="102",
            room_type="double",
            capacity=2,
            price_per_night_cents=59900,
            status="active",
        )
        self.svc.add_guest(full_name="Bob", email="bob@example.com", phone=None)

        booking1 = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        booking2 = self.svc.create_booking(
            room_number="102",
            guest_email="bob@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        self.svc.cancel_booking(booking1.id)

        room_101 = self.svc.list_booking_views_filtered(room_number="101")
        self.assertEqual([b.id for b in room_101], [booking1.id])

        guest_bob = self.svc.list_booking_views_filtered(guest_email="BOB@EXAMPLE.COM")
        self.assertEqual([b.id for b in guest_bob], [booking2.id])

        reserved_only = self.svc.list_booking_views_filtered(status="reserved")
        self.assertEqual([b.id for b in reserved_only], [booking2.id])

        cancelled_only = self.svc.list_booking_views_filtered(status="cancelled")
        self.assertEqual([b.id for b in cancelled_only], [booking1.id])

    def test_booking_view_by_id(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        view = self.svc.get_booking_view(booking.id)
        self.assertEqual(view.id, booking.id)
        self.assertEqual(view.room_number, "101")
        self.assertEqual(view.guest_email, "alice@example.com")

    def test_booking_list_can_filter_by_overlap_date_range(self) -> None:
        b1 = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        b2 = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 22),
            end_date=date(2025, 12, 24),
        )

        only_b1 = self.svc.list_booking_views_filtered(
            overlap_start=date(2025, 12, 20),
            overlap_end=date(2025, 12, 22),
        )
        self.assertEqual([b.id for b in only_b1], [b1.id])

        both = self.svc.list_booking_views_filtered(
            overlap_start=date(2025, 12, 21),
            overlap_end=date(2025, 12, 23),
        )
        self.assertCountEqual([b.id for b in both], [b1.id, b2.id])

    def test_booking_price_is_snapshot(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        view_before = self.svc.get_booking_view(booking.id)
        self.assertEqual(view_before.price_per_night_cents, 39900)

        # 房价调整不应影响已创建预订的价格快照
        self.svc.set_room_price(number="101", price_per_night_cents=49900)
        view_after = self.svc.get_booking_view(booking.id)
        self.assertEqual(view_after.price_per_night_cents, 39900)

    def test_room_available_excludes_conflicts(self) -> None:
        self.svc.add_room(
            number="102",
            room_type="double",
            capacity=2,
            price_per_night_cents=59900,
            status="active",
        )
        self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )

        available = self.svc.list_available_rooms(
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        self.assertEqual([r.number for r in available], ["102"])

    def test_booking_can_be_rescheduled(self) -> None:
        booking = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        updated = self.svc.reschedule_booking(
            booking_id=booking.id,
            start_date=date(2025, 12, 24),
            end_date=date(2025, 12, 26),
        )
        self.assertEqual(updated.id, booking.id)
        view = self.svc.get_booking_view(booking.id)
        self.assertEqual(view.start_date, date(2025, 12, 24))
        self.assertEqual(view.end_date, date(2025, 12, 26))

    def test_booking_reschedule_detects_conflict(self) -> None:
        self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 20),
            end_date=date(2025, 12, 22),
        )
        booking2 = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 22),
            end_date=date(2025, 12, 24),
        )

        with self.assertRaises(BookingConflictError):
            self.svc.reschedule_booking(
                booking_id=booking2.id,
                start_date=date(2025, 12, 21),
                end_date=date(2025, 12, 23),
            )

        # 原预订保持不变
        view2 = self.svc.get_booking_view(booking2.id)
        self.assertEqual(view2.start_date, date(2025, 12, 22))
        self.assertEqual(view2.end_date, date(2025, 12, 24))

    def test_booking_extend_detects_conflict(self) -> None:
        booking2 = self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 22),
            end_date=date(2025, 12, 24),
        )
        self.svc.create_booking(
            room_number="101",
            guest_email="alice@example.com",
            start_date=date(2025, 12, 24),
            end_date=date(2025, 12, 26),
        )

        with self.assertRaises(BookingConflictError):
            self.svc.extend_booking(booking_id=booking2.id, end_date=date(2025, 12, 25))

        # 原预订保持不变
        view2 = self.svc.get_booking_view(booking2.id)
        self.assertEqual(view2.start_date, date(2025, 12, 22))
        self.assertEqual(view2.end_date, date(2025, 12, 24))
