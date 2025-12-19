# [HotelManager] 任务看板
> **环境**: Windows 11 (pwsh -NoLogo -NoProfile wrapper) | **框架**: Python CLI + SQLite + Static UI | **档位**: 4档 (架构重构)
> **已激活矩阵**: [模块 A: 视觉矫正] + [模块 B: 逻辑直通] + [模块 E: 幽灵防御] + [模块 F: 需求镜像]

## 1. 需求镜像 (Requirement Mirroring)
> **我的理解**: 对 `HotelManager` 做原子级审查、修复与升级扩展，并重点打造世界级前端 UI；同时美化 GitHub 的 Markdown（README/Docs）。完成后推送远端，成功推送后删除本地克隆目录。
> **不做什么**: 不在本机后台启动任何长期驻留服务；不抢占端口；不执行破坏性清理（除“推送成功后删除本地克隆目录”）。

## 2. 进化知识库 (Evolutionary Knowledge - Ω)
- [!] (约束) Windows 命令统一使用 `pwsh -NoLogo -NoProfile -Command '...'`。
- [!] (前端) UI 必须满足 WCAG AA 对比度与单滚动原则。
- [!] (交付) 静态资源必须带版本号以强制刷新。

## 3. 执行清单 (Execution)
- [x] 1. 克隆仓库并核对运行环境
- [x] 2. 代码审查与功能增强（新增入住率统计）
- [x] 3. Web UI 基线搭建（Bento + 玻璃拟态 + 动效）
- [x] 4. 文档与 README 美化升级（含 UI 预览图与设计说明）
- [x] 5. 本地验证：`compileall` + `unittest` + `node --check`
- [ ] 6. Git 提交并推送到远端
- [ ] 7. 推送成功后删除本地克隆目录
