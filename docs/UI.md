# Web UI 设计说明

本目录提供一套 **静态管理台**（可直接用浏览器打开 `web/index.html` 预览），用于展示 HotelManager 的世界级交互体验基线。

## 设计目标

- **可读性优先**：核心数据 3 秒内可识别，文本对比满足 WCAG AA。
- **情绪化体验**：柔光渐变 + 玻璃拟态 + 微动效，减少冰冷感。
- **结构化密度**：Bento Grid 将复杂信息拆为清晰区块。
- **单滚动原则**：页面只有一个主滚动条，避免嵌套滚动。

## 视觉系统

- **色彩**：深色基底 + 冷暖双主色（#7c9dff / #7ef1d6）
- **质感**：卡片使用 `backdrop-filter: blur` 与微边框
- **背景**：多层渐变 + 噪点纹理，避免“死黑”

## 交互与动效

- **入场礼仪**：区块采用 `fade-up` 交错入场
- **微交互**：按钮 hover 上浮、active 缩放
- **多巴胺反馈**：操作按钮触发 confetti + shimmer

## 数据联通（CLI → Web UI）

本 UI 仍保持“纯静态可打开”，但支持导入 CLI 导出的 **JSON 快照**，让页面从“样机”升级为“离线可视化面板”：

1. 导出快照：
   ```bash
   python -m hotelmanager export snapshot --db hotelmanager.db --out snapshot.json --pretty
   ```
2. 打开 `web/index.html`
3. 点击右上角“导入快照”或拖拽 `snapshot.json` 到导入区域

说明：
- 导入逻辑仅在浏览器本地解析文件，不会发起网络请求
- 目前前端校验 `schema_version=1`（不匹配会提示错误）

## 组件预览

- 运营概览（Hero + 今日概览）
- KPI 统计卡
- 收入趋势与房态总览
- 预订节拍与运营时间线
- 空状态插画 + 拖拽导入

## 本地预览

1. 双击打开 `web/index.html`
2. 若需调色或排版，修改 `web/assets/styles.css`
3. 交互逻辑在 `web/assets/app.js`
