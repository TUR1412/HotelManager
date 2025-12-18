from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

RoomStatus = Literal["active", "maintenance"]
BookingStatus = Literal["reserved", "cancelled"]


@dataclass(frozen=True, slots=True)
class Room:
    id: int
    number: str
    room_type: str
    capacity: int
    price_per_night_cents: int
    status: RoomStatus


@dataclass(frozen=True, slots=True)
class Guest:
    id: int
    full_name: str
    email: str
    phone: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Booking:
    id: int
    room_id: int
    guest_id: int
    start_date: date
    end_date: date
    status: BookingStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class BookingView:
    id: int
    room_number: str
    guest_email: str
    start_date: date
    end_date: date
    status: BookingStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class HotelStats:
    room_count: int
    guest_count: int
    booking_count: int
    reserved_booking_count: int

