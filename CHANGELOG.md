# Changelog

本文件记录项目面向用户的变更摘要。

格式参考：Keep a Changelog（但本项目不强制严格遵循）。

## [Unreleased]

## [0.3.0] - 2025-12-18

升级与扩展：

- Booking：支持改期（`booking reschedule`）与延住（`booking extend`），并加入并发安全的事务保护（避免竞态双订）
- Booking：预订列表支持按日期区间过滤（筛选与区间重叠的预订）
- Stats：新增收入统计（`stats revenue`），按“价格快照 * 房晚”统计（仅统计 reserved）
- Export：新增 CSV 导出（`export rooms/guests/bookings`）
- CLI：新增 `--json` 输出（doctor/list/report 等支持脚本化）
- DB：增强初始化校验（结构校验 + 更清晰的 WAL 失败提示 + 事务工具）
- 工程化：CI 增加 Windows 运行矩阵；增加 `pip install .` 安装校验；新增 ruff 静态检查
- 文档与示例：新增 DB/FAQ/ROADMAP 文档与 demo 脚本、仓库脚本（check/lint）

## [0.2.0] - 2025-12-18

升级与扩展：

- Booking：新增“预订价格快照”（创建预订时把当时房价写入 bookings），避免后续改价影响历史预订展示
- Rooms：新增“可用房间查询”（按日期区间过滤，支持容量/房型过滤）
- CLI：新增 `booking quote`（不创建预订，仅做价格预估）
- CLI：预订列表/详情输出增加房型、住客姓名、晚数、每晚价格与总价
- DB：新增 schema 迁移（兼容老数据库；并启用 guests.email 的不区分大小写唯一索引）

## [0.1.0] - 2025-12-18

初始可用版本：

- CLI：房间 / 住客 / 预订 管理
- SQLite 存储与 Schema 初始化
- 预订冲突检测
- `doctor` 健康检查
- GitHub Actions CI（`compileall` + `unittest`）
