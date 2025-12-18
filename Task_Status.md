# [HotelManager] 任务看板
> **环境**: Windows 11 (pwsh -NoLogo -NoProfile wrapper) | **框架**: Python CLI + SQLite | **档位**: 4档 (架构重构)
> **已激活矩阵**: [模块 B: 逻辑直通] + [模块 E: 幽灵防御] + [模块 F: 需求镜像]

## 1. 需求镜像 (Requirement Mirroring)
> **我的理解**: 对现有 `HotelManager` 仓库进行“原子级审计 + 修复 + 升级扩展”，并补齐 GitHub 文档（README/Docs/模板）以达到更专业的交付水平。
> **不做什么**: 不在本机后台启动任何长期驻留服务；不抢占端口；不做破坏性清理（除用户明确要求的“推送成功后删除本地克隆目录”）。

## 2. 进化知识库 (Evolutionary Knowledge - Ω)
- [!] (约束) Windows 环境命令统一使用 `pwsh -NoLogo -NoProfile -Command '...'` 包裹（交互说明与执行日志中文）。
- [!] (升级) Python 3.14 起 `datetime.utcnow()` 已弃用：改用 `datetime.now(timezone.utc)` 生成 UTC 时间戳。
- [!] (升级) DB 必须可演进：引入幂等迁移 + `PRAGMA user_version`，避免“已有 db 文件无法升级”。

## 3. 执行清单 (Execution)
- [x] 1. 克隆仓库并核对环境
- [x] 2. 运行 compileall + unittest（本地验证）
- [x] 3. 设计并落地 DB 迁移：预订价格快照 + 邮箱不区分大小写唯一索引
- [x] 4. 扩展功能：可用房间查询 + booking quote
- [x] 5. CLI 输出体验升级：中文宽度对齐 + 预订金额展示 + 友好兜底错误
- [x] 6. 文档升级：README/CLI/ARCHITECTURE 同步更新
- [ ] 7. 提交并推送到 GitHub（需要本机具备推送权限）
- [ ] 8. 删除本地克隆目录 `_work\\HotelManager`（仅在确认推送成功后执行）
