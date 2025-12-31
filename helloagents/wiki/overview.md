# HotelManager（HelloAGENTS SSOT）

> 本文件包含项目级别的核心信息。详细模块文档见 `modules/` 目录。

---

## 1. 项目概述

HotelManager 是一个 **零运行时依赖** 的酒店管理骨架：以 CLI + SQLite 提供可运行、可测试、可扩展、可审计的核心能力，并以静态 Web UI 建立管理台的世界级视觉与交互基线。

本次演进目标：让静态 UI 支持导入 CLI 导出的 JSON 快照，使其可在离线/本地环境展示真实数据。

### 范围
- **范围内:** 房间/住客/预订管理、冲突检测、统计报表、CSV/JSON 导出、静态管理台（含快照导入）。
- **范围外:** 多租户、在线服务化、权限系统、支付/发票（可作为后续扩展）。

---

## 2. 模块索引

| 模块名称 | 职责 | 状态 | 文档 |
|---------|------|------|------|
| CLI | 命令入口、参数解析、输出编排（表格/JSON/CSV/快照） | 🚧开发中 | modules/cli.md |
| Service | 业务规则、校验、事务边界 | ✅稳定 | modules/services.md |
| Repository | SQL 访问、查询组装、数据映射 | 🚧开发中 | modules/repositories.md |
| DB | 连接、迁移、Schema 校验 | ✅稳定 | modules/db.md |
| Web UI | 静态管理台（视觉/交互/快照导入） | 🚧开发中 | modules/web-ui.md |

---

## 3. 快速链接
- 技术约定: `helloagents/project.md`
- 架构设计: `helloagents/wiki/arch.md`
- CLI “接口”: `helloagents/wiki/api.md`
- 数据模型: `helloagents/wiki/data.md`
- 变更历史: `helloagents/history/index.md`

