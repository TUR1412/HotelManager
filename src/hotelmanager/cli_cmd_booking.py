from __future__ import annotations

import argparse

from .cli_support import print_json, print_table
from .services import HotelManagerService, format_cents, parse_date


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
        overlap_start = None if args.date_from is None else parse_date(args.date_from)
        overlap_end = None if args.date_to is None else parse_date(args.date_to)
        bookings = svc.list_booking_views_filtered(
            room_number=args.room,
            guest_email=args.guest_email,
            status=args.status,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
        )
        if getattr(args, "json", False):
            print_json(
                [
                    {
                        "id": b.id,
                        "room_number": b.room_number,
                        "room_type": b.room_type,
                        "guest_name": b.guest_name,
                        "guest_email": b.guest_email,
                        "start_date": b.start_date.isoformat(),
                        "end_date": b.end_date.isoformat(),
                        "nights": (b.end_date - b.start_date).days,
                        "price_per_night_cents": b.price_per_night_cents,
                        "total_cents": b.price_per_night_cents * (b.end_date - b.start_date).days,
                        "status": b.status,
                        "created_at": b.created_at.isoformat(timespec="seconds"),
                    }
                    for b in bookings
                ]
            )
            return 0

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
        print_table(
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
        print_table(
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


def cmd_booking_reschedule(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        start = parse_date(args.start)
        end = parse_date(args.end)
        updated = svc.reschedule_booking(booking_id=args.id, start_date=start, end_date=end)
        view = svc.get_booking_view(updated.id)

        nights = (view.end_date - view.start_date).days
        total = view.price_per_night_cents * nights
        print(f"已改期预订：#{view.id}")
        print_table(
            ["字段", "值"],
            [
                ["房间号", view.room_number],
                ["房型", view.room_type],
                ["住客", view.guest_name],
                ["邮箱", view.guest_email],
                ["Start", view.start_date.isoformat()],
                ["End", view.end_date.isoformat()],
                ["晚数", str(nights)],
                ["每晚价格", format_cents(view.price_per_night_cents)],
                ["总价", format_cents(total)],
                ["状态", view.status],
            ],
        )
        return 0
    finally:
        svc.close()


def cmd_booking_extend(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        end = parse_date(args.end)
        updated = svc.extend_booking(booking_id=args.id, end_date=end)
        view = svc.get_booking_view(updated.id)

        nights = (view.end_date - view.start_date).days
        total = view.price_per_night_cents * nights
        print(f"已延住预订：#{view.id}")
        print_table(
            ["字段", "值"],
            [
                ["房间号", view.room_number],
                ["房型", view.room_type],
                ["住客", view.guest_name],
                ["邮箱", view.guest_email],
                ["Start", view.start_date.isoformat()],
                ["End", view.end_date.isoformat()],
                ["晚数", str(nights)],
                ["每晚价格", format_cents(view.price_per_night_cents)],
                ["总价", format_cents(total)],
                ["状态", view.status],
            ],
        )
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
        if getattr(args, "json", False):
            print_json(
                {
                    "room": {
                        "id": room.id,
                        "number": room.number,
                        "room_type": room.room_type,
                        "capacity": room.capacity,
                        "price_per_night_cents": room.price_per_night_cents,
                        "status": room.status,
                    },
                    "range": {"start": start.isoformat(), "end": end.isoformat()},
                    "nights": nights,
                    "total_cents": total_cents,
                }
            )
            return 0

        print_table(
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


def register(sub: argparse._SubParsersAction[argparse.ArgumentParser], sub_common: argparse.ArgumentParser) -> None:
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
        "--from",
        dest="date_from",
        default=None,
        help="按日期区间过滤（筛选与该区间重叠的预订）：from YYYY-MM-DD（可选，需要配合 --to）",
    )
    p_booking_list.add_argument(
        "--to",
        dest="date_to",
        default=None,
        help="按日期区间过滤（筛选与该区间重叠的预订）：to YYYY-MM-DD（可选，需要配合 --from）",
    )
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

    p_booking_reschedule = booking_sub.add_parser("reschedule", parents=[sub_common], help="预订改期")
    p_booking_reschedule.add_argument("--id", type=int, required=True, help="预订 ID")
    p_booking_reschedule.add_argument("--start", required=True, help="入住日期 YYYY-MM-DD")
    p_booking_reschedule.add_argument("--end", required=True, help="退房日期 YYYY-MM-DD（必须 > start）")
    p_booking_reschedule.set_defaults(func=cmd_booking_reschedule)

    p_booking_extend = booking_sub.add_parser("extend", parents=[sub_common], help="预订延住（仅延后退房日期）")
    p_booking_extend.add_argument("--id", type=int, required=True, help="预订 ID")
    p_booking_extend.add_argument("--end", required=True, help="新的退房日期 YYYY-MM-DD（必须 > 当前 end）")
    p_booking_extend.set_defaults(func=cmd_booking_extend)

    p_booking_quote = booking_sub.add_parser("quote", parents=[sub_common], help="预估价格（不创建预订）")
    p_booking_quote.add_argument("--room", required=True, help="房间号（如 101）")
    p_booking_quote.add_argument("--start", required=True, help="入住日期 YYYY-MM-DD")
    p_booking_quote.add_argument("--end", required=True, help="退房日期 YYYY-MM-DD（必须 > start）")
    p_booking_quote.set_defaults(func=cmd_booking_quote)
