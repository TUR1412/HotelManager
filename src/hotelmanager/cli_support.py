from __future__ import annotations

import argparse
import csv
import io
import json
import unicodedata


def build_common_parser(*, set_defaults: bool) -> argparse.ArgumentParser:
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
    parser.add_argument(
        "--json",
        action="store_true",
        default=False if set_defaults else argparse.SUPPRESS,
        help="以 JSON 输出（适合脚本化）",
    )
    return parser


def json_to_string(data: object, *, pretty: bool = True) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2 if pretty else None)


def print_json(data: object) -> None:
    print(json_to_string(data, pretty=True))


def csv_to_string(headers: list[str], rows: list[list[str]]) -> str:
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue()


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        print("（空）")
        return

    def cell_width(value: str) -> int:
        # 兼容中文等 East Asian 字符的显示宽度，避免表格错位（标准库实现）。
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
