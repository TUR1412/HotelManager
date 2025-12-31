from __future__ import annotations

from collections.abc import Sequence

_BANNED_SQL_TOKENS = (";", "\x00", "--", "/*", "*/")


def assert_safe_sql_fragment(fragment: str) -> None:
    if any(token in fragment for token in _BANNED_SQL_TOKENS):
        raise ValueError("检测到不安全的 SQL 片段（包含禁止字符/注释标记）")


def build_where_clause(conditions: Sequence[str]) -> str:
    cleaned = [c.strip() for c in conditions if c and c.strip()]
    for c in cleaned:
        assert_safe_sql_fragment(c)
    return "" if not cleaned else "WHERE " + " AND ".join(cleaned)


def build_and_conditions(conditions: Sequence[str]) -> str:
    cleaned = [c.strip() for c in conditions if c and c.strip()]
    for c in cleaned:
        assert_safe_sql_fragment(c)
    return " AND ".join(cleaned)
