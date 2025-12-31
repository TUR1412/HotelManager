# 项目技术约定（HelloAGENTS SSOT）

## 技术栈
- **Python:** 3.10+（CI 覆盖 3.10/3.11/3.12/3.13）
- **运行时依赖:** 0（仅标准库：`sqlite3` / `argparse` / `json` / `csv`）
- **数据库:** SQLite（Local-first，默认启用 WAL）
- **Web UI:** 纯静态 HTML/CSS/JS（支持导入本地 JSON 快照，不依赖后端服务）

## 分层边界（强约束）
- CLI（输入/输出）→ Service（业务规则）→ Repository（SQL 访问）→ DB（连接与迁移）
- CLI 不直接写 SQL；Repository 不包含业务规则；Service 负责事务边界与校验。

## 时间与日期
- **数据库时间:** UTC（以 `naive datetime` 写入，避免 naive/aware 混用）
- **预订日期:** ISO `YYYY-MM-DD`，区间为闭开 `[start, end)`

## 金额
- 唯一存储单位：`cents`（整数）
- 展示格式：`0.00`（CLI 输出为文本时做格式化；快照保留 cents 便于前端计算）

## 质量门禁
- **单元测试:** `pwsh -File ./scripts/check.ps1`
- **格式化/Lint:** Ruff（固定版本，见 `pyproject.toml` 与 `.github/workflows/ci.yml`）

## 安全约定
- 所有用户输入必须先校验（日期/邮箱/金额/整数）。
- SQL 必须参数化（`?` 占位符）；仅允许受控片段拼装（通过 `sql.py` 收敛）。
- Web UI 导入仅在浏览器本地解析文件，不触发网络请求。

