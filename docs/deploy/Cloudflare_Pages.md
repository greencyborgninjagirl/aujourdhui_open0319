# Cloudflare Pages 部署说明

## 产物路径（避免重复 `aujourdhui-frontend/`）

若 Dashboard 里 **Root directory（构建根目录）** 已设为 **`aujourdhui-frontend`**，则 **Build output directory** 只能填：

```text
dist/build/h5
```

不要填 `aujourdhui-frontend/dist/build/h5`，否则会变成 `aujourdhui-frontend/aujourdhui-frontend/...` 而报错。

若 **Root directory 留空（仓库根）**，则输出目录为：

```text
aujourdhui-frontend/dist/build/h5
```

并与仓库根目录的 `wrangler.toml` 中 `pages_build_output_dir` 一致。

## 构建命令示例

**根目录为 `aujourdhui-frontend` 时：**

```bash
npm ci --legacy-peer-deps && npm run build:h5
```

**根目录为仓库根时：**

```bash
cd aujourdhui-frontend && npm ci --legacy-peer-deps && npm run build:h5
```

## wrangler.json

若曾添加过 **无效** 的 `wrangler.json`，请删除或改为官方文档格式；本仓库以根目录 **`wrangler.toml`** 为准（Pages 的 `pages_build_output_dir`）。

## 构建日志里的「推广语」

若出现「欢迎将 web 站点部署到 uniCloud 前端网页托管…」等字样，来自 **uni-app / DCloud 构建工具** 的固定输出，**不是** Cloudflare 广告。

## 抽牌请求失败 **405**（Method Not Allowed）

常见于 **POST 打到 `*.pages.dev` 的静态层**：Pages 对未配置路由的 `/api/draw` 做 POST 往往返回 **405**。根因多为 **`VITE_API_BASE` 未打进构建**，前端仍用 `window.location.origin` 请求同域 `/api/draw`。

### 推荐：`functions/api/draw.js`（反向代理）

仓库在 **`aujourdhui-frontend/functions/api/draw.js`** 中把 **`/api/draw`** 转发到 Vercel 上的 FastAPI（默认 `https://aujourdhui-open0319.vercel.app`）。这样 **不依赖** 构建时注入 `VITE_API_BASE`，同域 `POST /api/draw` 会先进入 Pages Function，再转发到上游。

可选环境变量 **`API_ORIGIN`**（无末尾 `/`）：Pages → Settings → Environment variables，用于更换 Vercel 域名。

### 备选：仅构建时注入 API

`aujourdhui-frontend/vite.config.js` 会显式注入 **`VITE_API_BASE`**。若采用此方式，请在 Pages 构建变量中设置 `VITE_API_BASE` 并重新部署。

自检：Network 里 POST 的 URL 为 **`*.pages.dev/api/draw`** 且 **状态 200** 即表示 Function 已生效；若仍为 **405**，确认 **`functions/` 与 `dist/build/h5` 同属 Pages 根目录**（本仓库为 `aujourdhui-frontend/`）并已重新部署。
