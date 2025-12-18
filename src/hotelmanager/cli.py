from __future__ import annotations

import argparse
import sys
import traceback

from . import __version__
from .errors import HotelManagerError, ValidationError
from .services import HotelManagerService, format_cents, parse_date, parse_money_to_cents


def _add_global_db_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db",
        default="hotelmanager.db",
        help="SQLite 数据库路径（默认：hotelmanager.db）",
    )


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        print("（空）")
        return

    widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def fmt_row(values: list[str]) -> str:
        return "  ".join(v.ljust(widths[i]) for i, v in enumerate(values))

    print(fmt_row(headers))
    print(fmt_row(["-" * w for w in widths]))
    for row in rows:
        print(fmt_row(row))


def cmd_init(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        print(f"已初始化数据库：{args.db}")
        return 0
    finally:
        svc.close()


def cmd_room_add(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        room = svc.add_room(
            number=args.number,
            room_type=args.type,
            capacity=args.capacity,
            price_per_night_cents=parse_money_to_cents(args.price),
            status=args.status,
        )
        print(f"已新增房间：#{room.id}  房间号={room.number}")
        return 0
    finally:
        svc.close()


def cmd_room_list(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        rooms = svc.list_rooms()
        rows: list[list[str]] = []
        for r in rooms:
            rows.append(
                [
                    str(r.id),
                    r.number,
                    r.room_type,
                    str(r.capacity),
                    format_cents(r.price_per_night_cents),
                    r.status,
                ]
            )
        _print_table(["ID", "房间号", "房型", "容量", "每晚价格", "状态"], rows)
        return 0
    finally:
        svc.close()


def cmd_guest_add(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        guest = svc.add_guest(full_name=args.name, email=args.email, phone=args.phone)
        print(f"已新增住客：#{guest.id}  {guest.full_name} <{guest.email}>")
        return 0
    finally:
        svc.close()


def cmd_guest_list(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        guests = svc.list_guests()
        rows: list[list[str]] = []
        for g in guests:
            rows.append(
                [
                    str(g.id),
                    g.full_name,
                    g.email,
                    g.phone or "",
                    g.created_at.isoformat(timespec="seconds"),
                ]
            )
        _print_table(["ID", "姓名", "邮箱", "电话", "创建时间"], rows)
        return 0
    finally:
        svc.close()


def cmd_booking_create(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        start = parse_date(args.start)
        end = parse_date(args.end)
        booking = svc.create_booking(
            room_number=args.room,
            guest_email=args.guest_email,
            start_date=start,
            end_date=end,
        )
        print(
            "已创建预订："
            f"#{booking.id}  room_id={booking.room_id}  guest_id={booking.guest_id}  "
            f"{booking.start_date.isoformat()}~{booking.end_date.isoformat()}"
        )
        return 0
    finally:
        svc.close()


def cmd_booking_list(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        bookings = svc.list_booking_views()
        rows: list[list[str]] = []
        for b in bookings:
            rows.append(
                [
                    str(b.id),
                    b.room_number,
                    b.guest_email,
                    b.start_date.isoformat(),
                    b.end_date.isoformat(),
                    b.status,
                    b.created_at.isoformat(timespec="seconds"),
                ]
            )
        _print_table(["ID", "房间号", "住客邮箱", "Start", "End", "状态", "创建时间"], rows)
        return 0
    finally:
        svc.close()


def cmd_booking_cancel(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        booking = svc.cancel_booking(args.id)
        print(f"已取消预订：#{booking.id}")
        return 0
    finally:
        svc.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hotelmanager",
        description="HotelManager - 轻量酒店管理 CLI（房间/住客/预订 + SQLite）",
    )
    _add_global_db_arg(parser)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出详细异常堆栈（用于排错）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="输出版本号并退出",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化数据库")
    p_init.set_defaults(func=cmd_init)

    # room
    p_room = sub.add_parser("room", help="房间管理")
    room_sub = p_room.add_subparsers(dest="room_cmd", required=True)

    p_room_add = room_sub.add_parser("add", help="新增房间")
    p_room_add.add_argument("--number", required=True, help="房间号（如 101）")
    p_room_add.add_argument("--type", required=True, help="房型（如 single/double/suite）")
    p_room_add.add_argument("--capacity", type=int, required=True, help="可住人数（正整数）")
    p_room_add.add_argument("--price", required=True, help="每晚价格（示例：399.00）")
    p_room_add.add_argument(
        "--status",
        default="active",
        choices=["active", "maintenance"],
        help="房间状态（默认：active）",
    )
    p_room_add.set_defaults(func=cmd_room_add)

    p_room_list = room_sub.add_parser("list", help="查看房间列表")
    p_room_list.set_defaults(func=cmd_room_list)

    # guest
    p_guest = sub.add_parser("guest", help="住客管理")
    guest_sub = p_guest.add_subparsers(dest="guest_cmd", required=True)

    p_guest_add = guest_sub.add_parser("add", help="新增住客")
    p_guest_add.add_argument("--name", required=True, help="姓名")
    p_guest_add.add_argument("--email", required=True, help="邮箱（唯一）")
    p_guest_add.add_argument("--phone", default=None, help="电话（可选）")
    p_guest_add.set_defaults(func=cmd_guest_add)

    p_guest_list = guest_sub.add_parser("list", help="查看住客列表")
    p_guest_list.set_defaults(func=cmd_guest_list)

    # booking
    p_booking = sub.add_parser("booking", help="预订管理")
    booking_sub = p_booking.add_subparsers(dest="booking_cmd", required=True)

    p_booking_create = booking_sub.add_parser("create", help="创建预订")
    p_booking_create.add_argument("--room", required=True, help="房间号（如 101）")
    p_booking_create.add_argument("--guest-email", required=True, help="住客邮箱（需已存在）")
    p_booking_create.add_argument("--start", required=True, help="入住日期 YYYY-MM-DD")
    p_booking_create.add_argument("--end", required=True, help="退房日期 YYYY-MM-DD（必须 > start）")
    p_booking_create.set_defaults(func=cmd_booking_create)

    p_booking_list = booking_sub.add_parser("list", help="查看预订列表")
    p_booking_list.set_defaults(func=cmd_booking_list)

    p_booking_cancel = booking_sub.add_parser("cancel", help="取消预订")
    p_booking_cancel.add_argument("--id", type=int, required=True, help="预订 ID")
    p_booking_cancel.set_defaults(func=cmd_booking_cancel)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except ValidationError as e:
        print(f"参数错误：{e}", file=sys.stderr)
        if getattr(args, "verbose", False):
            traceback.print_exc()
        return 2
    except HotelManagerError as e:
        print(f"错误：{e}", file=sys.stderr)
        if getattr(args, "verbose", False):
            traceback.print_exc()
        return 2
