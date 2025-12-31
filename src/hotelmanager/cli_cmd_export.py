from __future__ import annotations

import argparse

from .cli_support import csv_to_string, json_to_string, write_text
from .services import HotelManagerService


def cmd_export_rooms(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        rooms = svc.list_rooms()
        rows = [
            [
                str(r.id),
                r.number,
                r.room_type,
                str(r.capacity),
                str(r.price_per_night_cents),
                r.status,
            ]
            for r in rooms
        ]
        content = csv_to_string(["id", "number", "room_type", "capacity", "price_per_night_cents", "status"], rows)
        if args.out:
            write_text(args.out, content)
        else:
            print(content, end="")
        return 0
    finally:
        svc.close()


def cmd_export_guests(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        guests = svc.list_guests()
        rows = [
            [
                str(g.id),
                g.full_name,
                g.email,
                g.phone or "",
                g.created_at.isoformat(timespec="seconds"),
            ]
            for g in guests
        ]
        content = csv_to_string(["id", "full_name", "email", "phone", "created_at"], rows)
        if args.out:
            write_text(args.out, content)
        else:
            print(content, end="")
        return 0
    finally:
        svc.close()


def cmd_export_bookings(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        views = svc.list_booking_views()
        rows: list[list[str]] = []
        for b in views:
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
                    str(b.price_per_night_cents),
                    str(total),
                    b.status,
                    b.created_at.isoformat(timespec="seconds"),
                ]
            )
        content = csv_to_string(
            [
                "id",
                "room_number",
                "room_type",
                "guest_name",
                "guest_email",
                "start_date",
                "end_date",
                "nights",
                "price_per_night_cents",
                "total_cents",
                "status",
                "created_at",
            ],
            rows,
        )
        if args.out:
            write_text(args.out, content)
        else:
            print(content, end="")
        return 0
    finally:
        svc.close()


def cmd_export_snapshot(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        snapshot = svc.export_snapshot()
        content = json_to_string(snapshot, pretty=args.pretty)
        if args.out:
            write_text(args.out, content + "\n")
        else:
            print(content)
        return 0
    finally:
        svc.close()


def register(sub: argparse._SubParsersAction[argparse.ArgumentParser], sub_common: argparse.ArgumentParser) -> None:
    p_export = sub.add_parser("export", help="导出（CSV/JSON；默认输出到 stdout）")
    export_sub = p_export.add_subparsers(dest="export_cmd", required=True)

    p_export_rooms = export_sub.add_parser("rooms", parents=[sub_common], help="导出房间 CSV")
    p_export_rooms.add_argument("--out", default=None, help="输出文件路径（可选；不填则输出到 stdout）")
    p_export_rooms.set_defaults(func=cmd_export_rooms)

    p_export_guests = export_sub.add_parser("guests", parents=[sub_common], help="导出住客 CSV")
    p_export_guests.add_argument("--out", default=None, help="输出文件路径（可选；不填则输出到 stdout）")
    p_export_guests.set_defaults(func=cmd_export_guests)

    p_export_bookings = export_sub.add_parser("bookings", parents=[sub_common], help="导出预订 CSV（含金额快照）")
    p_export_bookings.add_argument("--out", default=None, help="输出文件路径（可选；不填则输出到 stdout）")
    p_export_bookings.set_defaults(func=cmd_export_bookings)

    p_export_snapshot = export_sub.add_parser(
        "snapshot", parents=[sub_common], help="导出 JSON 快照（用于 Web UI 导入）"
    )
    p_export_snapshot.add_argument("--out", default=None, help="输出文件路径（可选；不填则输出到 stdout）")
    p_export_snapshot.add_argument("--pretty", action="store_true", help="格式化 JSON（缩进输出）")
    p_export_snapshot.set_defaults(func=cmd_export_snapshot)
