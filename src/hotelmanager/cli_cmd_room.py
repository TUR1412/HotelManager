from __future__ import annotations

import argparse

from .cli_support import print_json, print_table
from .services import HotelManagerService, format_cents, parse_date, parse_money_to_cents


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
        rooms = svc.list_rooms_filtered(status=args.status, min_capacity=args.min_capacity, room_type=args.type)
        if getattr(args, "json", False):
            print_json(
                [
                    {
                        "id": r.id,
                        "number": r.number,
                        "room_type": r.room_type,
                        "capacity": r.capacity,
                        "price_per_night_cents": r.price_per_night_cents,
                        "status": r.status,
                    }
                    for r in rooms
                ]
            )
            return 0

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
        print_table(["ID", "房间号", "房型", "容量", "每晚价格", "状态"], rows)
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
        print_table(
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
        if getattr(args, "json", False):
            print_json(
                {
                    "range": {"start": start.isoformat(), "end": end.isoformat()},
                    "rooms": [
                        {
                            "id": r.id,
                            "number": r.number,
                            "room_type": r.room_type,
                            "capacity": r.capacity,
                            "price_per_night_cents": r.price_per_night_cents,
                            "status": r.status,
                        }
                        for r in rooms
                    ],
                }
            )
            return 0

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
        print_table(["ID", "房间号", "房型", "容量", "每晚价格", "状态"], rows)
        return 0
    finally:
        svc.close()


def register(sub: argparse._SubParsersAction[argparse.ArgumentParser], sub_common: argparse.ArgumentParser) -> None:
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
    p_room_list.add_argument("--min-capacity", type=int, default=None, help="按最小容量过滤（可选）")
    p_room_list.add_argument("--type", default=None, help="按房型过滤（可选，大小写不敏感）")
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
