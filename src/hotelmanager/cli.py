from __future__ import annotations

import argparse
import sqlite3
import sys
import traceback

from . import __version__
from .cli_cmd_booking import register as register_booking
from .cli_cmd_core import register as register_core
from .cli_cmd_export import register as register_export
from .cli_cmd_guest import register as register_guest
from .cli_cmd_room import register as register_room
from .cli_cmd_stats import register as register_stats
from .cli_support import build_common_parser
from .errors import HotelManagerError, ValidationError


def build_parser() -> argparse.ArgumentParser:
    main_common = build_common_parser(set_defaults=True)
    sub_common = build_common_parser(set_defaults=False)

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
    register_core(sub, sub_common)
    register_stats(sub, sub_common)
    register_export(sub, sub_common)
    register_room(sub, sub_common)
    register_guest(sub, sub_common)
    register_booking(sub, sub_common)
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
    except sqlite3.Error as e:
        msg = str(e)
        lower = msg.lower()
        suggestion = "请运行 `doctor` 检查数据库状态。"
        if "locked" in lower:
            suggestion = "数据库被占用（locked）。请关闭其他占用该 db 的进程后重试，或稍后再试。"
        elif "readonly" in lower:
            suggestion = "数据库为只读。请检查文件权限，或将 db 放到可写目录。"
        elif "no such table" in lower:
            suggestion = "数据库缺少表。请先运行 `init` 初始化数据库。"

        print(f"数据库错误：{msg}\n建议：{suggestion}", file=sys.stderr)
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
