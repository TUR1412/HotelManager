# Web UI 预览说明

本目录提供 HotelManager 的 **静态管理台 UI**，用于展示视觉与交互基线。

同时支持导入 CLI 导出的 **JSON 数据快照**（本地解析，不联网），让 UI 可以展示真实数据。

## 快速预览

1. 直接打开 `web/index.html`
2. CSS：`web/assets/styles.css`
3. JS：`web/assets/app.js`

## 交互速查

- 主题切换：右上角「主题」按钮，一键切换深色/浅色（会记忆偏好）。
- 日报导出：右上角「生成日报」，导出 Markdown 日报（本地生成，不联网）。
- 键盘快捷键：`I` 导入快照 / `G` 生成日报 / `T` 切换主题

## 导入数据快照（推荐）

1. 生成快照：

```bash
python -m hotelmanager export snapshot --db hotelmanager.db --out snapshot.json --pretty
```

2. 打开 `web/index.html`
3. 点击右上角“导入快照”，或拖拽 `snapshot.json` 到页面导入区域

> 前端会校验 `schema_version`；目前兼容 `schema_version=1`。
> 导入成功后会刷新 KPI、最新预订、入住率/到店/离店、房态总览与收入曲线。

## 设计关键词

- Bento Grid（信息模块化）
- 玻璃拟态（层级与空间感）
- 动效编排（交错入场 + 微交互）
- 高可读性（WCAG AA）
