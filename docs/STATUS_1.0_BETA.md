# aujourdhui · 项目状态快照

**版本阶段：1.0 正式 Beta**  
**Git 标签：** `v1.0.0-beta.1`（与 [`CHANGELOG.md`](../CHANGELOG.md) 中 [Beta 1.0] 条目对应）  
**归档用途**：记录截至 Beta 上线时的技术形态、部署方式与对外入口，便于日后回顾或交接。

---

## 产品一句话

每日一牌 Web（H5）：法式极简视觉 + 心理化叙事（非传统占卜）。对外名称可用 **aujourd'hui**，仓库与包名 **aujourdhui**。

---

## 当前线上形态（Beta）

| 角色 | 平台 | 说明 |
|------|------|------|
| **对外前端（主入口）** | Cloudflare Pages | 静态 H5；构建根目录 `aujourdhui-frontend`，输出 `dist/build/h5` |
| **API（FastAPI）** | Vercel Python Serverless | `POST /api/draw`；入口 `api/draw.py`，逻辑与本地 `backend_api.py` 同源 |
| **同域 API 转发** | Cloudflare Pages Functions | `aujourdhui-frontend/functions/api/draw.js` 将 `/api/draw` 代理至 Vercel，避免静态层对 POST 返回 405 |

**典型对外地址（Beta）**

- 前端：`https://aujourdhui-web.pages.dev`（`*.pages.dev` 为 Cloudflare 默认子域；可另绑自定义域，非必须）
- 后端（直连调试用）：`https://aujourdhui-open0319.vercel.app`（与 Function 内默认 `API_ORIGIN` 一致）

---

## 仓库技术栈

- **后端**：Python 3、FastAPI、Uvicorn；牌义与叙事见 `app.py`、`draw_logic.py`；主内容库 `docs/content/logic_mapping_2.md`
- **前端**：uni-app 3、Vue 3、Vite、Sass（目录 `aujourdhui-frontend/`）

---

## 与环境变量相关的约定

| 变量 | 作用位置 | 说明 |
|------|-----------|------|
| `VITE_API_BASE` | 前端构建（Vite） | `vite.config.js` 中会显式注入；可选。未设置时 H5 倾向走**同域** `/api/draw`（依赖 Pages Function 转发） |
| `API_ORIGIN` | Cloudflare Pages（Function） | 可选；覆盖代理目标，无末尾 `/`。不设则用 `functions/api/draw.js` 内默认 Vercel 地址 |

本地开发：前端默认连 `http://127.0.0.1:8000`（见 `config.js`）。

---

## 关键文件（部署相关）

| 路径 | 作用 |
|------|------|
| `backend_api.py` | 本地与逻辑参考用的 FastAPI 应用 |
| `api/draw.py` | Vercel Serverless 挂载的 ASGI |
| `vercel.json` | Vercel 全仓安装、构建 H5、输出目录与 `api/` |
| `aujourdhui-frontend/vite.config.js` | 生产构建注入 `VITE_API_BASE`（CI 友好） |
| `aujourdhui-frontend/functions/api/draw.js` | Cloudflare 上 `/api/draw` → Vercel |
| `docs/deploy/Cloudflare_Pages.md` | Pages 路径、405 与变量说明 |

---

## 已知限制（与 README 一致）

- Serverless 存在**冷启动**与**执行时长**上限；名画等外联较慢时偶发超时需后续优化或换常驻后端。
- 牌图等资源依赖外网；部分网络环境可能较慢。

---

## 文档索引

产品、内容、其它部署说明见 [`docs/README.md`](./README.md)；仓库总览见根目录 [`README.md`](../README.md)。

---

*本快照反映 Beta 上线时状态；若更换 Vercel 项目名、自定义域或下掉某一平台，请同步更新本文或另起版本快照。*
