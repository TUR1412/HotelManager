# 任务清单: HotelManager 深度递归进化（Quark-Level Evolution）

目录: `helloagents/plan/202512312122_hotelmanager_quark_evolution/`

---

## 1. 工程化与质量门禁
- [√] 1.1 固定 Ruff 版本并让 CI/本地一致
- [√] 1.2 Ruff 格式化并确保 CI 通过

## 2. 后端：快照导出能力
- [√] 2.1 在 Service 层实现快照聚合（stats/rooms/guests/bookings）
- [√] 2.2 在 CLI 增加 `export snapshot` 子命令（stdout/--out/--pretty），补充单元测试

## 3. 后端：查询与边界收敛（重构）
- [√] 3.1 抽取受控 SQL/where_clause 构建工具，减少重复与审计成本
- [√] 3.2 将 CLI 入口拆分为命令模块（保持对外命令兼容）

## 4. Web UI：视觉革命 + 数据导入
- [√] 4.1 Design Tokens 补强（含 code/焦点态/成功失败态）
- [√] 4.2 实现 JSON 拖拽导入：校验 schema_version 与字段，导入后刷新 KPI/列表
- [√] 4.3 可访问性增强：键盘操作与焦点可见

## 5. 文档升级
- [√] 5.1 README/CLI/UI 文档补齐“快照导出→导入”路径与架构图
- [√] 5.2 同步 helloagents/wiki 与 helloagents/CHANGELOG.md

## 6. 测试
- [√] 6.1 运行 `pwsh -File ./scripts/check.ps1`
- [√] 6.2 运行 `pwsh -File ./scripts/lint.ps1`
