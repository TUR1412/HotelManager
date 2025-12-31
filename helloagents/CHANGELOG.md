# Changelog

本文件记录 **HelloAGENTS 工作空间（SSOT）** 视角下的关键变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.5.0] - 2025-12-31

### 新增
- CLI：新增 `export snapshot`（JSON 快照），用于 Web UI 离线导入展示。
- Web UI：新增快照导入能力（拖拽/点击上传），导入后刷新 KPI 与“最新预订节拍”列表。

### 变更
- CLI：重构为薄入口 + 命令模块（`cli_cmd_*.py`）+ 通用输出工具（`cli_support.py`），降低复杂度。
- Repository：引入受控 SQL 片段构建工具（`sql.py`）以收敛 where 条件拼装与安全检查。
- 工程化：固定 Ruff 版本（CI 与本地一致，避免格式检查漂移）。

### 修复
- DB：对 `PRAGMA table_info` 动态表名增加白名单校验，避免未来误用导致注入风险。
