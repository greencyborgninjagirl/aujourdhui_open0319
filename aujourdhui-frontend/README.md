# aujourdhui · 今日镜像 — 前端

**仓库总览**（后端、文档索引、Vercel）：上一级目录 [`README.md`](../README.md) · [`docs/README.md`](../docs/README.md)。

**重要**：请用 HBuilderX **只打开本文件夹 `aujourdhui-frontend`**（不要打开仓库根目录），再「运行 → 运行到浏览器」，否则会白屏。详见本目录下 `CHECKLIST.md`。

项目标识为 **aujourdhui**（避免编程中单引号冲突），页面上仍显示为 aujourd'hui。**主端为 Uni-app（HBuilderX 开发）**；Streamlit 版已弃用，流程与文案遵循产品宪章。

## 流程

1. **开屏** `pages/index` — 名画 + 名画信息 + 引导语「tell me about today」+ 进入按钮 → 点击进入抽牌页
2. **抽牌** `pages/draw` — 引导语 + 牌背展示 +「开启镜像」→ 请求 `POST /api/draw` → 存结果并跳转解读页
3. **解读** `pages/result` — 牌背 → 点击翻开 → 牌面 + 牌意解读 + 名画意境分享

## 本地联调

1. 后端：在项目**上一级**目录启动 `uvicorn backend_api:app --reload`（即 aujourdhui 项目根目录）
2. 前端：在 `config.js` 中 `BASE_URL` 已设为 `http://127.0.0.1:8000`，开发期间保持本机；上线/真机测试时再改 IP
3. 用 HBuilderX 打开本目录，运行到浏览器（H5）：开屏点进入 → 抽牌页点「开启镜像」→ 解读页查看结果

## 若你在别处已建了 aujourdhui-frontend

把本目录下这些同步过去即可：

- `config.js`、`utils/request.js`、`api/draw.js`
- `pages.json`、`manifest.json`、`App.vue`、`main.js`、`index.html`
- `pages/index/index.vue`、`pages/draw/draw.vue`、`pages/result/result.vue`

注意：若你已有 `pages` 或 `App.vue`，请按需合并路由与全局样式（莫兰迪色、留白、`.btn-mirror` 等）。

**项目文件夹名**：若希望根目录也统一为 aujourdhui，可在访达中把项目文件夹从 `aujourd'hui` 改名为 `aujourdhui`，并更新终端/HBuilderX 中的路径。
