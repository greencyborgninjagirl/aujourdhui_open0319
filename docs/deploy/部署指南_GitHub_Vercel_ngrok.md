# aujourd'hui 公网内测部署指南

## 架构说明

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   GitHub    │ ──► │   Vercel    │     │  ngrok (本机)    │
│   代码仓库   │     │  前端 H5    │ ──► │  后端 API 隧道   │
└─────────────┘     └─────────────┘     └─────────────────┘
                           │                      │
                           │  安全链接             │
                           ▼                      ▼
                    https://xxx.vercel.app   https://xxx.ngrok.io
```

- **Vercel**：托管前端静态页面（从 GitHub 自动构建部署）
- **ngrok**：将本机 FastAPI 后端暴露到公网（生成 HTTPS 链接）
- **安全链接**：Vercel 与 ngrok 均提供 HTTPS，适合内测分享

---

## 一、前置准备

1. **GitHub 账号**，代码已推送到仓库
2. **Vercel 账号**（可用 GitHub 登录）：https://vercel.com
3. **ngrok 账号**（免费版可用）：https://ngrok.com
4. **本机环境**：Python 3.x、Node.js（用于运行后端）

---

## 二、部署步骤

### Step 1：连接 GitHub 与 Vercel

1. 登录 [Vercel](https://vercel.com) → **Add New** → **Project**
2. 选择你的 GitHub 仓库（aujourd'hui 所在仓库）
3. **不要**点 Deploy，先配置环境变量

### Step 2：配置 Vercel 环境变量

在 Vercel 项目 **Settings** → **Environment Variables** 中添加：

| Name | Value | 说明 |
|------|-------|------|
| `VITE_API_BASE` | `https://你的ngrok域名` | 见 Step 4，先留空亦可 |

- 先保存，后续启动 ngrok 后再填并触发重新部署

### Step 3：部署前端

1. 确认 Vercel **Root Directory** 为 `aujourdhui-frontend`，且该目录下有 `vercel.json`（或仅用控制台默认构建）
2. 点击 **Deploy**
3. 部署完成后得到链接，如：`https://aujourdhui-xxx.vercel.app`

### Step 4：启动后端 + ngrok

1. **安装 ngrok**（若未安装）：
   ```bash
   # macOS (Homebrew)
   brew install ngrok
   ```

2. **启动 API**：
   ```bash
   uvicorn api:app --host 127.0.0.1 --port 8000
   ```
   或双击 `run-api.command`

3. **启动 ngrok 隧道**：
   ```bash
   ngrok http 8000
   ```
   - 终端会显示公网地址，如：`https://abc123.ngrok-free.app`
   - 复制该 **HTTPS** 地址（不要带末尾斜杠）

4. **回填 Vercel 环境变量**：
   - 将 `VITE_API_BASE` 设为 `https://abc123.ngrok-free.app`
   - 在 Vercel 项目 **Deployments** → 最新部署 → **Redeploy** 触发重新构建

### Step 5：获取内测链接

- **内测链接**：`https://你的项目.vercel.app`（即 Vercel 部署后的 URL）
- 分享给测试者，手机浏览器打开即可使用

---

## 三、ngrok 免费版说明

| 项目 | 说明 |
|------|------|
| URL 变化 | 每次重启 ngrok 会生成新域名，需更新 Vercel 的 `VITE_API_BASE` 并 Redeploy |
| 固定域名 | ngrok 付费版可绑定固定子域名，一次配置长期有效 |
| 本机运行 | 电脑需保持开机且 ngrok 与 API 同时运行，测试者才能正常抽牌 |

---

## 四、安全检查

- Vercel 与 ngrok 均提供 **HTTPS**，传输加密
- 未在代码中硬编码 API Key / Secret
- CORS 已允许前端域名访问 API（内测可接受）
- 内测结束后可关闭 ngrok 与 API 进程，停止对外暴露

---

## 五、常见问题

**Q：抽牌失败 / 请求超时？**  
- 确认本机 API 已启动（`uvicorn api:app --host 127.0.0.1 --port 8000`）
- 确认 ngrok 隧道已启动且未断开
- 确认 Vercel 的 `VITE_API_BASE` 与当前 ngrok 地址一致

**Q：ngrok 重启后链接变了？**  
- 免费版每次重启会变，需更新 Vercel 环境变量并 Redeploy

**Q：牌面图加载不出来？**  
- 牌面来自 Wikipedia Commons，大陆部分地区可能较慢或需代理

**Q：Vercel 构建失败 / 找不到输出目录？**  
- uni-app H5 输出可能在 `dist/build/h5` 或 `unpackage/dist/build/h5`，若报错可尝试修改 `vercel.json` 的 `outputDirectory`

---

## 六、相关文档

- [Vercel 部署问题清单](./Vercel部署问题清单.md)（`uni: command not found`、Root Directory 等）
- [内测说明](../internal/内测说明.md)（局域网、安全注意）
- 仓库总览：[README.md](../../README.md)
