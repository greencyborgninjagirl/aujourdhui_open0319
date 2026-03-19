<script setup>
// 全局逻辑可在此扩展
</script>

<template>
  <view class="app-wrap" id="app-wrap">
    <!-- Uni-app 在此注入当前页面 -->
  </view>
</template>

<style>
/* ========== aujourd'hui 视觉规范：极简 · 留白 · 莫兰迪 ==========
 * 设计原则：低饱和度、留白感、法式极简，照见当下。
 * 技术栈：Uni-app Vue3，仅用 CSS 变量 + 类，无额外依赖。
 */
:root {
  /* 莫兰迪色系（内页 / 第三页） */
  --aj-bg: #f5f0ed;
  --aj-bg-paper: #faf9f7;
  --aj-text: #5a5652;
  --aj-text-soft: #7a7570;
  --aj-text-muted: #9c9892;
  --aj-border: rgba(90, 86, 82, 0.12);
  --aj-accent: #8b8379;
  --aj-accent-soft: rgba(139, 131, 121, 0.25);
  /* 留白与排版 */
  --aj-space-xs: 0.375rem;
  --aj-space-sm: 0.75rem;
  --aj-space-md: 1rem;
  --aj-space-lg: 1.5rem;
  --aj-space-xl: 2.5rem;
  --aj-max-width: 420px;
  --aj-radius: 6px;
  --aj-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  --aj-serif: Georgia, "Times New Roman", serif;
  font-size: 15px;
}

page {
  width: 100%;
  min-height: 100vh;
  color: var(--aj-text);
  font-family: var(--aj-font);
  background: var(--aj-bg);
  box-sizing: border-box;
}
.app-wrap {
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
}
#app-wrap { display: block; }

/* 全局复用 */
.mirror-text { color: var(--aj-text); line-height: 1.75; }
.subtitle {
  font-weight: 300;
  letter-spacing: 0.2em;
  color: var(--aj-text-soft);
  font-size: 0.75rem;
}
.disclaimer {
  margin-top: var(--aj-space-lg);
  padding-top: var(--aj-space-md);
  font-size: 0.7rem;
  color: var(--aj-text-muted);
  border-top: 1px solid var(--aj-border);
}
.card-name {
  font-weight: 300;
  letter-spacing: 0.12em;
  margin-bottom: var(--aj-space-sm);
  color: var(--aj-text);
}
.btn-mirror {
  background: var(--aj-accent);
  border: none;
  color: var(--aj-bg-paper);
  padding: 0.65rem 1.5rem;
  border-radius: var(--aj-radius);
  letter-spacing: 0.12em;
  font-weight: 400;
  font-size: 0.9rem;
}
.btn-mirror:active { opacity: 0.88; }
.btn-mirror[disabled] { opacity: 0.6; }
</style>
