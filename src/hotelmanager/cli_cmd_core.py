from __future__ import annotations

import argparse

from .cli_support import print_json, print_table
from .services import HotelManagerService


def cmd_init(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        print(f"已初始化数据库：{args.db}")
        return 0
    finally:
        svc.close()


def cmd_doctor(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        stats = svc.get_stats()
        info = svc.get_db_info()
        if getattr(args, "json", False):
            print_json(
                {
                    "stats": {
                        "room_count": stats.room_count,
                        "guest_count": stats.guest_count,
                        "booking_count": stats.booking_count,
                        "reserved_booking_count": stats.reserved_booking_count,
                    },
                    "db": {
                        "sqlite_version": info.sqlite_version,
                        "schema_user_version": info.user_version,
                        "journal_mode": info.journal_mode,
                        "foreign_keys": info.foreign_keys,
                        "busy_timeout_ms": info.busy_timeout_ms,
                    },
                }
            )
            return 0

        print_table(
            ["项目", "数量"],
            [
                ["房间数", str(stats.room_count)],
                ["住客数", str(stats.guest_count)],
                ["预订数", str(stats.booking_count)],
                ["有效预订", str(stats.reserved_booking_count)],
            ],
        )
        print("")
        print_table(
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


def register(sub: argparse._SubParsersAction[argparse.ArgumentParser], sub_common: argparse.ArgumentParser) -> None:
    p_init = sub.add_parser("init", parents=[sub_common], help="初始化数据库")
    p_init.set_defaults(func=cmd_init)

    p_doctor = sub.add_parser("doctor", parents=[sub_common], help="数据库健康检查")
    p_doctor.set_defaults(func=cmd_doctor)
