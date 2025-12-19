# HotelManager

<p align="center">
  <img src="docs/hero.svg" alt="HotelManager UI Preview" width="100%" />
</p>

![CI](https://github.com/TUR1412/HotelManager/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![SQLite](https://img.shields.io/badge/SQLite-Local%20First-003B57)

一个轻量、可扩展的酒店管理引擎：**CLI + SQLite + 可视化静态 UI**。  
强调“**可运行、可测试、可扩展、可审计**”，并用世界级 UI 规范定义管理台体验基线。

> 目标定位：专业级骨架 + 运营级可视化基线（可跑、可测、可复用）。

---

## 目录

- [核心亮点](#核心亮点)
- [功能范围（当前版本）](#功能范围当前版本)
- [Web UI（静态管理台）](#web-ui静态管理台)
- [快速开始](#快速开始)
- [开发与测试](#开发与测试)
- [目录结构](#目录结构)
- [设计与架构](#设计与架构)
- [路线图（Roadmap）](#路线图roadmap)
- [贡献](#贡献)

---

## 核心亮点

- **零运行时依赖**：仅 Python 标准库（`sqlite3` + `argparse`）
- **领域层稳固**：CLI / 服务层 / 仓储层 / Schema 分离
- **业务规则可验证**：预订冲突检测（闭开区间 `[start, end)`）
- **历史金额快照**：房价调整不影响已创建预订
- **统计升级**：收入统计 + 入住率统计（按已售房晚占比）
- **UI 体验基线**：Bento Grid / 玻璃拟态 / 微动效 / 高可读性

---

## 功能范围（当前版本）

- 房间（Room）
  - 新增房间、查看房间列表
  - 按条件过滤（状态/容量/房型）
  - 查询可用房间（按日期区间）
- 住客（Guest）
  - 新增住客、查看住客列表
- 预订（Booking）
  - 创建预订（自动检测日期冲突）
  - 查看预订列表
  - 取消预订
  - 改期（reschedule）/ 延住（extend）
  - 按日期区间过滤（筛选与区间重叠的预订）
  - 价格预估（不创建预订）
- 统计（Stats）
  - 收入统计（按预订房价快照 * 房晚）
  - 入住率统计（已售房晚 / 可售房晚）
- 导出（Export）
  - 导出 rooms/guests/bookings 为 CSV
  - 列表/报表支持 `--json` 输出

---

## Web UI（静态管理台）

> UI 为静态预览，不依赖后端服务；设计目标是建立“世界级视觉与交互基线”。

### 本地预览

1. 直接打开 `web/index.html`
2. CSS 在 `web/assets/styles.css`，JS 在 `web/assets/app.js`

### 设计亮点

- **Bento Grid**：信息模块化、层级明确
- **玻璃拟态**：卡片层次与空间感
- **动效编排**：交错入场 + 微交互 + Confetti
- **高可读性**：对比度满足 WCAG AA

详细说明见：`docs/UI.md`。

---

## 快速开始

> 默认数据库文件：当前目录 `hotelmanager.db`。可通过 `--db` 指定路径。

### 安装（可选）

```bash
python -m pip install -e .
```

### 一键 Demo（推荐）

```powershell
pwsh -NoLogo -NoProfile -File .\examples\demo.ps1
```

```bash
bash ./examples/demo.sh
```

### 常用命令

初始化数据库：

```bash
python -m hotelmanager init --db hotelmanager.db
```

创建预订：

```bash
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

收入统计：

```bash
python -m hotelmanager stats revenue --start 2025-12-20 --end 2025-12-30 --db hotelmanager.db
```

入住率统计：

```bash
python -m hotelmanager stats occupancy --start 2025-12-20 --end 2025-12-30 --db hotelmanager.db
```

更多 CLI 见：`docs/CLI.md`。

---

## 开发与测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m compileall -q src tests
```

也可以使用仓库脚本：

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\check.ps1
```

---

## 目录结构

```
.
├─ src/
│  └─ hotelmanager/
├─ tests/
├─ docs/
├─ web/
│  ├─ index.html
│  └─ assets/
├─ examples/
├─ .github/
└─ pyproject.toml
```

---

## 设计与架构

设计与分层结构说明见：`docs/ARCHITECTURE.md`  
CLI 参数说明见：`docs/CLI.md`  
数据库与迁移策略见：`docs/DB.md`  
常见问题见：`docs/FAQ.md`

---

## 路线图（Roadmap）

见：`docs/ROADMAP.md`

---

## 贡献

开发约定见：`CONTRIBUTING.md`  
变更记录见：`CHANGELOG.md`
