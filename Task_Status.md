# [HotelManager] 任务看板
> **环境**: Windows 11 (pwsh -NoLogo wrapper) | **框架**: Python CLI + SQLite | **档位**: 3档 (标准工程)
> **已激活矩阵**: [模块 B: 逻辑直通] + [模块 E: 幽灵防御]

## 1. 需求镜像 (Requirement Mirroring)
> **我的理解**: 该 GitHub 仓库当前为空，需要创建一个与 `HotelManager` 命名一致、可运行可测试的专业项目，并推送到远端仓库。
> **不做什么**: 不在本机后台启动任何长期驻留服务；不删除 `C:\wook` 其他目录，仅在确认推送成功后删除本次创建的 `C:\wook\HotelManager`。

## 2. 进化知识库 (Evolutionary Knowledge - Ω)
- [!] (约束) 仓库为空：需要从 0 初始化工程结构、CI、测试与可运行入口。
- [!] (约束) Windows 环境命令统一使用 `pwsh -NoLogo -NoProfile -Command '...'` 包裹（交互说明与执行日志中文）。

## 3. 执行清单 (Execution)
- [x] 1. 克隆空仓库并核对环境
- [x] 2. 定义功能范围与项目结构
- [x] 3. 实现核心领域与 SQLite 存储
- [x] 4. 实现 CLI 与文档
- [x] 5. 添加测试与 CI 校验
- [ ] 6. 提交并推送到 GitHub
- [ ] 7. 删除本地项目目录（仅本项目）
