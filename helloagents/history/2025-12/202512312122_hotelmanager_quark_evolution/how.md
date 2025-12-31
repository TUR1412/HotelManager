# 技术设计: HotelManager 深度递归进化（Quark-Level Evolution）

## 技术方案

### 核心技术
- Python 标准库（sqlite3/argparse/json/csv）
- Web：Vanilla JS + CSS Design Tokens

### 实现要点
- CLI：
  - `cli.py` 作为薄入口，命令拆分到 `cli_cmd_*.py`
  - `cli_support.py` 统一表格/JSON/文件写入等工具
  - 新增 `export snapshot`：输出 JSON 快照（可选 `--pretty`）
- 后端：
  - Service 提供 `export_snapshot` 聚合数据并输出标准字段
  - Repository 使用 `sql.py` 收敛 where 子句拼装（并做危险 token 拦截）
  - DB 对 `PRAGMA table_info` 引入表名白名单
- Web：
  - `web/assets/app.js` 实现拖拽/点击导入，校验 `schema_version`
  - 导入后更新 KPI 与预订列表；全程本地解析，不联网

## 架构决策 ADR

### ADR-001: 维持零运行时依赖并以快照导出对接 Web UI
**上下文:** 需要“数据联通”的可视化体验，同时保持零运行时依赖与离线可用。
**决策:** 不引入 Web 后端；采用 CLI 导出 JSON 快照 + Web UI 本地导入。
**理由:** 简单、可靠、可审计、不增加部署复杂度。
**替代方案:** 引入 FastAPI/Flask → 拒绝：破坏零依赖定位并增加运行复杂度。

## 快照 schema（v1）

```json
{
  "schema_version": 1,
  "app_version": "0.5.0",
  "generated_at": "2025-12-31T21:22:00Z",
  "stats": { "room_count": 0, "guest_count": 0, "booking_count": 0, "reserved_booking_count": 0 },
  "rooms": [],
  "guests": [],
  "bookings": []
}
```

## 测试与验证
- Python：`pwsh -File ./scripts/check.ps1`、`pwsh -File ./scripts/lint.ps1`
- Web：`node --check web/assets/app.js`（语法检查）+ 浏览器手工导入验收
