from __future__ import annotations

import argparse
import sys
import traceback
import unicodedata

from . import __version__
from .errors import HotelManagerError, ValidationError
from .services import HotelManagerService, format_cents, parse_date, parse_money_to_cents


def _build_common_parser(*, set_defaults: bool) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--db",
        default="hotelmanager.db" if set_defaults else argparse.SUPPRESS,
        help="SQLite 数据库路径（默认：hotelmanager.db）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False if set_defaults else argparse.SUPPRESS,
        help="输出详细异常堆栈（用于排错）",
    )
    return parser


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        print("（空）")
        return

    def cell_width(value: str) -> int:
        # 兼容中文等 East Asian 字符的显示宽度，避免表格错位（标准库实现）
        width = 0
        for ch in value:
            if unicodedata.combining(ch):
                continue
            width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        return width

    def pad(value: str, target: int) -> str:
        return value + (" " * max(0, target - cell_width(value)))

    widths = [cell_width(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], cell_width(cell))

    def fmt_row(values: list[str]) -> str:
        return "  ".join(pad(v, widths[i]) for i, v in enumerate(values))

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
        rooms = svc.list_rooms_filtered(status=args.status)
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


def cmd_doctor(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        stats = svc.get_stats()
        info = svc.get_db_info()
        _print_table(
            ["项目", "数量"],
            [
                ["房间数", str(stats.room_count)],
                ["住客数", str(stats.guest_count)],
                ["预订数", str(stats.booking_count)],
                ["有效预订", str(stats.reserved_booking_count)],
            ],
        )
        print("")
        _print_table(
            ["项目", "值"],
            [
                ["SQLite", info.sqlite_version],
                ["schema(user_version)", str(info.user_version)],
                ["journal_mode", info.journal_mode],
                ["foreign_keys", "ON" if info.foreign_keys else "OFF"],
                ["busy_timeout(ms)", str(info.busy_timeout_ms)],
            ],
        )
        return 0
    finally:
        svc.close()


def cmd_room_status(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        room = svc.set_room_status(number=args.number, status=args.status)
        print(f"已更新房间状态：房间号={room.number}  状态={room.status}")
        return 0
    finally:
        svc.close()


def cmd_room_show(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        r = svc.get_room_by_number(args.number)
        _print_table(
            ["字段", "值"],
            [
                ["ID", str(r.id)],
                ["房间号", r.number],
                ["房型", r.room_type],
                ["容量", str(r.capacity)],
                ["每晚价格", format_cents(r.price_per_night_cents)],
                ["状态", r.status],
            ],
        )
        return 0
    finally:
        svc.close()


def cmd_room_price(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        room = svc.set_room_price(
            number=args.number,
            price_per_night_cents=parse_money_to_cents(args.price),
        )
        print(f"已更新房价：房间号={room.number}  每晚价格={format_cents(room.price_per_night_cents)}")
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
        guests = svc.list_guests_filtered(args.q)
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


def cmd_guest_show(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        g = svc.get_guest_by_email(args.email)
        _print_table(
            ["字段", "值"],
            [
                ["ID", str(g.id)],
                ["姓名", g.full_name],
                ["邮箱", g.email],
                ["电话", g.phone or ""],
                ["创建时间", g.created_at.isoformat(timespec="seconds")],
            ],
        )
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
        view = svc.get_booking_view(booking.id)
        nights = (view.end_date - view.start_date).days
        total = view.price_per_night_cents * nights
        print(
            "已创建预订："
            f"#{booking.id}  房间={view.room_number}（{view.room_type}）  "
            f"住客={view.guest_name} <{view.guest_email}>  "
            f"{view.start_date.isoformat()}~{view.end_date.isoformat()}（{nights}晚）  "
            f"总价={format_cents(total)}"
        )
        return 0
    finally:
        svc.close()


def cmd_booking_list(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        bookings = svc.list_booking_views_filtered(
            room_number=args.room,
            guest_email=args.guest_email,
            status=args.status,
        )
        rows: list[list[str]] = []
        for b in bookings:
            nights = (b.end_date - b.start_date).days
            total = b.price_per_night_cents * nights
            rows.append(
                [
                    str(b.id),
                    b.room_number,
                    b.room_type,
                    b.guest_name,
                    b.guest_email,
                    b.start_date.isoformat(),
                    b.end_date.isoformat(),
                    str(nights),
                    format_cents(b.price_per_night_cents),
                    format_cents(total),
                    b.status,
                    b.created_at.isoformat(timespec="seconds"),
                ]
            )
        _print_table(
            ["ID", "房间号", "房型", "住客", "邮箱", "Start", "End", "晚数", "每晚", "总价", "状态", "创建时间"],
            rows,
        )
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


def cmd_booking_show(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        b = svc.get_booking_view(args.id)
        nights = (b.end_date - b.start_date).days
        total = b.price_per_night_cents * nights
        _print_table(
            ["字段", "值"],
            [
                ["ID", str(b.id)],
                ["房间号", b.room_number],
                ["房型", b.room_type],
                ["住客", b.guest_name],
                ["住客邮箱", b.guest_email],
                ["Start", b.start_date.isoformat()],
                ["End", b.end_date.isoformat()],
                ["晚数", str(nights)],
                ["每晚价格", format_cents(b.price_per_night_cents)],
                ["总价", format_cents(total)],
                ["状态", b.status],
                ["创建时间", b.created_at.isoformat(timespec="seconds")],
            ],
        )
        return 0
    finally:
        svc.close()


def cmd_room_available(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        start = parse_date(args.start)
        end = parse_date(args.end)
        rooms = svc.list_available_rooms(
            start_date=start,
            end_date=end,
            min_capacity=args.min_capacity,
            room_type=args.type,
        )
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
        print(f"可用房间（{start.isoformat()}~{end.isoformat()}，闭开区间 [start, end)）：")
        _print_table(["ID", "房间号", "房型", "容量", "每晚价格", "状态"], rows)
        return 0
    finally:
        svc.close()


def cmd_booking_quote(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        start = parse_date(args.start)
        end = parse_date(args.end)
        room, nights, total_cents = svc.quote_booking_cost(
            room_number=args.room,
            start_date=start,
            end_date=end,
        )
        _print_table(
            ["字段", "值"],
            [
                ["房间号", room.number],
                ["房型", room.room_type],
                ["容量", str(room.capacity)],
                ["状态", room.status],
                ["Start", start.isoformat()],
                ["End", end.isoformat()],
                ["晚数", str(nights)],
                ["每晚价格", format_cents(room.price_per_night_cents)],
                ["预估总价", format_cents(total_cents)],
            ],
        )
        return 0
    finally:
        svc.close()

def build_parser() -> argparse.ArgumentParser:
    main_common = _build_common_parser(set_defaults=True)
    sub_common = _build_common_parser(set_defaults=False)

    parser = argparse.ArgumentParser(
        prog="hotelmanager",
        description="HotelManager - 轻量酒店管理 CLI（房间/住客/预订 + SQLite）",
        parents=[main_common],
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="输出版本号并退出",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", parents=[sub_common], help="初始化数据库")
    p_init.set_defaults(func=cmd_init)

    p_doctor = sub.add_parser("doctor", parents=[sub_common], help="数据库健康检查")
    p_doctor.set_defaults(func=cmd_doctor)

    # room
    p_room = sub.add_parser("room", help="房间管理")
    room_sub = p_room.add_subparsers(dest="room_cmd", required=True)

    p_room_add = room_sub.add_parser("add", parents=[sub_common], help="新增房间")
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

    p_room_list = room_sub.add_parser("list", parents=[sub_common], help="查看房间列表")
    p_room_list.add_argument(
        "--status",
        default=None,
        choices=["active", "maintenance"],
        help="按状态过滤（可选）",
    )
    p_room_list.set_defaults(func=cmd_room_list)

    p_room_status = room_sub.add_parser("status", parents=[sub_common], help="设置房间状态")
    p_room_status.add_argument("--number", required=True, help="房间号（如 101）")
    p_room_status.add_argument(
        "--status",
        required=True,
        choices=["active", "maintenance"],
        help="目标状态",
    )
    p_room_status.set_defaults(func=cmd_room_status)

    p_room_show = room_sub.add_parser("show", parents=[sub_common], help="查看房间详情")
    p_room_show.add_argument("--number", required=True, help="房间号（如 101）")
    p_room_show.set_defaults(func=cmd_room_show)

    p_room_price = room_sub.add_parser("price", parents=[sub_common], help="设置房间每晚价格")
    p_room_price.add_argument("--number", required=True, help="房间号（如 101）")
    p_room_price.add_argument("--price", required=True, help="每晚价格（示例：399.00）")
    p_room_price.set_defaults(func=cmd_room_price)

    p_room_available = room_sub.add_parser("available", parents=[sub_common], help="查询可用房间（按日期区间）")
    p_room_available.add_argument("--start", required=True, help="入住日期 YYYY-MM-DD")
    p_room_available.add_argument("--end", required=True, help="退房日期 YYYY-MM-DD（必须 > start）")
    p_room_available.add_argument("--min-capacity", type=int, default=None, help="最小容量（可选）")
    p_room_available.add_argument("--type", default=None, help="房型（可选，大小写不敏感）")
    p_room_available.set_defaults(func=cmd_room_available)

    # guest
    p_guest = sub.add_parser("guest", help="住客管理")
    guest_sub = p_guest.add_subparsers(dest="guest_cmd", required=True)

    p_guest_add = guest_sub.add_parser("add", parents=[sub_common], help="新增住客")
    p_guest_add.add_argument("--name", required=True, help="姓名")
    p_guest_add.add_argument("--email", required=True, help="邮箱（唯一）")
    p_guest_add.add_argument("--phone", default=None, help="电话（可选）")
    p_guest_add.set_defaults(func=cmd_guest_add)

    p_guest_list = guest_sub.add_parser("list", parents=[sub_common], help="查看住客列表")
    p_guest_list.add_argument("--q", default=None, help="按姓名/邮箱模糊搜索（可选）")
    p_guest_list.set_defaults(func=cmd_guest_list)

    p_guest_show = guest_sub.add_parser("show", parents=[sub_common], help="查看住客详情")
    p_guest_show.add_argument("--email", required=True, help="住客邮箱")
    p_guest_show.set_defaults(func=cmd_guest_show)

    # booking
    p_booking = sub.add_parser("booking", help="预订管理")
    booking_sub = p_booking.add_subparsers(dest="booking_cmd", required=True)

    p_booking_create = booking_sub.add_parser("create", parents=[sub_common], help="创建预订")
    p_booking_create.add_argument("--room", required=True, help="房间号（如 101）")
    p_booking_create.add_argument("--guest-email", required=True, help="住客邮箱（需已存在）")
    p_booking_create.add_argument("--start", required=True, help="入住日期 YYYY-MM-DD")
    p_booking_create.add_argument("--end", required=True, help="退房日期 YYYY-MM-DD（必须 > start）")
    p_booking_create.set_defaults(func=cmd_booking_create)

    p_booking_list = booking_sub.add_parser("list", parents=[sub_common], help="查看预订列表")
    p_booking_list.add_argument("--room", default=None, help="按房间号过滤（可选）")
    p_booking_list.add_argument("--guest-email", default=None, help="按住客邮箱过滤（可选）")
    p_booking_list.add_argument(
        "--status",
        default=None,
        choices=["reserved", "cancelled"],
        help="按预订状态过滤（可选）",
    )
    p_booking_list.set_defaults(func=cmd_booking_list)

    p_booking_cancel = booking_sub.add_parser("cancel", parents=[sub_common], help="取消预订")
    p_booking_cancel.add_argument("--id", type=int, required=True, help="预订 ID")
    p_booking_cancel.set_defaults(func=cmd_booking_cancel)

    p_booking_show = booking_sub.add_parser("show", parents=[sub_common], help="查看预订详情")
    p_booking_show.add_argument("--id", type=int, required=True, help="预订 ID")
    p_booking_show.set_defaults(func=cmd_booking_show)

    p_booking_quote = booking_sub.add_parser("quote", parents=[sub_common], help="预估价格（不创建预订）")
    p_booking_quote.add_argument("--room", required=True, help="房间号（如 101）")
    p_booking_quote.add_argument("--start", required=True, help="入住日期 YYYY-MM-DD")
    p_booking_quote.add_argument("--end", required=True, help="退房日期 YYYY-MM-DD（必须 > start）")
    p_booking_quote.set_defaults(func=cmd_booking_quote)

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
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        return 130
    except Exception:
        print("发生未预期错误。你可以加 --verbose 查看详细堆栈。", file=sys.stderr)
        if getattr(args, "verbose", False):
            traceback.print_exc()
        return 1
