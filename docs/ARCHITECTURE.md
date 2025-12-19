# 架构与设计说明（HotelManager）

本文档解释本项目的核心设计取舍，便于后续迭代（例如：入住/退房、账单、房态看板、REST API 等）。

## 1. 分层结构

项目采用轻量分层（不引入框架）：

- **CLI 层**：`src/hotelmanager/cli.py`
  - 负责解析参数、组织输出、将用户输入转为领域可用的数据类型（如日期/金额）。
  - 不直接写 SQL，不直接拼接数据库逻辑。
- **Web UI（静态预览）**：`web/`
  - 以静态页面形式提供管理台体验基线，强调视觉与交互规范。
  - 不依赖后端服务，便于设计评审与演进。
- **应用服务层**：`src/hotelmanager/services.py`
  - 承载业务规则：校验、预订冲突检测、状态约束等。
  - 对外提供“可组合”的方法（例如 `create_booking`、`set_room_status`、`list_booking_views_filtered`）。
- **仓储层**：`src/hotelmanager/repositories.py`
  - 封装 SQL 与对象映射（Row -> dataclass）。
  - 不包含业务规则（例如：不在仓储层判断房间状态）。
- **DB/Schema 层**：`src/hotelmanager/db.py`
  - SQLite 连接、Schema 初始化（`init_db`）。

## 2. 数据模型

### Rooms

- `number`：房间号（唯一）
- `room_type`：房型（示例：single/double/suite）
- `capacity`：容量（正整数）
- `price_per_night_cents`：以“分”为单位的整数金额，避免浮点误差
- `status`：`active | maintenance`

扩展能力：

- “可用房间查询”通过 `NOT EXISTS + 区间重叠判断` 排除冲突预订（见 `RoomRepository.list_available`）

### Guests

- `email`：住客邮箱（逻辑上按不区分大小写处理；应用层会归一化为小写）

### Bookings

- `start_date` 与 `end_date`：日期区间采用 **闭开区间** `[start, end)`（start 含、end 不含）
  - 这样可以自然表达“连续入住”（例如 12/20-12/22 与 12/22-12/23 不冲突）
- `status`：`reserved | cancelled`
- `price_per_night_cents`：**预订价格快照**
  - 创建预订时把“当时的房价”写入 bookings，避免后续 `room price` 调整导致历史预订金额变化。

## 3. 预订冲突检测

冲突定义（同一房间，且仅对 `reserved` 生效）：

> 两个区间重叠：`NOT (existing_end <= new_start OR existing_start >= new_end)`

对应实现位于 `BookingRepository.has_conflict`。

## 4. 错误与异常策略

- 业务可预期错误统一继承自 `HotelManagerError`（见 `src/hotelmanager/errors.py`）
- CLI 捕获后输出“人话”错误信息，并在 `--verbose` 时打印堆栈

## 5. 可测试性

- 核心逻辑由 `HotelManagerService` 提供，可在 `:memory:` SQLite 下快速测试
- 单元测试集中在 `tests/`

## 6. Web UI（静态管理台）

UI 位于 `web/`，为静态预览页面，不依赖后端服务。  
设计原则与组件说明见：`docs/UI.md`。

本地运行：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m compileall -q src tests
```

## 7. 数据库迁移（Schema Migration）

为避免“用户已有数据库文件无法升级”的问题，`init_db` 会：

- 先执行 `CREATE TABLE IF NOT EXISTS ...` 保障结构存在
- 再做“幂等迁移”（根据 `PRAGMA table_info` 判断缺失字段并补齐）
- 最后写入 `PRAGMA user_version` 用于版本追踪

目前已包含：

- `bookings.price_per_night_cents` 字段补齐与回填
- `guests.email` 的不区分大小写唯一索引（`lower(email)`）
