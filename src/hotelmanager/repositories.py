from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone

from .domain import Booking, BookingView, Guest, Room


def _parse_iso_datetime(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


class RoomRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(
        self,
        *,
        number: str,
        room_type: str,
        capacity: int,
        price_per_night_cents: int,
        status: str,
    ) -> Room:
        cur = self._conn.execute(
            """
            INSERT INTO rooms (number, room_type, capacity, price_per_night_cents, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (number, room_type, capacity, price_per_night_cents, status),
        )
        self._conn.commit()
        return self.get_by_id(int(cur.lastrowid))

    def get_by_id(self, room_id: int) -> Room:
        row = self._conn.execute(
            "SELECT id, number, room_type, capacity, price_per_night_cents, status FROM rooms WHERE id = ?",
            (room_id,),
        ).fetchone()
        if row is None:
            raise LookupError(f"room_id={room_id} 不存在")
        return Room(
            id=int(row["id"]),
            number=str(row["number"]),
            room_type=str(row["room_type"]),
            capacity=int(row["capacity"]),
            price_per_night_cents=int(row["price_per_night_cents"]),
            status=str(row["status"]),  # type: ignore[assignment]
        )

    def get_by_number(self, number: str) -> Room | None:
        row = self._conn.execute(
            "SELECT id, number, room_type, capacity, price_per_night_cents, status FROM rooms WHERE number = ?",
            (number,),
        ).fetchone()
        if row is None:
            return None
        return Room(
            id=int(row["id"]),
            number=str(row["number"]),
            room_type=str(row["room_type"]),
            capacity=int(row["capacity"]),
            price_per_night_cents=int(row["price_per_night_cents"]),
            status=str(row["status"]),  # type: ignore[assignment]
        )

    def list_all(self) -> list[Room]:
        rows = self._conn.execute(
            "SELECT id, number, room_type, capacity, price_per_night_cents, status FROM rooms ORDER BY number"
        ).fetchall()
        return [
            Room(
                id=int(r["id"]),
                number=str(r["number"]),
                room_type=str(r["room_type"]),
                capacity=int(r["capacity"]),
                price_per_night_cents=int(r["price_per_night_cents"]),
                status=str(r["status"]),  # type: ignore[assignment]
            )
            for r in rows
        ]

    def list_filtered(self, *, status: str | None) -> list[Room]:
        if status is None:
            return self.list_all()

        rows = self._conn.execute(
            """
            SELECT id, number, room_type, capacity, price_per_night_cents, status
            FROM rooms
            WHERE status = ?
            ORDER BY number
            """,
            (status,),
        ).fetchall()
        return [
            Room(
                id=int(r["id"]),
                number=str(r["number"]),
                room_type=str(r["room_type"]),
                capacity=int(r["capacity"]),
                price_per_night_cents=int(r["price_per_night_cents"]),
                status=str(r["status"]),  # type: ignore[assignment]
            )
            for r in rows
        ]

    def list_available(
        self,
        *,
        start: date,
        end: date,
        min_capacity: int | None = None,
        room_type: str | None = None,
    ) -> list[Room]:
        conditions: list[str] = ["r.status = 'active'"]
        params: list[object] = []

        if min_capacity is not None:
            conditions.append("r.capacity >= ?")
            params.append(min_capacity)

        if room_type is not None:
            conditions.append("lower(r.room_type) = lower(?)")
            params.append(room_type)

        # 可用性：没有任何与 [start, end) 重叠的 reserved 预订
        conditions.append(
            """
            NOT EXISTS (
                SELECT 1
                FROM bookings b
                WHERE b.room_id = r.id
                  AND b.status = 'reserved'
                  AND NOT (b.end_date <= ? OR b.start_date >= ?)
            )
            """
        )
        params.extend([start.isoformat(), end.isoformat()])

        where_clause = " AND ".join(c.strip() for c in conditions)
        rows = self._conn.execute(
            f"""
            SELECT r.id, r.number, r.room_type, r.capacity, r.price_per_night_cents, r.status
            FROM rooms r
            WHERE {where_clause}
            ORDER BY r.number
            """,
            params,
        ).fetchall()
        return [
            Room(
                id=int(r["id"]),
                number=str(r["number"]),
                room_type=str(r["room_type"]),
                capacity=int(r["capacity"]),
                price_per_night_cents=int(r["price_per_night_cents"]),
                status=str(r["status"]),  # type: ignore[assignment]
            )
            for r in rows
        ]

    def set_status_by_number(self, number: str, status: str) -> Room:
        self._conn.execute(
            "UPDATE rooms SET status = ? WHERE number = ?",
            (status, number),
        )
        self._conn.commit()
        room = self.get_by_number(number)
        if room is None:
            raise LookupError(f"room.number={number} 不存在")
        return room

    def set_price_by_number(self, number: str, price_per_night_cents: int) -> Room:
        self._conn.execute(
            "UPDATE rooms SET price_per_night_cents = ? WHERE number = ?",
            (price_per_night_cents, number),
        )
        self._conn.commit()
        room = self.get_by_number(number)
        if room is None:
            raise LookupError(f"room.number={number} 不存在")
        return room


class GuestRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(
        self,
        *,
        full_name: str,
        email: str,
        phone: str | None,
        created_at: datetime,
    ) -> Guest:
        cur = self._conn.execute(
            """
            INSERT INTO guests (full_name, email, phone, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (full_name, email, phone, created_at.isoformat(timespec="seconds")),
        )
        self._conn.commit()
        return self.get_by_id(int(cur.lastrowid))

    def get_by_id(self, guest_id: int) -> Guest:
        row = self._conn.execute(
            "SELECT id, full_name, email, phone, created_at FROM guests WHERE id = ?",
            (guest_id,),
        ).fetchone()
        if row is None:
            raise LookupError(f"guest_id={guest_id} 不存在")
        return Guest(
            id=int(row["id"]),
            full_name=str(row["full_name"]),
            email=str(row["email"]),
            phone=None if row["phone"] is None else str(row["phone"]),
            created_at=_parse_iso_datetime(str(row["created_at"])),
        )

    def get_by_email(self, email: str) -> Guest | None:
        row = self._conn.execute(
            "SELECT id, full_name, email, phone, created_at FROM guests WHERE lower(email) = lower(?)",
            (email,),
        ).fetchone()
        if row is None:
            return None
        return Guest(
            id=int(row["id"]),
            full_name=str(row["full_name"]),
            email=str(row["email"]),
            phone=None if row["phone"] is None else str(row["phone"]),
            created_at=_parse_iso_datetime(str(row["created_at"])),
        )

    def list_all(self) -> list[Guest]:
        rows = self._conn.execute(
            "SELECT id, full_name, email, phone, created_at FROM guests ORDER BY created_at DESC"
        ).fetchall()
        return [
            Guest(
                id=int(r["id"]),
                full_name=str(r["full_name"]),
                email=str(r["email"]),
                phone=None if r["phone"] is None else str(r["phone"]),
                created_at=_parse_iso_datetime(str(r["created_at"])),
            )
            for r in rows
        ]

    def search(self, query: str) -> list[Guest]:
        like = f"%{query}%"
        rows = self._conn.execute(
            """
            SELECT id, full_name, email, phone, created_at
            FROM guests
            WHERE lower(full_name) LIKE lower(?)
               OR lower(email) LIKE lower(?)
            ORDER BY created_at DESC
            """,
            (like, like),
        ).fetchall()
        return [
            Guest(
                id=int(r["id"]),
                full_name=str(r["full_name"]),
                email=str(r["email"]),
                phone=None if r["phone"] is None else str(r["phone"]),
                created_at=_parse_iso_datetime(str(r["created_at"])),
            )
            for r in rows
        ]


class BookingRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def has_conflict(
        self,
        *,
        room_id: int,
        start: date,
        end: date,
        exclude_booking_id: int | None = None,
    ) -> bool:
        conditions: list[str] = [
            "room_id = ?",
            "status = 'reserved'",
            "NOT (end_date <= ? OR start_date >= ?)",
        ]
        params: list[object] = [room_id, start.isoformat(), end.isoformat()]

        if exclude_booking_id is not None:
            conditions.append("id != ?")
            params.append(exclude_booking_id)

        where_clause = " AND ".join(conditions)
        row = self._conn.execute(
            f"""
            SELECT 1
            FROM bookings
            WHERE {where_clause}
            LIMIT 1
            """,
            params,
        ).fetchone()
        return row is not None

    def create(
        self,
        *,
        room_id: int,
        guest_id: int,
        price_per_night_cents: int,
        start: date,
        end: date,
        created_at: datetime,
    ) -> Booking:
        cur = self._conn.execute(
            """
            INSERT INTO bookings (
                room_id, guest_id, start_date, end_date, price_per_night_cents, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, 'reserved', ?)
            """,
            (
                room_id,
                guest_id,
                start.isoformat(),
                end.isoformat(),
                price_per_night_cents,
                created_at.isoformat(timespec="seconds"),
            ),
        )
        self._conn.commit()
        return self.get_by_id(int(cur.lastrowid))

    def get_by_id(self, booking_id: int) -> Booking:
        row = self._conn.execute(
            """
            SELECT id, room_id, guest_id, start_date, end_date, price_per_night_cents, status, created_at
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,),
        ).fetchone()
        if row is None:
            raise LookupError(f"booking_id={booking_id} 不存在")
        return Booking(
            id=int(row["id"]),
            room_id=int(row["room_id"]),
            guest_id=int(row["guest_id"]),
            start_date=_parse_iso_date(str(row["start_date"])),
            end_date=_parse_iso_date(str(row["end_date"])),
            price_per_night_cents=int(row["price_per_night_cents"]),
            status=str(row["status"]),  # type: ignore[assignment]
            created_at=_parse_iso_datetime(str(row["created_at"])),
        )

    def cancel(self, booking_id: int) -> Booking:
        self._conn.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
            (booking_id,),
        )
        self._conn.commit()
        return self.get_by_id(booking_id)

    def update_dates(self, booking_id: int, *, start: date, end: date) -> Booking:
        self._conn.execute(
            "UPDATE bookings SET start_date = ?, end_date = ? WHERE id = ?",
            (start.isoformat(), end.isoformat(), booking_id),
        )
        self._conn.commit()
        return self.get_by_id(booking_id)

    def get_view_by_id(self, booking_id: int) -> BookingView | None:
        row = self._conn.execute(
            """
            SELECT
                b.id AS id,
                r.number AS room_number,
                r.room_type AS room_type,
                g.full_name AS guest_name,
                g.email AS guest_email,
                b.start_date AS start_date,
                b.end_date AS end_date,
                b.status AS status,
                b.price_per_night_cents AS price_per_night_cents,
                b.created_at AS created_at
            FROM bookings b
            JOIN rooms r ON r.id = b.room_id
            JOIN guests g ON g.id = b.guest_id
            WHERE b.id = ?
            """,
            (booking_id,),
        ).fetchone()
        if row is None:
            return None
        return BookingView(
            id=int(row["id"]),
            room_number=str(row["room_number"]),
            room_type=str(row["room_type"]),
            guest_name=str(row["guest_name"]),
            guest_email=str(row["guest_email"]),
            start_date=_parse_iso_date(str(row["start_date"])),
            end_date=_parse_iso_date(str(row["end_date"])),
            status=str(row["status"]),  # type: ignore[assignment]
            price_per_night_cents=int(row["price_per_night_cents"]),
            created_at=_parse_iso_datetime(str(row["created_at"])),
        )

    def list_all(self) -> list[Booking]:
        rows = self._conn.execute(
            """
            SELECT id, room_id, guest_id, start_date, end_date, price_per_night_cents, status, created_at
            FROM bookings
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [
            Booking(
                id=int(r["id"]),
                room_id=int(r["room_id"]),
                guest_id=int(r["guest_id"]),
                start_date=_parse_iso_date(str(r["start_date"])),
                end_date=_parse_iso_date(str(r["end_date"])),
                price_per_night_cents=int(r["price_per_night_cents"]),
                status=str(r["status"]),  # type: ignore[assignment]
                created_at=_parse_iso_datetime(str(r["created_at"])),
            )
            for r in rows
        ]

    def list_views(
        self,
        *,
        room_number: str | None = None,
        guest_email: str | None = None,
        status: str | None = None,
    ) -> list[BookingView]:
        conditions: list[str] = []
        params: list[object] = []
        if room_number is not None:
            conditions.append("r.number = ?")
            params.append(room_number)
        if guest_email is not None:
            conditions.append("lower(g.email) = lower(?)")
            params.append(guest_email)
        if status is not None:
            conditions.append("b.status = ?")
            params.append(status)

        where_clause = "" if not conditions else "WHERE " + " AND ".join(conditions)
        query = f"""
            SELECT
                b.id AS id,
                r.number AS room_number,
                r.room_type AS room_type,
                g.full_name AS guest_name,
                g.email AS guest_email,
                b.start_date AS start_date,
                b.end_date AS end_date,
                b.status AS status,
                b.price_per_night_cents AS price_per_night_cents,
                b.created_at AS created_at
            FROM bookings b
            JOIN rooms r ON r.id = b.room_id
            JOIN guests g ON g.id = b.guest_id
            {where_clause}
            ORDER BY b.created_at DESC
        """
        rows = self._conn.execute(query, params).fetchall()

        return [
            BookingView(
                id=int(r["id"]),
                room_number=str(r["room_number"]),
                room_type=str(r["room_type"]),
                guest_name=str(r["guest_name"]),
                guest_email=str(r["guest_email"]),
                start_date=_parse_iso_date(str(r["start_date"])),
                end_date=_parse_iso_date(str(r["end_date"])),
                status=str(r["status"]),  # type: ignore[assignment]
                price_per_night_cents=int(r["price_per_night_cents"]),
                created_at=_parse_iso_datetime(str(r["created_at"])),
            )
            for r in rows
        ]
