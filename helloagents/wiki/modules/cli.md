# CLI 模块

## 目的
提供命令入口、参数解析与输出编排，使核心业务能力可被脚本化调用，并为 Web UI 提供离线数据快照导出。

## 模块概述
- **职责:** 输入解析 → 调用 Service → 输出（表格/JSON/CSV/快照）
- **状态:** 🚧开发中
- **最后更新:** 2025-12-31

## 结构
- `src/hotelmanager/cli.py`: 薄入口（parser 组装 + 错误处理）
- `src/hotelmanager/cli_cmd_*.py`: 按业务域拆分的命令模块（core/stats/export/room/guest/booking）
- `src/hotelmanager/cli_support.py`: 输出与通用 parser 工具

## 规范
- CLI 不直接拼装 SQL；通过 Service/Repository 访问数据。
- 必须支持脚本化输出（`--json`）与可读输出（默认表格）。

