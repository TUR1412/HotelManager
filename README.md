# HotelManager

一个轻量、可扩展的“酒店管理”示例项目：以 **SQLite** 作为本地数据存储，提供 **命令行 CLI** 用于管理房间、住客与预订（Booking）。

> 目标定位：仓库初始化 & 专业级骨架（可运行、可测试、可 CI）。

## 功能范围（当前版本）

- 房间（Room）
  - 新增房间、查看房间列表
- 住客（Guest）
  - 新增住客、查看住客列表
- 预订（Booking）
  - 创建预订（自动检测日期冲突）
  - 查看预订列表
  - 取消预订

## 技术栈

- Python（仅使用标准库）
- SQLite（`sqlite3`）
- CLI：`argparse`
- CI：GitHub Actions（`unittest` + `compileall`）

## 快速开始

> 默认数据库文件：当前目录下 `hotelmanager.db`。你也可以通过 `--db` 指定路径。

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

新增住客：

```bash
python -m hotelmanager guest add --name "Alice" --email "alice@example.com" --phone "13800000000" --db hotelmanager.db
```

创建预订（日期为闭开区间：`start` 含、`end` 不含）：

```bash
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

查看列表：

```bash
python -m hotelmanager room list --db hotelmanager.db
python -m hotelmanager guest list --db hotelmanager.db
python -m hotelmanager booking list --db hotelmanager.db
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
