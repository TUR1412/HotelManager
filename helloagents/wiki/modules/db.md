# DB 模块

## 目的
提供 SQLite 连接策略、Schema 初始化/迁移与结构校验，确保运行时行为稳定可诊断。

## 模块概述
- **职责:** connect/init/migrate/validate
- **状态:** ✅稳定
- **最后更新:** 2025-12-31

## 规范
- 默认启用：`foreign_keys=ON`、`busy_timeout`、`journal_mode=WAL`（失败则明确报错，不静默降级）。
- 迁移必须可重复执行（idempotent）。
- 元信息查询（如 `PRAGMA table_info`）必须限制表名范围（白名单）。

