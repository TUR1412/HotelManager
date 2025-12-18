# FAQ（常见问题）

## 1) 提示“参数错误：日期格式错误”

HotelManager 的日期统一使用 `YYYY-MM-DD`（例如 `2025-12-20`）。

示例：

```bash
python -m hotelmanager booking create --room 101 --guest-email "alice@example.com" --start 2025-12-20 --end 2025-12-22 --db hotelmanager.db
```

## 2) 提示“预订冲突”

预订区间采用闭开区间 `[start, end)`：

- `start` 含（入住日）
- `end` 不含（退房日）

所以连续入住不会冲突：

- `2025-12-20~2025-12-22`
- `2025-12-22~2025-12-23`

如果你想看某个时间段哪些预订占用房间，可以用日期区间过滤：

```bash
python -m hotelmanager booking list --from 2025-12-21 --to 2025-12-23 --db hotelmanager.db
```

## 3) 提示“数据库被占用（locked）”

这是 SQLite 的常见提示：某个进程正在占用同一个 db 文件写锁。

建议：

- 关闭其他正在使用同一个 `--db` 的程序/终端
- 等待 1~2 秒后重试
- 把 db 放到本地磁盘目录（避免网络盘）

你也可以运行：

```bash
python -m hotelmanager doctor --db hotelmanager.db
```

## 4) 提示“无法启用 SQLite WAL 模式”

本项目默认强制启用 WAL（不静默降级），如果失败通常是：

- db 所在目录不可写（权限/只读）
- 文件系统不兼容 WAL（常见于某些网络盘）

建议：把 `--db` 指向本地可写目录后重试。

更多解释见：`docs/DB.md`

## 5) 提示“邮箱存在大小写重复，无法升级”

这是旧 db 里出现了：

- `Alice@Example.com`
- `alice@example.com`

同时存在的情况。

为保证一致性，HotelManager 会在迁移时建立 `lower(email)` 唯一索引，从而拒绝这类脏数据。

建议：

1. 备份 db
2. 删除重复邮箱记录（保留一条）
3. 重新运行任意命令触发迁移（如 `doctor`）

