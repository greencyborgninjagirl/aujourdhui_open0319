import { defineConfig } from 'vite';
import uniModule from '@dcloudio/vite-plugin-uni';

/** CJS 默认导出在部分 Node/Vite 组合下需解包 */
const uni = typeof uniModule === 'function' ? uniModule : uniModule.default;

export default defineConfig({
  plugins: [uni()],
  build: {
    minify: true,
  },
});
