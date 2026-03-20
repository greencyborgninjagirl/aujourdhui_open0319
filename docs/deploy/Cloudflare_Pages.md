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

常见于 **POST 仍发到 `*.pages.dev`**：Pages 只托管静态文件，对 `/api/draw` 的 POST 往往返回 **405**。根因是生产包里 **`VITE_API_BASE` 未打进构建**（`BASE_URL` 为空时会用 `window.location.origin`，即 Cloudflare 域名）。

仓库已在 `aujourdhui-frontend/vite.config.js` 里对 `import.meta.env.VITE_API_BASE` 做 **显式注入**（读取 Cloudflare 构建环境变量）。请确认：

1. Pages → **Settings** → **Environment variables** 中 **`VITE_API_BASE`** = `https://你的项目.vercel.app`（无末尾 `/`）。
2. 保存后 **重新部署**（必须重新跑 `npm run build:h5`）。

自检：浏览器 **开发者工具 → Network**，抽牌时 POST 的 **Request URL** 应为 `https://xxx.vercel.app/api/draw`，而不是 `https://xxx.pages.dev/api/draw`。
