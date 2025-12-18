# Changelog

本文件记录项目面向用户的变更摘要。

格式参考：Keep a Changelog（但本项目不强制严格遵循）。

## [Unreleased]

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
