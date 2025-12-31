from __future__ import annotations

import argparse

from .cli_support import print_json, print_table
from .services import HotelManagerService


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
        if getattr(args, "json", False):
            print_json(
                [
                    {
                        "id": g.id,
                        "full_name": g.full_name,
                        "email": g.email,
                        "phone": g.phone,
                        "created_at": g.created_at.isoformat(timespec="seconds"),
                    }
                    for g in guests
                ]
            )
            return 0

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
        print_table(["ID", "姓名", "邮箱", "电话", "创建时间"], rows)
        return 0
    finally:
        svc.close()


def cmd_guest_show(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        g = svc.get_guest_by_email(args.email)
        print_table(
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


def register(sub: argparse._SubParsersAction[argparse.ArgumentParser], sub_common: argparse.ArgumentParser) -> None:
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
