# Vercel 部署问题清单

基于当前项目结构整理。**当前约定（全栈）**：`vercel.json` 在 **仓库根目录**；**Root Directory 留空**（不要用仅前端的子目录）。根目录配置会安装 Python 依赖、构建 `aujourdhui-frontend`，并由 **`api/draw.py`** 提供 **`POST /api/draw`**。若仍使用「仅前端子目录」旧配置，勿与根目录 `cd aujourdhui-frontend` 混用。

---

## 〇、依赖与构建脚本（Node / uni-app 版本）

### Python：externally-managed-environment（PEP 668）

Vercel 构建机上的 Python 由 **uv** 管理，直接 `pip install` 可能报错。根目录 **`vercel.json`** 的 `installCommand` 已使用：

`python -m pip install -r requirements.txt --break-system-packages`

仅在**构建容器**内使用，不影响你本机 Python。

### Uni-app / Node

- **旧版 `@dcloudio/*`（如 2024-07 的 `3.0.0-40203…`）**：与当前 Vercel 常用 Node、Vite 5.4 等组合易出现 peer 冲突或解析失败；已对齐到 npm 上较新的 **`3.0.0-alpha-5000420260319001`** 系列，并将 **Vite 固定为 `5.2.8`**（与官方 `vite-plugin-uni` peer 一致）。
- **构建命令**：应使用 **`uni build`**（由 `@dcloudio/vite-plugin-uni` 提供 `uni` 命令），而不是裸跑 `vite build`；否则易缺少 `UNI_PLATFORM` / 输入目录等环境。
- **无 `src/` 目录的旧结构**：官方 CLI 默认 `UNI_INPUT_DIR=src`。本项目页面在根目录，脚本中已设置 **`UNI_INPUT_DIR=.`**。
- **`unplugin-auto-import`**：`uni-cli-shared` 会从项目根 `require('unplugin-auto-import/vite')`，需在 **`devDependencies` 中显式声明**，否则构建阶段报 `MODULE_NOT_FOUND`（依赖嵌套在子包时 npm 未必提升到根目录）。

---

## 一、核心问题：工作目录错误（最可能）

### 现象
- 报错：`sh: line 1: uni: command not found`
- 原因：`uni` 来自 `node_modules/.bin/`，只有执行 `npm install` 后才会存在

### 根因
- **项目根目录**（仓库根）下**没有** `package.json`，`package.json` 在 `aujourdhui-frontend/` 里。
- 若 Vercel **未**设置 Root Directory：在根目录执行安装会失败；若 **已**把 Root Directory 设为 `aujourdhui-frontend`，又在 `installCommand` 里写 **`cd aujourdhui-frontend`**，会报 **`No such file or directory`**（当前目录已经是子目录，不应再 `cd`）。
- 根目录执行 `npm run build:h5` 会失败（没有该脚本），且 `uni` 不在 PATH 中。

### 解决方向（当前仓库：全栈）
1. **Root Directory**：**留空**（仓库根）。
2. **`vercel.json`**：在根目录，含 `pip install -r requirements.txt`、`cd aujourdhui-frontend && npm run build:h5`、`outputDirectory` 指向 `aujourdhui-frontend/dist/build/h5`。
3. **Python Serverless**：`api/draw.py` 导出与 `backend_api.py` 相同的 FastAPI `app`（ASGI）。

---

## 二、可能缺失的依赖

### 1. `@dcloudio/vite-plugin-uni`
- `vite.config.js` 中有：`import uni from '@dcloudio/vite-plugin-uni'`
- `package.json` 中**没有**显式声明该包
- 可能作为 `@dcloudio/uni-app` 的依赖被间接安装，也可能缺失
- 若构建报错找不到该模块，需在 `devDependencies` 中显式添加

### 2. `sass` 与 `vite` 版本
- 使用 `sass: ^1.77.0`，新版可能有兼容性问题
- 未显式声明 `vite`，由 uni-app 相关包带入，版本不可控

---

## 三、`uni` 命令来源

### 当前脚本
```json
"build:h5": "uni build -p h5"
```

### 说明
- `uni` 通常由 `@dcloudio/uni-app` 或 `@dcloudio/uni-app-cli` 提供
- 使用 `"latest"` 后，包结构可能变化，CLI 名称或路径可能不同
- 备选：改为 `npx uni build -p h5` 或 `npx vite build`（若 uni-app 支持）

---

## 四、构建输出路径

### 当前配置
```json
"outputDirectory": "dist/build/h5"
```

### 说明
- uni-app H5 常见输出：`dist/build/h5` 或 `unpackage/dist/build/h5`
- 若 Root Directory 设为 `aujourdhui-frontend`，则 `dist/build/h5` 表示 `aujourdhui-frontend/dist/build/h5`
- 若 Root Directory 为项目根，则需改为 `aujourdhui-frontend/dist/build/h5` 或 `aujourdhui-frontend/unpackage/dist/build/h5`

---

## 五、`.gitignore` 与构建产物

### 当前
- `aujourdhui-frontend/dist/` 和 `aujourdhui-frontend/unpackage/dist/` 已忽略
- 构建在 Vercel 上重新执行，本地是否提交这些目录影响不大

---

## 六、其他潜在问题

### 1. Node 版本
- 当前：`"node": "24.x"`
- Node 24 较新，部分依赖可能不兼容，必要时可尝试 `20.x` 或 `22.x`

### 2. `config.js` 中的 `VITE_API_BASE`
- 构建时需在 Vercel 环境变量中设置
- 未设置时使用默认 `http://127.0.0.1:8000`，部署后 API 请求会失败

### 3. 静态资源路径
- 牌背图：`/static/visual/back.jpg`
- 需确认 `static` 目录在构建产物中正确输出

---

## 七、建议修复顺序

| 优先级 | 问题 | 建议操作 |
|--------|------|----------|
| 1 | 工作目录错误 | 在 Vercel 中设置 Root Directory = `aujourdhui-frontend`，或修改 vercel.json 中所有命令与 outputDirectory |
| 2 | `uni` 命令找不到 | 确认 Root Directory 正确后，若仍报错，尝试 `npx uni build -p h5` 或恢复固定版本号 |
| 3 | 输出路径 | 若部署成功但页面 404，检查 outputDirectory 是否与实际输出一致 |
| 4 | 依赖缺失 | 若出现 `Cannot find module '@dcloudio/vite-plugin-uni'`，在 package.json 中显式添加 |

---

## 八、项目结构速览

```
aujourdhui/                    ← 项目根（Vercel Root Directory 留空）
├── vercel.json                 ← 根目录：pip + 前端 build + outputDirectory
├── backend_api.py              ← FastAPI（本地 uvicorn）
├── api/
│   └── draw.py                 ← Vercel Python Serverless（ASGI，POST /api/draw）
├── app.py
├── draw_logic.py
├── docs/
└── aujourdhui-frontend/      ← uni-app 前端
    ├── package.json
    └── dist/build/h5/          ← 构建输出
```
