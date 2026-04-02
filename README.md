# aujourdhui · 今日镜像

Web（H5）与微信小程序方向的每日一牌产品：法式极简视觉 + 心理化叙事（非传统占卜）。对外名称可为 **aujourd'hui**，仓库与包名使用 **aujourdhui** 以避免路径中的撇号问题。

---

## 仓库结构

```
aujourdhui/
├── README.md                 ← 本文件
├── requirements.txt          ← Python 依赖（FastAPI / 无 Streamlit）
├── backend_api.py            ← FastAPI 应用（本地 uvicorn / 供 api/ 引用）
├── api/draw.py               ← Vercel Python Serverless 入口（ASGI）
├── app.py                    ← 牌库、叙事生成、Commons 牌图 URL（无 UI）
├── draw_logic.py             ← 抽牌池、名画匹配
├── artwork_minor.py          ← 小阿卡纳名画数据
├── docs/                     ← 产品与运维文档（详见 docs/README.md）
├── run-api.command           ← 本机启动 API（127.0.0.1）
├── run-api-lan.command       ← 局域网启动 API（0.0.0.0）
└── aujourdhui-frontend/      ← uni-app + Vue3 + Vite；含 vercel.json（部署见下文）
```

---

## 快速开始

### 1. 后端

```bash
cd /path/to/aujourdhui
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend_api:app --reload --host 127.0.0.1 --port 8000
```

- 接口文档：<http://127.0.0.1:8000/docs>
- 牌义来源：`docs/content/logic_mapping_2.md`（由 `app.load_cards_from_logic_mapping()` 读取）

### 2. 前端（H5）

```bash
cd aujourdhui-frontend
npm install
npm run dev:h5
```

- 用 **HBuilderX** 开发时，请**只打开** `aujourdhui-frontend` 文件夹，避免白屏（详见该目录下 `CHECKLIST.md`）。
- API 地址：`config.js` / 环境变量 **`VITE_API_BASE`**（生产构建前必须指向真实后端）。

### 3. 局域网给手机测

见 [`docs/internal/内测说明.md`](docs/internal/内测说明.md)（`run-api-lan.command`、`.env.development.local` 等）。

---

## 文档在哪

| 需求 | 文档 |
|------|------|
| 产品原则与文案规范 | [`docs/product/aujourdhui_product_constitution_1.1.txt`](docs/product/aujourdhui_product_constitution_1.1.txt) |
| 抽牌交互原则 | [`docs/product/practice_workflow.md`](docs/product/practice_workflow.md) |
| 全部牌义（编辑内容主战场） | [`docs/content/logic_mapping_2.md`](docs/content/logic_mapping_2.md) |
| Vercel + ngrok 公网短测 | [`docs/deploy/部署指南_GitHub_Vercel_ngrok.md`](docs/deploy/部署指南_GitHub_Vercel_ngrok.md) |
| Vercel 构建报错排查 | [`docs/deploy/Vercel部署问题清单.md`](docs/deploy/Vercel部署问题清单.md) |
| 完整文档索引 | [`docs/README.md`](docs/README.md) |
| 变更记录 | 根目录 [`CHANGELOG.md`](CHANGELOG.md) |
| 分支与版本约定 | [`docs/VERSIONING.md`](docs/VERSIONING.md) |

---

## Vercel 部署要点（前端静态 + Python Serverless 同项目）

- **Root Directory**：留空，使用 **Git 仓库根目录**（与 `vercel.json`、`api/`、`aujourdhui-frontend/` 同级）。**不要**再填 `aujourdhui-frontend`（旧配置仅前端时用过）。
- 根目录 **`vercel.json`** 会：`pip install -r requirements.txt` → 构建 H5 → 输出 `aujourdhui-frontend/dist/build/h5`；**`api/draw.py`** 提供 **`POST /api/draw`**（FastAPI ASGI，与本地 `backend_api.py` 同源）。
- **前端请求地址**：生产构建默认 **`VITE_API_BASE` 未设置时走相对路径**（与页面同域，见 `aujourdhui-frontend/config.js`）。若仍要连外置后端（ngrok 等），再在 Vercel 设置 **`VITE_API_BASE`**。
- **Node**：`aujourdhui-frontend/package.json` 中 `engines.node` 为 **`20.x`**。
- **注意**：Serverless 有冷启动与执行时长限制；名画请求若较慢，偶发超时需再调（或后续换常驻后端）。详见 [`docs/deploy/Vercel部署问题清单.md`](docs/deploy/Vercel部署问题清单.md)。

---

## 技术栈摘要

- **后端**：Python 3、FastAPI、Uvicorn、`requests`
- **前端**：uni-app 3、Vue 3、Vite、Sass
- **已移除**：Streamlit（历史 UI 已删除，不再安装）

---

## 许可与资源说明

塔罗牌面图来自 **Wikipedia Commons**（1909 RWS）；名画匹配使用公开接口（如 Met Museum）。大陆网络环境下外链可能较慢，见内测说明。
