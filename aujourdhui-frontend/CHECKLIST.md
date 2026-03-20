# aujourdhui-frontend 完整性检查

## 一、必需文件（均已存在）

| 文件 | 说明 | 状态 |
|------|------|------|
| `index.html` | H5 入口 HTML，含 `#app` 与脚本引用 | ✅ |
| `main.js` | 导出 `createApp()`，使用 `createSSRApp(App)` | ✅ |
| `App.vue` | 根组件，含 `app-wrap` 根节点 | ✅ |
| `pages.json` | 三页：index、draw、result，首页为 index | ✅ |
| `manifest.json` | appid、h5 router（hash + base "/"） | ✅ |
| `package.json` | main、scripts dev:h5/build:h5、@dcloudio/uni-* 依赖 | ✅ |
| `config.js` | BASE_URL 配置 | ✅ |
| `utils/request.js` | 封装 uni.request，POST 带 application/json | ✅ |
| `api/draw.js` | drawCard() 调用 POST /api/draw | ✅ |
| `pages/index/index.vue` | 首页，双按钮（进入 / 抽一张牌） | ✅ |
| `pages/draw/draw.vue` | 抽牌页，开启镜像调 drawCard | ✅ |
| `pages/result/result.vue` | 结果页，从 storage 读 drawn_card | ✅ |

## 二、目录结构

- 页面与入口均在**前端根目录**（无 `src/` 包裹），符合 Uni-app 常见写法。
- 本目录包含 **`vite.config.js`**，与 `@dcloudio/vite-plugin-uni` 配合执行 `npm run build:h5`（即 `vite build`）。若仅用 HBuilderX 图形界面运行，仍以 IDE 提示为准。

## 三、可能导致 H5 白屏的原因

1. **用 HBuilderX 打开了错误的文件夹**  
   必须用 HBuilderX 打开 **`aujourdhui-frontend`** 这个文件夹（即包含本 CHECKLIST.md 的目录），不要打开上一级 `aujourd'hui`。  
   若打开的是上一级，IDE 会找不到 `pages.json` / `manifest.json`，不会按 Uni-app 编译，容易白屏。

2. **未安装依赖**  
   首次运行前在 `aujourdhui-frontend` 下执行：`npm install`。

3. **直接用浏览器打开 8080 端口**  
   若用命令行跑的是别的项目或端口，请确认当前访问的地址是本次 H5  dev 服务给出的地址（例如终端里打印的 localhost:xxxx）。

## 四、仓库根目录与前端关系

- 仓库根目录是**后端 + 文档**：`api.py`、`app.py`、`draw_logic.py`、`docs/`（产品宪章、牌义库、部署说明）等，与前端是否白屏无直接关系。
- 前端是**独立工程**，日常运行与编译在 `aujourdhui-frontend` 内完成；HBuilderX 只需打开并运行该文件夹。总览见仓库根目录 [`README.md`](../README.md)。
