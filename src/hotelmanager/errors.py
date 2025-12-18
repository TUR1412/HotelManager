from __future__ import annotations


class HotelManagerError(Exception):
    """项目内可预期错误的基类（用于 CLI 友好输出）。"""


class ValidationError(HotelManagerError):
    pass


class NotFoundError(HotelManagerError):
    pass


class BookingConflictError(HotelManagerError):
    pass


class DatabaseError(HotelManagerError):
    pass
