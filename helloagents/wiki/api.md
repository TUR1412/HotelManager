# CLI 接口（作为“API”）

## 概述
本项目无 HTTP API；CLI 本身即对外接口。此处以“可脚本化 API”的方式记录命令、参数与输出形态（文本/JSON/CSV/快照）。

## 全局参数
- `--db`: SQLite 数据库路径（默认 `hotelmanager.db`）
- `--json`: 以 JSON 输出（适合脚本化）
- `--verbose`: 输出详细异常堆栈（用于排错）

## 命令列表（摘要）
- `init`: 初始化数据库
- `doctor`: 数据库健康检查
- `stats revenue|occupancy`: 报表
- `export rooms|guests|bookings`: 导出 CSV
- `export snapshot`: 导出 JSON 快照（用于 Web UI 导入，支持 `--pretty`）
- `room ...`: 房间管理
- `guest ...`: 住客管理
- `booking ...`: 预订管理

