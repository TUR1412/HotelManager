# 架构设计

## 总体架构

```mermaid
flowchart TD
  User[运营人员/开发者] --> CLI[CLI: argparse]
  CLI --> Svc[Service: 业务规则/校验/事务]
  Svc --> Repo[Repository: SQL/映射]
  Repo --> DB[(SQLite)]

  CLI -->|export snapshot| JSON[(snapshot.json)]
  User --> Web[Web UI: 静态管理台]
  JSON --> Web
```

## 技术栈
- **后端:** Python 3.10+（标准库）
- **前端:** HTML / CSS / Vanilla JS（静态导入 JSON）
- **数据:** SQLite（WAL + foreign_keys + busy_timeout）

## 重大架构决策（ADR）

| adr_id | title | date | status | affected_modules | details |
|--------|-------|------|--------|------------------|---------|
| ADR-001 | 维持零运行时依赖并以快照导出对接 Web UI | 2025-12-31 | ✅已采纳 | CLI/Web/Service | helloagents/plan/202512312122_hotelmanager_quark_evolution/how.md#adr-001-维持零运行时依赖并以快照导出对接-web-ui |

