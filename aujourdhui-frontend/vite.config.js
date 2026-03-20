import { defineConfig, loadEnv } from 'vite';
import uniModule from '@dcloudio/vite-plugin-uni';

/** CJS 默认导出在部分 Node/Vite 组合下需解包 */
const uni = typeof uniModule === 'function' ? uniModule : uniModule.default;

export default defineConfig(({ mode }) => {
  // 合并 .env 与 CI（如 Cloudflare Pages）在构建时注入的 process.env
  const env = loadEnv(mode, process.cwd(), '');
  const apiBase = String(
    process.env.VITE_API_BASE ?? env.VITE_API_BASE ?? ''
  ).replace(/\/$/, '');

  return {
    plugins: [uni()],
    define: {
      // uni-app 生产构建有时未把 CI 环境变量打进包，显式注入避免仍请求 pages.dev 导致 POST 405
      'import.meta.env.VITE_API_BASE': JSON.stringify(apiBase),
    },
    build: {
      minify: true,
    },
  };
});
