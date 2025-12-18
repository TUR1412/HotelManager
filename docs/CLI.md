# CLI 使用说明

本项目提供命令行工具 `hotelmanager`（或使用 `python -m hotelmanager` 运行）。

## 0. 全局参数

以下参数在 **主命令** 与 **子命令** 上都可用：

- `--db`：SQLite 数据库路径（默认：`hotelmanager.db`）
- `--verbose`：输出详细异常堆栈（用于排错）
- `--version`：输出版本号并退出
- `--json`：以 JSON 输出（适合脚本化；部分命令支持）

示例（两种写法等价）：

```bash
python -m hotelmanager doctor --db hotelmanager.db
python -m hotelmanager --db hotelmanager.db doctor
```

## 1. 初始化与健康检查

初始化数据库：

```bash
python -m hotelmanager init --db hotelmanager.db
```

健康检查（统计房间/住客/预订数量）：

```bash
python -m hotelmanager doctor --db hotelmanager.db
```

## 2. 房间（room）

新增房间：

```bash
python -m hotelmanager room add --number 101 --type single --capacity 1 --price 399.00 --db hotelmanager.db
```

查看房间列表（支持按状态过滤）：

```bash
python -m hotelmanager room list --db hotelmanager.db
python -m hotelmanager room list --status active --db hotelmanager.db
```

按容量/房型过滤：

```bash
python -m hotelmanager room list --min-capacity 2 --db hotelmanager.db
python -m hotelmanager room list --type suite --db hotelmanager.db
```

查看房间详情：

```bash
python -m hotelmanager room show --number 101 --db hotelmanager.db
```

设置房间状态：

```bash
python -m hotelmanager room status --number 101 --status maintenance --db hotelmanager.db
```

设置房间价格：

```bash
python -m hotelmanager room price --number 101 --price 499.00 --db hotelmanager.db
```

查询可用房间（按日期区间 `[start, end)`，支持容量/房型过滤）：

```bash
python -m hotelmanager room available --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
python -m hotelmanager room available --start 2025-12-20 --end 2025-12-22 --min-capacity 2 --type double --db hotelmanager.db
```

## 3. 住客（guest）

新增住客：

```bash
python -m hotelmanager guest add --name "Alice" --email "alice@example.com" --phone "13800000000" --db hotelmanager.db
```

查看住客列表（支持模糊搜索）：

```bash
python -m hotelmanager guest list --db hotelmanager.db
python -m hotelmanager guest list --q alice --db hotelmanager.db
```

查看住客详情：

```bash
python -m hotelmanager guest show --email "alice@example.com" --db hotelmanager.db
```

## 4. 预订（booking）

创建预订（日期区间为闭开区间 `[start, end)`）：

```bash
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

查看预订列表（支持过滤）：

```bash
python -m hotelmanager booking list --db hotelmanager.db
python -m hotelmanager booking list --room 101 --status reserved --db hotelmanager.db
python -m hotelmanager booking list --guest-email "alice@example.com" --db hotelmanager.db
```

按日期区间过滤（筛选与区间重叠的预订）：

```bash
python -m hotelmanager booking list --from 2025-12-21 --to 2025-12-23 --db hotelmanager.db
```

查看预订详情：

```bash
python -m hotelmanager booking show --id 1 --db hotelmanager.db
```

取消预订：

```bash
python -m hotelmanager booking cancel --id 1 --db hotelmanager.db
```

预估价格（不创建预订）：

```bash
python -m hotelmanager booking quote --room 101 --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

预订改期：

```bash
python -m hotelmanager booking reschedule --id 1 --start 2025-12-24 --end 2025-12-26 --db hotelmanager.db
```

预订延住（仅延后退房日期）：

```bash
python -m hotelmanager booking extend --id 1 --end 2025-12-27 --db hotelmanager.db
```

## 5. 统计（stats）

收入统计（按预订房价快照 * 房晚，仅统计 reserved）：

```bash
python -m hotelmanager stats revenue --start 2025-12-20 --end 2025-12-30 --db hotelmanager.db
```

## 6. 导出（export）

导出 CSV（默认输出到 stdout，可用 `--out` 写文件）：

```bash
python -m hotelmanager export rooms --db hotelmanager.db --out rooms.csv
python -m hotelmanager export guests --db hotelmanager.db --out guests.csv
python -m hotelmanager export bookings --db hotelmanager.db --out bookings.csv
```
