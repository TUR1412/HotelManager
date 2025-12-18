# 数据库与迁移（SQLite）

本项目使用 SQLite 作为本地存储，并将“Schema 演进”作为一等公民处理：**旧的 db 文件应尽可能可升级**，而不是让用户删库重来。

## 1. 数据库文件与 WAL

- 默认数据库文件：`hotelmanager.db`（可通过 `--db` 指定）
- 当启用 WAL 模式时，SQLite 会在同目录生成：
  - `*.db-wal`
  - `*.db-shm`

这些文件属于正常现象，仓库已在 `.gitignore` 中忽略。

> 说明：本项目默认 **强制启用 WAL**（不做静默降级）。如果 WAL 无法启用，会给出可行动报错（通常是路径只读、文件系统不兼容或权限问题）。

## 2. Schema 版本（PRAGMA user_version）

SQLite 提供 `PRAGMA user_version` 用于记录用户自定义的 schema 版本号。

HotelManager 在 `init_db()` 中会：

1. 执行 `CREATE TABLE IF NOT EXISTS ...`，确保表存在
2. 执行幂等迁移（根据 `PRAGMA table_info` 判断缺失字段并补齐）
3. 写入当前 `user_version`

这样可以兼容：

- 老版本 db 文件（字段不全）
- db 文件复制/迁移导致版本号不可信的情况

## 3. 当前迁移点（示例）

### 3.1 预订价格快照（bookings.price_per_night_cents）

为避免“房价调整影响历史预订金额展示”，创建预订时会把当时房价写入 bookings。

对旧数据库：

- 若缺少 `price_per_night_cents`，会通过 `ALTER TABLE` 补齐
- 并尝试用当前房价进行回填（历史真实房价无法还原，但至少避免 0 造成误导）

### 3.2 邮箱不区分大小写唯一（lower(email) unique index）

应用层会把邮箱归一化为小写，但为了抵御并发/外部写入带来的脏数据，数据库层也会加一层约束：

- `CREATE UNIQUE INDEX ... ON guests (lower(email))`

若你的旧数据库存在 `Alice@Example.com` 和 `alice@example.com` 同时存在的情况，迁移会失败并提示你先清理重复数据。

## 4. 常见问题（Troubleshooting）

### 4.1 提示无法启用 WAL

建议：

- 把 `--db` 指向本地可写目录（避免网络盘/只读目录）
- 检查是否有权限写入 db 文件所在目录

### 4.2 提示 email 存在大小写重复

建议：

- 备份 db
- 删除重复邮箱记录（保留一条）
- 再运行任意命令（`init/doctor/...`），触发迁移

