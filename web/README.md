# Web UI 预览说明

本目录提供 HotelManager 的 **静态管理台 UI**，用于展示视觉与交互基线。

同时支持导入 CLI 导出的 **JSON 数据快照**（本地解析，不联网），让 UI 可以展示真实数据。

## 快速预览

1. 直接打开 `web/index.html`
2. CSS：`web/assets/styles.css`
3. JS：`web/assets/app.js`

## 导入数据快照（推荐）

1. 生成快照：

```bash
python -m hotelmanager export snapshot --db hotelmanager.db --out snapshot.json --pretty
```

2. 打开 `web/index.html`
3. 点击右上角“导入快照”，或拖拽 `snapshot.json` 到页面导入区域

> 前端会校验 `schema_version`；目前兼容 `schema_version=1`。

## 设计关键词

- Bento Grid（信息模块化）
- 玻璃拟态（层级与空间感）
- 动效编排（交错入场 + 微交互）
- 高可读性（WCAG AA）
