<template>
  <view class="draw-page">
    <view class="btn-back" @click="onBack">
      <text class="btn-back-icon">‹</text>
    </view>
    <view class="page-head">
      <text class="page-head-title">aujourd'hui</text>
      <text class="page-head-subtitle">L'image de soi</text>
      <text class="page-head-caption">今日镜像 · 照见当下</text>
    </view>
    <view class="draw-inner">
      <view class="intro-main">{{ INTRO_BEFORE_DRAW }}</view>
      <view class="card-back-wrap">
        <view class="card-back">
          <image class="card-back-img" src="/static/visual/back.jpg" mode="aspectFit" />
        </view>
      </view>
      <button
        class="btn-mirror"
        :disabled="loading"
        @click="onOpenMirror"
      >
        {{ loading ? '抽牌中…' : '开启镜像' }}
      </button>
    </view>
    <view class="disclaimer-secondary">{{ DISCLAIMER }}</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { drawCard } from '../../api/draw.js'

const INTRO_BEFORE_DRAW = '这次观测将聚焦当下的时间线切片，聚焦于今天。\n——— 如同多棱镜的一个切面，塔罗牌会为你映照此刻心中光谱里一束可能的颜色。\n而你的察觉与选择，将始终是书写故事的那支笔。\n\n现在请你闭上眼睛，聚焦于"aujourd\'hui-今日"。\n我们来进行三个深呼吸。\n1-------2-------3-------'
const DISCLAIMER = '本服务仅供美学启发与心理平衡，不具临床诊断价值。你对自己的生活拥有最终决定权。'

const loading = ref(false)

function onBack() {
  uni.navigateBack()
}

async function onOpenMirror() {
  if (loading.value) return
  loading.value = true
  try {
    const res = await drawCard()
    uni.setStorageSync('drawn_card', res)
    uni.navigateTo({ url: '/pages/result/result' })
  } catch (e) {
    const msg = e && (e.message || e.errMsg) ? (e.message || e.errMsg) : '抽牌失败'
    uni.showToast({ title: msg, icon: 'none', duration: 2800 })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.btn-back {
  position: fixed;
  left: clamp(0.75rem, 3vw, 1.5rem);
  top: constant(safe-area-inset-top);
  top: env(safe-area-inset-top, 0);
  z-index: 10;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  cursor: pointer;
}
.btn-back:active {
  opacity: 0.7;
}
.btn-back-icon {
  font-size: 2rem;
  font-weight: 300;
  color: rgba(90, 86, 82, 0.85);
  line-height: 1;
}
.draw-page {
  width: 100%;
  min-height: 100vh;
  padding: 0 clamp(1rem, 8vw, 4rem) clamp(1.5rem, 4vw, 2.5rem);
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top, 0);
  padding-bottom: 4rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: linear-gradient(to right, #e4d4a4, #FADADD 60%, #E8E6F0 100%);
}
.page-head {
  width: 100%;
  padding: clamp(0.75rem, 2vh, 1.25rem) clamp(1rem, 4vw, 2rem);
  text-align: center;
  box-sizing: border-box;
  background: transparent;
}
.page-head-title {
  display: block;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(0.9rem, 2.2vw, 1.05rem);
  font-weight: 400;
  letter-spacing: 0.15em;
  color: rgba(90, 86, 82, 0.92);
  margin-bottom: 0.2rem;
}
.page-head-subtitle {
  display: block;
  font-weight: 300;
  font-size: clamp(0.68rem, 1.7vw, 0.72rem);
  letter-spacing: 0.18em;
  color: var(--aj-text-muted);
}
.page-head-caption {
  display: block;
  font-size: clamp(0.62rem, 1.5vw, 0.65rem);
  color: var(--aj-text-muted);
  opacity: 0.88;
  margin-top: 0.15rem;
}
.draw-inner {
  width: 100%;
  max-width: min(90vw, 720px);
}
.intro-main {
  font-size: 0.8125rem;
  line-height: 1.75;
  color: var(--aj-text-soft);
  margin: clamp(0.75rem, 2vh, 1.25rem) 0;
  text-align: left;
  white-space: pre-wrap;
}
.card-back-wrap {
  margin: clamp(0.75rem, 2vh, 1.25rem) 0;
}
.card-back {
  width: clamp(140px, 38vw, 200px);
  height: clamp(218px, 56vw, 312px);
  margin: 0 auto;
  border-radius: var(--aj-radius);
  overflow: hidden;
  filter: drop-shadow(0 2px 12px rgba(74, 74, 74, 0.06));
}
.card-back-img {
  width: 100%;
  height: 100%;
  display: block;
}
.btn-mirror {
  margin-top: clamp(0.75rem, 2vh, 1.25rem);
  width: 100%;
  max-width: clamp(160px, 44vw, 200px);
  display: block;
  margin-left: auto;
  margin-right: auto;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #e8c4d0 0%, #d4c8e8 50%, #c8d4e8 100%);
  border: none;
  color: rgba(90, 86, 82, 0.9);
}
.btn-mirror:active {
  opacity: 0.9;
}
.btn-mirror[disabled] {
  opacity: 0.7;
}
.disclaimer-secondary {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  font-size: 0.6875rem;
  color: var(--aj-text-muted);
  font-style: italic;
  padding: clamp(0.75rem, 2vh, 1rem) clamp(1rem, 8vw, 4rem);
  padding-bottom: calc(clamp(0.75rem, 2vh, 1rem) + env(safe-area-inset-bottom, 0));
  border-top: 1px solid var(--aj-border);
  text-align: center;
  background: linear-gradient(to top, rgba(250, 218, 221, 0.95), rgba(232, 230, 240, 0.9));
}
</style>
