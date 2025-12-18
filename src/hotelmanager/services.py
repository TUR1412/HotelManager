from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from typing import Iterable

import sqlite3

from . import db as db_module
from .domain import Booking, BookingView, Guest, HotelStats, Room
from .errors import BookingConflictError, DatabaseError, NotFoundError, ValidationError
from .repositories import BookingRepository, GuestRepository, RoomRepository


@dataclass(frozen=True, slots=True)
class DbInfo:
    user_version: int
    sqlite_version: str
    journal_mode: str
    foreign_keys: bool
    busy_timeout_ms: int


@dataclass(frozen=True, slots=True)
class RevenueReport:
    booking_count: int
    room_nights: int
    revenue_cents: int


def now_utc() -> datetime:
    # 统一存储：UTC 但以 naive datetime 写入（避免“naive/aware 混用”导致比较时报错）。
    return datetime.now(tz=timezone.utc).replace(microsecond=0, tzinfo=None)


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as e:  # pragma: no cover
        raise ValidationError(f"日期格式错误：{value}（期望 YYYY-MM-DD）") from e


def parse_money_to_cents(value: str) -> int:
    raw = value.strip()
    cleaned = raw.replace(",", "")
    cleaned = cleaned.lstrip("¥￥$")

    if not cleaned:
        raise ValidationError("价格不能为空")

    # 不做过度复杂的货币解析：拒绝科学计数法、字母等；允许 `399` / `399.00` / `¥399.00` / `1,299.99`
    if not re.fullmatch(r"\d+(?:\.\d+)?", cleaned):
        raise ValidationError(f"价格格式错误：{value}（示例：399.00）")

    if "." in cleaned:
        _, frac = cleaned.split(".", 1)
        if len(frac) > 2 and any(ch != "0" for ch in frac[2:]):
            raise ValidationError(f"价格最多保留 2 位小数：{value}")

    try:
        d = Decimal(cleaned)
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
        raise ValidationError(f"{field_name} 格式不正确：缺少或包含多个 @（{email}）")

    local_part, domain_part = email.split("@")
    if not local_part:
        raise ValidationError(f"{field_name} 格式不正确：@ 前不能为空（{email}）")
    if not domain_part:
        raise ValidationError(f"{field_name} 格式不正确：@ 后不能为空（{email}）")
    if "." not in domain_part:
        raise ValidationError(f"{field_name} 格式不正确：域名缺少 .（{email}）")
    if domain_part.startswith(".") or domain_part.endswith("."):
        raise ValidationError(f"{field_name} 格式不正确：域名不能以 . 开头/结尾（{email}）")

    if ".." in email:
        raise ValidationError(f"{field_name} 格式不正确：不能包含连续的 .（{email}）")

    # RFC 相关上限（不做过度严格校验，但尽量避免异常输入）
    if len(email) > 254:
        raise ValidationError(f"{field_name} 过长（>254）：{email}")
    if len(local_part) > 64:
        raise ValidationError(f"{field_name} 本地部分过长（>64）：{email}")

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

    def get_db_info(self) -> DbInfo:
        user_version = int(self.conn.execute("PRAGMA user_version;").fetchone()[0])
        journal_mode = str(self.conn.execute("PRAGMA journal_mode;").fetchone()[0])
        foreign_keys = bool(int(self.conn.execute("PRAGMA foreign_keys;").fetchone()[0]))
        busy_timeout_ms = int(self.conn.execute("PRAGMA busy_timeout;").fetchone()[0])
        sqlite_version = str(self.conn.execute("SELECT sqlite_version();").fetchone()[0])
        return DbInfo(
            user_version=user_version,
            sqlite_version=sqlite_version,
            journal_mode=journal_mode,
            foreign_keys=foreign_keys,
            busy_timeout_ms=busy_timeout_ms,
        )

    def get_revenue_report(self, *, start_date: date, end_date: date) -> RevenueReport:
        if end_date <= start_date:
            raise ValidationError("日期区间不合法：end 必须晚于 start（闭开区间 [start, end)）")
        booking_count, room_nights, revenue_cents = BookingRepository(self.conn).get_revenue_for_range(
            start=start_date, end=end_date
        )
        return RevenueReport(
            booking_count=booking_count,
            room_nights=room_nights,
            revenue_cents=revenue_cents,
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

    def list_rooms_filtered(self, *, status: str | None) -> list[Room]:
        if status is not None and status not in ("active", "maintenance"):
            raise ValidationError(f"未知房间状态：{status}")
        return RoomRepository(self.conn).list_filtered(status=status)

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
                created_at=now_utc(),
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

        # 并发安全：使用 IMMEDIATE 事务保证“冲突检测 + 写入”原子性，避免多进程/多线程下的竞态双订。
        with db_module.transaction(self.conn, mode="IMMEDIATE"):
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
                price_per_night_cents=room.price_per_night_cents,
                start=start_date,
                end=end_date,
                created_at=now_utc(),
            )

    def list_available_rooms(
        self,
        *,
        start_date: date,
        end_date: date,
        min_capacity: int | None = None,
        room_type: str | None = None,
    ) -> list[Room]:
        if end_date <= start_date:
            raise ValidationError("日期区间不合法：end 必须晚于 start（闭开区间 [start, end)）")
        if min_capacity is not None:
            _ensure_positive_int(min_capacity, "最小容量")
        if room_type is not None:
            room_type = _ensure_non_empty(room_type, "房型")
        return RoomRepository(self.conn).list_available(
            start=start_date,
            end=end_date,
            min_capacity=min_capacity,
            room_type=room_type,
        )

    def quote_booking_cost(
        self,
        *,
        room_number: str,
        start_date: date,
        end_date: date,
    ) -> tuple[Room, int, int]:
        room = self.get_room_by_number(room_number)
        if room.status != "active":
            raise ValidationError(f"房间不可用（状态={room.status}）：{room.number}")
        if end_date <= start_date:
            raise ValidationError("日期区间不合法：end 必须晚于 start（闭开区间 [start, end)）")

        nights = (end_date - start_date).days
        total_cents = nights * room.price_per_night_cents
        return room, nights, total_cents

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
        overlap_start: date | None = None,
        overlap_end: date | None = None,
    ) -> list[BookingView]:
        if room_number is not None:
            room_number = _ensure_non_empty(room_number, "房间号")
        if guest_email is not None:
            guest_email = _ensure_email(guest_email, "住客邮箱")
        if status is not None and status not in ("reserved", "cancelled"):
            raise ValidationError(f"未知预订状态：{status}")
        if (overlap_start is None) != (overlap_end is None):
            raise ValidationError("日期过滤必须同时提供 overlap_start 与 overlap_end（闭开区间 [start, end)）")
        if overlap_start is not None and overlap_end is not None and overlap_end <= overlap_start:
            raise ValidationError("日期过滤区间不合法：overlap_end 必须晚于 overlap_start")
        return BookingRepository(self.conn).list_views(
            room_number=room_number,
            guest_email=guest_email,
            status=status,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
        )

    def cancel_booking(self, booking_id: int) -> Booking:
        _ensure_positive_int(booking_id, "预订ID")
        try:
            return BookingRepository(self.conn).cancel(booking_id)
        except LookupError as e:
            raise NotFoundError(f"预订不存在：id={booking_id}") from e

    def reschedule_booking(self, *, booking_id: int, start_date: date, end_date: date) -> Booking:
        _ensure_positive_int(booking_id, "预订ID")
        if end_date <= start_date:
            raise ValidationError("退房日期必须晚于入住日期（end > start）")

        repo = BookingRepository(self.conn)
        try:
            with db_module.transaction(self.conn, mode="IMMEDIATE"):
                booking = repo.get_by_id(booking_id)
                if booking.status != "reserved":
                    raise ValidationError(f"仅允许对有效预订改期（当前状态={booking.status}）")

                if repo.has_conflict(
                    room_id=booking.room_id,
                    start=start_date,
                    end=end_date,
                    exclude_booking_id=booking_id,
                ):
                    raise BookingConflictError(
                        f"预订冲突：房间 room_id={booking.room_id} 在 {start_date.isoformat()}~{end_date.isoformat()} 已被占用"
                    )

                return repo.update_dates(booking_id, start=start_date, end=end_date)
        except LookupError as e:
            raise NotFoundError(f"预订不存在：id={booking_id}") from e

    def extend_booking(self, *, booking_id: int, end_date: date) -> Booking:
        _ensure_positive_int(booking_id, "预订ID")

        repo = BookingRepository(self.conn)
        try:
            with db_module.transaction(self.conn, mode="IMMEDIATE"):
                booking = repo.get_by_id(booking_id)
                if booking.status != "reserved":
                    raise ValidationError(f"仅允许对有效预订延住（当前状态={booking.status}）")

                if end_date <= booking.end_date:
                    raise ValidationError("延住必须使退房日期延后（new_end > current_end）")
                if end_date <= booking.start_date:
                    raise ValidationError("退房日期必须晚于入住日期（end > start）")

                if repo.has_conflict(
                    room_id=booking.room_id,
                    start=booking.start_date,
                    end=end_date,
                    exclude_booking_id=booking_id,
                ):
                    raise BookingConflictError(
                        f"预订冲突：房间 room_id={booking.room_id} 在 {booking.start_date.isoformat()}~{end_date.isoformat()} 已被占用"
                    )

                return repo.update_dates(booking_id, start=booking.start_date, end=end_date)
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
