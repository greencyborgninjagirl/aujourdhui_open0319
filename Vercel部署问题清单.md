# Vercel 部署问题清单

基于当前项目结构和报错 `uni: command not found`，整理可能的问题点。**先列不改**，供你决策后再修。

---

## 一、核心问题：工作目录错误（最可能）

### 现象
- 报错：`sh: line 1: uni: command not found`
- 原因：`uni` 来自 `node_modules/.bin/`，只有执行 `npm install` 后才会存在

### 根因
- **项目根目录**（`aujourd'hui/`）下**没有** `package.json`
- `package.json` 在 `aujourdhui-frontend/` 里
- 当前 `vercel.json` 的 `installCommand` 和 `buildCommand` 在**根目录**执行
- 根目录执行 `npm install` 会找不到 `package.json` 或安装到错误位置
- 根目录执行 `npm run build:h5` 会失败（没有该脚本），且 `uni` 不在 PATH 中

### 解决方向（二选一）
1. **在 Vercel 控制台**：Settings → General → **Root Directory** 设为 `aujourdhui-frontend`
2. **在 vercel.json**：所有命令加 `cd aujourdhui-frontend &&`，并把 `outputDirectory` 改为 `aujourdhui-frontend/dist/build/h5`

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
aujourd'hui/                    ← 项目根（无 package.json）
├── vercel.json                 ← 当前命令在此目录执行
├── api.py
├── app.py
├── ...
└── aujourdhui-frontend/        ← 前端代码
    ├── package.json            ← 含 build:h5 脚本
    ├── vite.config.js
    ├── node_modules/           ← npm install 应在此生成
    ├── dist/build/h5/          ← 构建输出（或 unpackage/dist/build/h5）
    └── ...
```
