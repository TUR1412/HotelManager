from __future__ import annotations

import argparse

from .cli_support import print_json, print_table
from .services import HotelManagerService, format_cents, parse_date


def cmd_stats_revenue(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        start = parse_date(args.start)
        end = parse_date(args.end)
        report = svc.get_revenue_report(start_date=start, end_date=end)

        avg = 0 if report.room_nights == 0 else report.revenue_cents // report.room_nights
        if getattr(args, "json", False):
            print_json(
                {
                    "range": {"start": start.isoformat(), "end": end.isoformat()},
                    "booking_count": report.booking_count,
                    "room_nights": report.room_nights,
                    "revenue_cents": report.revenue_cents,
                    "avg_price_per_night_cents": avg,
                }
            )
            return 0

        print_table(
            ["项目", "值"],
            [
                ["区间", f"{start.isoformat()}~{end.isoformat()}（闭开 [start, end)）"],
                ["预订数", str(report.booking_count)],
                ["房晚数", str(report.room_nights)],
                ["收入", format_cents(report.revenue_cents)],
                ["平均每晚", format_cents(avg)],
            ],
        )
        return 0
    finally:
        svc.close()


def cmd_stats_occupancy(args: argparse.Namespace) -> int:
    svc = HotelManagerService.open(args.db)
    try:
        svc.init_db()
        start = parse_date(args.start)
        end = parse_date(args.end)
        report = svc.get_occupancy_report(start_date=start, end_date=end)

        percent = 0.0 if report.available_room_nights == 0 else report.occupancy_rate * 100
        if getattr(args, "json", False):
            print_json(
                {
                    "range": {"start": start.isoformat(), "end": end.isoformat()},
                    "room_count": report.room_count,
                    "available_room_nights": report.available_room_nights,
                    "room_nights": report.room_nights,
                    "occupancy_rate": report.occupancy_rate,
                    "occupancy_percent": round(percent, 2),
                }
            )
            return 0

        print_table(
            ["项目", "值"],
            [
                ["区间", f"{start.isoformat()}~{end.isoformat()}（闭开 [start, end)）"],
                ["可售房间数", str(report.room_count)],
                ["可售房晚", str(report.available_room_nights)],
                ["已售房晚", str(report.room_nights)],
                ["入住率", f"{percent:.2f}%"],
            ],
        )
        return 0
    finally:
        svc.close()


def register(sub: argparse._SubParsersAction[argparse.ArgumentParser], sub_common: argparse.ArgumentParser) -> None:
    p_stats = sub.add_parser("stats", help="统计报表")
    stats_sub = p_stats.add_subparsers(dest="stats_cmd", required=True)

    p_stats_revenue = stats_sub.add_parser("revenue", parents=[sub_common], help="统计收入（按预订房价快照）")
    p_stats_revenue.add_argument("--start", required=True, help="起始日期 YYYY-MM-DD（含）")
    p_stats_revenue.add_argument("--end", required=True, help="结束日期 YYYY-MM-DD（不含）")
    p_stats_revenue.set_defaults(func=cmd_stats_revenue)

    p_stats_occupancy = stats_sub.add_parser("occupancy", parents=[sub_common], help="入住率统计（按房晚占比）")
    p_stats_occupancy.add_argument("--start", required=True, help="起始日期 YYYY-MM-DD（含）")
    p_stats_occupancy.add_argument("--end", required=True, help="结束日期 YYYY-MM-DD（不含）")
    p_stats_occupancy.set_defaults(func=cmd_stats_occupancy)
