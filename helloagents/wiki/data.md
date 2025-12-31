# 数据模型（SQLite）

## rooms
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK | 自增主键 |
| number | TEXT | UNIQUE, NOT NULL | 房间号 |
| room_type | TEXT | NOT NULL | 房型 |
| capacity | INTEGER | NOT NULL, CHECK>0 | 可住人数 |
| price_per_night_cents | INTEGER | NOT NULL, CHECK>=0 | 每晚价格（分） |
| status | TEXT | NOT NULL | `active` / `maintenance` |

## guests
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK | 自增主键 |
| full_name | TEXT | NOT NULL | 姓名 |
| email | TEXT | UNIQUE, NOT NULL | 邮箱（逻辑上不区分大小写） |
| phone | TEXT | NULL | 电话 |
| created_at | TEXT | NOT NULL | ISO datetime（UTC, naive） |

## bookings
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK | 自增主键 |
| room_id | INTEGER | FK | rooms.id |
| guest_id | INTEGER | FK | guests.id |
| start_date | TEXT | NOT NULL | 入住日期（ISO date） |
| end_date | TEXT | NOT NULL | 退房日期（ISO date） |
| price_per_night_cents | INTEGER | NOT NULL | 下单时房价快照（分） |
| status | TEXT | NOT NULL | `reserved` / `cancelled` |
| created_at | TEXT | NOT NULL | ISO datetime（UTC, naive） |

