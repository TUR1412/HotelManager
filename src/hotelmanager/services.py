from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable

import sqlite3

from . import db as db_module
from .domain import Booking, BookingView, Guest, HotelStats, Room
from .errors import BookingConflictError, DatabaseError, NotFoundError, ValidationError
from .repositories import BookingRepository, GuestRepository, RoomRepository


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as e:  # pragma: no cover
        raise ValidationError(f"日期格式错误：{value}（期望 YYYY-MM-DD）") from e


def parse_money_to_cents(value: str) -> int:
    try:
        d = Decimal(value)
    except InvalidOperation as e:
        raise ValidationError(f"价格格式错误：{value}（示例：399.00）") from e

    if d < 0:
        raise ValidationError("价格不能为负数")

    d = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    cents = int(d * 100)
    return cents


def format_cents(cents: int) -> str:
    d = Decimal(cents) / Decimal(100)
    return f"{d:.2f}"


def _ensure_non_empty(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name} 不能为空")
    return cleaned


def _ensure_email(value: str, field_name: str) -> str:
    email = _ensure_non_empty(value, field_name).strip()
    if " " in email:
        raise ValidationError(f"{field_name} 不能包含空格")

    if email.count("@") != 1:
        raise ValidationError(f"{field_name} 格式不正确：{email}")

    local_part, domain_part = email.split("@")
    if not local_part or not domain_part or "." not in domain_part:
        raise ValidationError(f"{field_name} 格式不正确：{email}")

    return email.lower()


def _ensure_positive_int(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValidationError(f"{field_name} 必须为正整数")
    return value


@dataclass(slots=True)
class HotelManagerService:
    conn: sqlite3.Connection

    @classmethod
    def open(cls, db_path: str) -> "HotelManagerService":
        try:
            conn = db_module.connect(db_path)
        except Exception as e:  # pragma: no cover
            raise DatabaseError(f"无法打开数据库：{db_path}") from e
        return cls(conn=conn)

    def close(self) -> None:
        self.conn.close()

    def init_db(self) -> None:
        db_module.init_db(self.conn)

    def get_stats(self) -> HotelStats:
        room_count = int(self.conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0])
        guest_count = int(self.conn.execute("SELECT COUNT(*) FROM guests").fetchone()[0])
        booking_count = int(self.conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0])
        reserved_booking_count = int(
            self.conn.execute("SELECT COUNT(*) FROM bookings WHERE status = 'reserved'").fetchone()[0]
        )
        return HotelStats(
            room_count=room_count,
            guest_count=guest_count,
            booking_count=booking_count,
            reserved_booking_count=reserved_booking_count,
        )

    # Rooms
    def add_room(
        self,
        *,
        number: str,
        room_type: str,
        capacity: int,
        price_per_night_cents: int,
        status: str = "active",
    ) -> Room:
        number = _ensure_non_empty(number, "房间号")
        room_type = _ensure_non_empty(room_type, "房型")
        _ensure_positive_int(capacity, "可住人数")

        try:
            repo = RoomRepository(self.conn)
            return repo.create(
                number=number,
                room_type=room_type,
                capacity=capacity,
                price_per_night_cents=price_per_night_cents,
                status=status,
            )
        except sqlite3.IntegrityError as e:
            raise ValidationError(f"房间号已存在：{number}") from e

    def list_rooms(self) -> list[Room]:
        return RoomRepository(self.conn).list_all()

    def get_room_by_number(self, number: str) -> Room:
        number = _ensure_non_empty(number, "房间号")
        room = RoomRepository(self.conn).get_by_number(number)
        if room is None:
            raise NotFoundError(f"房间不存在：{number}")
        return room

    def set_room_status(self, *, number: str, status: str) -> Room:
        number = _ensure_non_empty(number, "房间号")
        if status not in ("active", "maintenance"):
            raise ValidationError(f"未知房间状态：{status}")

        try:
            return RoomRepository(self.conn).set_status_by_number(number, status)
        except LookupError as e:
            raise NotFoundError(f"房间不存在：{number}") from e

    def set_room_price(self, *, number: str, price_per_night_cents: int) -> Room:
        number = _ensure_non_empty(number, "房间号")
        if price_per_night_cents < 0:
            raise ValidationError("价格不能为负数")

        try:
            return RoomRepository(self.conn).set_price_by_number(number, price_per_night_cents)
        except LookupError as e:
            raise NotFoundError(f"房间不存在：{number}") from e

    # Guests
    def add_guest(
        self,
        *,
        full_name: str,
        email: str,
        phone: str | None,
    ) -> Guest:
        full_name = _ensure_non_empty(full_name, "姓名")
        email = _ensure_email(email, "邮箱")
        phone = None if phone is None else phone.strip() or None

        repo = GuestRepository(self.conn)
        if repo.get_by_email(email) is not None:
            raise ValidationError(f"邮箱已存在：{email}")

        try:
            return repo.create(
                full_name=full_name,
                email=email,
                phone=phone,
                created_at=datetime.now().astimezone().replace(tzinfo=None),
            )
        except sqlite3.IntegrityError as e:
            raise ValidationError(f"邮箱已存在：{email}") from e

    def list_guests(self) -> list[Guest]:
        return GuestRepository(self.conn).list_all()

    def list_guests_filtered(self, query: str | None) -> list[Guest]:
        if query is None:
            return self.list_guests()
        cleaned = query.strip()
        if not cleaned:
            return self.list_guests()
        return GuestRepository(self.conn).search(cleaned)

    def get_guest_by_email(self, email: str) -> Guest:
        email = _ensure_email(email, "邮箱")
        guest = GuestRepository(self.conn).get_by_email(email)
        if guest is None:
            raise NotFoundError(f"住客不存在：{email}")
        return guest

    # Bookings
    def create_booking(
        self,
        *,
        room_number: str,
        guest_email: str,
        start_date: date,
        end_date: date,
    ) -> Booking:
        room_number = _ensure_non_empty(room_number, "房间号")
        guest_email = _ensure_email(guest_email, "住客邮箱")

        if end_date <= start_date:
            raise ValidationError("退房日期必须晚于入住日期（end > start）")

        room_repo = RoomRepository(self.conn)
        guest_repo = GuestRepository(self.conn)
        booking_repo = BookingRepository(self.conn)

        room = room_repo.get_by_number(room_number)
        if room is None:
            raise NotFoundError(f"房间不存在：{room_number}")
        if room.status != "active":
            raise ValidationError(f"房间不可用（状态={room.status}）：{room_number}")

        guest = guest_repo.get_by_email(guest_email)
        if guest is None:
            raise NotFoundError(f"住客不存在（请先新增 guest）：{guest_email}")

        if booking_repo.has_conflict(room_id=room.id, start=start_date, end=end_date):
            raise BookingConflictError(
                f"预订冲突：房间 {room_number} 在 {start_date.isoformat()}~{end_date.isoformat()} 已被占用"
            )

        return booking_repo.create(
            room_id=room.id,
            guest_id=guest.id,
            start=start_date,
            end=end_date,
            created_at=datetime.now().astimezone().replace(tzinfo=None),
        )

    def list_bookings(self) -> list[Booking]:
        return BookingRepository(self.conn).list_all()

    def list_booking_views(self) -> list[BookingView]:
        return self.list_booking_views_filtered()

    def list_booking_views_filtered(
        self,
        *,
        room_number: str | None = None,
        guest_email: str | None = None,
        status: str | None = None,
    ) -> list[BookingView]:
        if room_number is not None:
            room_number = _ensure_non_empty(room_number, "房间号")
        if guest_email is not None:
            guest_email = _ensure_email(guest_email, "住客邮箱")
        if status is not None and status not in ("reserved", "cancelled"):
            raise ValidationError(f"未知预订状态：{status}")
        return BookingRepository(self.conn).list_views(
            room_number=room_number,
            guest_email=guest_email,
            status=status,
        )

    def cancel_booking(self, booking_id: int) -> Booking:
        _ensure_positive_int(booking_id, "预订ID")
        try:
            return BookingRepository(self.conn).cancel(booking_id)
        except LookupError as e:
            raise NotFoundError(f"预订不存在：id={booking_id}") from e

    def get_booking_view(self, booking_id: int) -> BookingView:
        _ensure_positive_int(booking_id, "预订ID")
        view = BookingRepository(self.conn).get_view_by_id(booking_id)
        if view is None:
            raise NotFoundError(f"预订不存在：id={booking_id}")
        return view


def close_quietly(services: Iterable[HotelManagerService]) -> None:
    for service in services:
        try:
            service.close()
        except Exception:
            pass
