# aujourd'hui 前端视觉规范（当前技术栈）

在 **HBuilderX + Uni-app Vue3** 下可直接运行，无额外依赖。视觉与文案原则见仓库 [`docs/product/aujourdhui_product_constitution_1.1.txt`](../docs/product/aujourdhui_product_constitution_1.1.txt)：极简、留白；色板与文字色**按画作主色**驱动（当前开屏示例：金棕渐变 + 对应文案色），后续将按画作提供模板。

---

## 原则

- **极简**：少装饰，少层级，信息清晰；画作区不用硬边框，用极淡阴影 `drop-shadow(0 2px 12px rgba(74,74,74,0.06))`，无闪粉/微光。
- **留白**：上下左右留足空间，不挤满屏。
- **色表**：背景为左深→右浅渐变、文字色均依据画作主色（当前为金棕系示例）。
- **法式极简**：标题可用衬线（Georgia/Calibri），字距略大，按钮克制的线框或浅底。

---

## 实现方式（本栈）

- **全局变量**：在 `App.vue` 的 `:root` 里定义 CSS 变量（`--aj-*`），各页面用 `var(--aj-*)` 引用。
- **配色**：`--aj-bg` 背景、`--aj-text` 主文、`--aj-text-soft` / `--aj-text-muted` 次要、`--aj-border` 边框、`--aj-accent` 强调。
- **留白**：`--aj-space-xs/sm/md/lg/xl`、`--aj-max-width` 控制内容宽度与间距。
- **字体**：`--aj-font` 无衬线、`--aj-serif` 衬线（品牌/标题）。

---

## 已应用页面

- **index**：开屏画作 + 画作信息 + 文案「tell me about today」+ 进入按钮，居中、留白、衬线标题。
- **draw**：同套变量，标题衬线，免责小字 muted。
- **result**：牌背/牌面用莫兰迪灰阶渐变，叙事区用 `--aj-bg-paper` 与细边框。

后续新页面或组件只需复用 `var(--aj-*)` 即可保持统一。
