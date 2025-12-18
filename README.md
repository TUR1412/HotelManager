# HotelManager

![CI](https://github.com/TUR1412/HotelManager/actions/workflows/ci.yml/badge.svg)

一个轻量、可扩展的“酒店管理”示例项目：以 **SQLite** 作为本地数据存储，提供 **命令行 CLI** 用于管理房间、住客与预订（Booking）。

> 目标定位：仓库初始化 & 专业级骨架（可运行、可测试、可 CI）。

## 目录

- [核心亮点](#核心亮点)
- [功能范围（当前版本）](#功能范围当前版本)
- [技术栈](#技术栈)
- [路线图（Roadmap）](#路线图roadmap)
- [快速开始](#快速开始)
- [开发与测试](#开发与测试)
- [设计与架构](#设计与架构)
- [贡献](#贡献)

## 核心亮点

- **零运行时依赖**：仅 Python 标准库（`sqlite3` + `argparse`）
- **分层清晰**：CLI / 服务层 / 仓储层 / Schema 分离，便于扩展
- **业务规则可验证**：预订冲突检测（日期区间采用闭开区间 `[start, end)`）
- **更真实的金额模型**：预订写入“房价快照”，后续改价不会影响历史预订展示
- **实用扩展**：可用房间查询、预订改期/延住、收入统计、CSV/JSON 导出

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
- 导出（Export）
  - 导出 rooms/guests/bookings 为 CSV
  - 列表/报表支持 `--json` 输出（便于脚本化）

## 技术栈

- Python（仅使用标准库）
- SQLite（`sqlite3`）
- CLI：`argparse`
- CI：GitHub Actions（`unittest` + `compileall`）

## 路线图（Roadmap）

> 这是一个可扩展骨架，欢迎把它发展成完整的 Hotel PMS/OMS。

- [ ] 入住 / 退房（Check-in / Check-out）状态流转
- [ ] 账单与发票（按房晚 / 折扣 / 税费）
- [ ] 房态看板（按日期/楼层/状态）
- [ ] 数据导出（CSV/JSON）与备份
- [ ] REST API / Web UI（在保持核心领域层不变的前提下扩展交互层）

## 快速开始

> 默认数据库文件：当前目录下 `hotelmanager.db`。你也可以通过 `--db` 指定路径。

### 安装（可选）

你可以直接用 `python -m hotelmanager ...` 运行；如果希望使用 `hotelmanager` 命令行入口，推荐可编辑安装：

```bash
python -m pip install -e .
```

### 一键 Demo（推荐）

仓库内提供示例脚本，按“真实使用路径”快速跑通：

```powershell
pwsh -NoLogo -NoProfile -File .\examples\demo.ps1
```

```bash
bash ./examples/demo.sh
```

安装后示例：

```bash
hotelmanager --version
hotelmanager doctor --db hotelmanager.db
```

### 常用命令

初始化数据库：

```bash
python -m hotelmanager init --db hotelmanager.db
```

健康检查（查看数据量与数据库状态）：

```bash
python -m hotelmanager doctor --db hotelmanager.db
```

查看版本：

```bash
python -m hotelmanager --version
```

新增房间：

```bash
python -m hotelmanager room add --number 101 --type single --capacity 1 --price 399.00 --db hotelmanager.db
```

设置房间状态（可用/维护）：

```bash
python -m hotelmanager room status --number 101 --status maintenance --db hotelmanager.db
```

设置房间价格：

```bash
python -m hotelmanager room price --number 101 --price 499.00 --db hotelmanager.db
```

新增住客：

```bash
python -m hotelmanager guest add --name "Alice" --email "alice@example.com" --phone "13800000000" --db hotelmanager.db
```

创建预订（日期为闭开区间：`start` 含、`end` 不含）：

```bash
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

预订改期 / 延住：

```bash
python -m hotelmanager booking reschedule --id 1 --start 2025-12-24 --end 2025-12-26 --db hotelmanager.db
python -m hotelmanager booking extend --id 1 --end 2025-12-27 --db hotelmanager.db
```

查询可用房间：

```bash
python -m hotelmanager room available --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

预估价格（不创建预订）：

```bash
python -m hotelmanager booking quote --room 101 --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

预订列表按日期区间过滤（筛选与区间重叠的预订）：

```bash
python -m hotelmanager booking list --from 2025-12-21 --to 2025-12-23 --db hotelmanager.db
```

统计收入：

```bash
python -m hotelmanager stats revenue --start 2025-12-20 --end 2025-12-30 --db hotelmanager.db
```

导出 CSV：

```bash
python -m hotelmanager export rooms --db hotelmanager.db --out rooms.csv
python -m hotelmanager export guests --db hotelmanager.db --out guests.csv
python -m hotelmanager export bookings --db hotelmanager.db --out bookings.csv
```

脚本化输出（JSON）：

```bash
python -m hotelmanager doctor --db hotelmanager.db --json
python -m hotelmanager booking list --db hotelmanager.db --json
python -m hotelmanager stats revenue --start 2025-12-20 --end 2025-12-30 --db hotelmanager.db --json
```

查看列表：

```bash
python -m hotelmanager room list --db hotelmanager.db
python -m hotelmanager guest list --db hotelmanager.db
python -m hotelmanager booking list --db hotelmanager.db
```

按状态筛选房间：

```bash
python -m hotelmanager room list --status active --db hotelmanager.db
```

按条件筛选住客（姓名/邮箱模糊搜索）：

```bash
python -m hotelmanager guest list --q alice --db hotelmanager.db
```

查看某个房间详情：

```bash
python -m hotelmanager room show --number 101 --db hotelmanager.db
```

查看某个住客详情：

```bash
python -m hotelmanager guest show --email "alice@example.com" --db hotelmanager.db
```

查看某条预订详情：

```bash
python -m hotelmanager booking show --id 1 --db hotelmanager.db
```

按条件筛选预订：

```bash
python -m hotelmanager booking list --room 101 --status reserved --db hotelmanager.db
python -m hotelmanager booking list --guest-email "alice@example.com" --db hotelmanager.db
```

取消预订：

```bash
python -m hotelmanager booking cancel --id 1 --db hotelmanager.db
```

## 开发与测试

不安装依赖的情况下运行测试（通过 `PYTHONPATH` 指向 `src/`）：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m compileall -q src tests
```

也可以使用仓库内脚本：

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\check.ps1
```

```bash
bash ./scripts/check.sh
```

## 目录结构

```
.
├─ src/
│  └─ hotelmanager/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ cli.py
│     ├─ db.py
│     ├─ domain.py
│     ├─ errors.py
│     ├─ repositories.py
│     └─ services.py
├─ tests/
│  └─ test_booking_conflicts.py
├─ .github/workflows/ci.yml
├─ pyproject.toml
└─ Task_Status.md
```

## 设计与架构

设计取舍与分层结构说明见：`docs/ARCHITECTURE.md`。

CLI 参数与用法说明见：`docs/CLI.md`。

数据库与迁移策略说明见：`docs/DB.md`。

示例脚本见：`examples/README.md`。

## 贡献

- 开发约定见：`CONTRIBUTING.md`
- 变更记录见：`CHANGELOG.md`
