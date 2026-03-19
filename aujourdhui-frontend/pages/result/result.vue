<template>
  <view class="result-page">
    <view class="btn-back" @click="onBack">
      <text class="btn-back-icon">‹</text>
    </view>
    <view class="page-head">
      <text class="page-head-title">aujourd'hui</text>
      <text class="page-head-subtitle">L'image de soi</text>
      <text class="page-head-caption">今日镜像 · 照见当下</text>
    </view>

    <template v-if="phase === 'back'">
      <view class="flip-hint">轻轻触碰，翻开你的牌</view>
      <view
        class="flip-card-wrap"
        :class="{ 'flip-card-wrap--flipped': isFlipped }"
        @click="onCardClick"
      >
        <view class="flip-card">
          <view class="flip-card-face flip-card-back">
            <image class="card-back-img" src="/static/visual/back.jpg" mode="aspectFit" />
          </view>
          <view class="flip-card-face flip-card-front">
            <image
              v-if="drawn.card_image_url"
              class="tarot-image"
              :class="{ 'tarot-image--reversed': isReversed, 'tarot-image--loaded': cardImageLoaded }"
              :src="drawn.card_image_url"
              mode="aspectFit"
              @load="onCardFaceLoad"
            />
            <view v-else class="tarot-placeholder">{{ drawn.card_name || '牌面' }}</view>
          </view>
        </view>
      </view>
    </template>

    <template v-else>
      <view class="reveal-wrap">
        <view class="card-col">
          <image
            v-if="drawn.card_image_url"
            class="tarot-image"
            :class="{ 'tarot-image--reversed': isReversed }"
            :src="drawn.card_image_url"
            mode="aspectFit"
          />
          <view v-else class="tarot-placeholder">{{ drawn.card_name || '牌面' }}</view>
        </view>
        <view class="mirror-output mirror-fade-in">
          <view class="card-name">{{ drawn.card_name }}</view>
          <view v-if="isReversed" class="reversed-intro">{{ INTRO_REVERSED }}</view>
          <view class="two-col">
            <view class="col-left">
              <view class="label">「当下叙事」</view>
              <view class="narrative-text">{{ displayNarrative }}</view>
            </view>
            <view class="col-right">
              <view class="label">「名画意境」</view>
              <view class="artwork-meta">{{ artworkMeta }}</view>
              <view v-if="artworkUrl">
                <text class="link" @click="openArtwork">查看作品</text>
              </view>
              <view v-if="artworkReason" class="artwork-reason">{{ artworkReason }}</view>
            </view>
          </view>
          <view class="intro-after">{{ INTRO_AFTER_DRAW }}</view>
        </view>
      </view>
    </template>

    <view class="disclaimer">{{ DISCLAIMER }}</view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const INTRO_REVERSED = "这张牌以逆位呈现，如同镜子被稍稍偏移了一个角度。它邀请我们观察同一种原型能量在当下可能呈现的另一种状态——或许是更内在的、正在调整的、或需要被温柔关注的一面。"
const INTRO_AFTER_DRAW = "这张牌如同今日心理风景的一帧快照，提供了一个对话的起点。所有解读都是可探讨、可质疑、可重新诠释的。你今天如何理解这份「镜像」？"
const DISCLAIMER = "本服务仅供美学启发与心理平衡，不具临床诊断价值。你对自己的生活拥有最终决定权。"

const phase = ref('back')
const isFlipped = ref(false)
const cardImageLoaded = ref(false)
const drawn = ref({
  card_name: '',
  base_meaning: '',
  narrative: '',
  artwork: {},
  card_image_url: '',
})

const isReversed = computed(() => (drawn.value.card_name || '').includes(' · 逆位'))

const artwork = computed(() => drawn.value.artwork || {})
const artworkMeta = computed(() => {
  const a = artwork.value
  if (!a.artist && !a.title && !a.year) return ''
  return [a.artist, a.title, a.year ? `(${a.year})` : ''].filter(Boolean).join(' · ')
})
const artworkUrl = computed(() => artwork.value.url)
const artworkReason = computed(() => stripMarkdown(artwork.value.reason || ''))

/** 去除 AI/Markdown 格式残留，确保前端不展示 ** 等痕迹 */
function stripMarkdown(text) {
  if (!text || typeof text !== 'string') return ''
  return text.replace(/\*\*/g, '')
}

const displayNarrative = computed(() => stripMarkdown(drawn.value.narrative || ''))

onMounted(() => {
  const data = uni.getStorageSync('drawn_card')
  if (data && data.card_name) {
    drawn.value = data
    preloadCardImage(data.card_image_url)
  } else {
    uni.showToast({ title: '请先抽牌', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1500)
  }
})

function preloadCardImage(url) {
  if (!url) return
  const img = new Image()
  img.src = url
}

function onCardClick() {
  if (isFlipped.value) return
  isFlipped.value = true
  setTimeout(() => {
    phase.value = 'reveal'
  }, 800)
}

function onCardFaceLoad() {
  cardImageLoaded.value = true
}

function onBack() {
  uni.navigateBack()
}

function openArtwork() {
  const url = drawn.value.artwork?.url
  if (!url) return
  // H5 新窗口打开；App 用系统浏览器；小程序可复制链接
  // #ifdef H5
  window.open(url)
  // #endif
  // #ifdef APP-PLUS
  plus.runtime.openURL(url)
  // #endif
  // #ifdef MP-WEIXIN || MP-ALIPAY || MP
  uni.setClipboardData({ data: url })
  uni.showToast({ title: '链接已复制' })
  // #endif
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
.result-page {
  width: 100%;
  min-height: 100vh;
  padding: 0 clamp(1rem, 6vw, 3rem) clamp(1.5rem, 5vw, 2.5rem);
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top, 0);
  padding-bottom: 4rem;
  box-sizing: border-box;
  background: linear-gradient(180deg, #FADADD 0%, #E8E6F0 50%, #E6E6FA 100%);
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
.flip-hint {
  text-align: center;
  font-size: 0.8125rem;
  letter-spacing: 0.12em;
  color: var(--aj-text-soft);
  margin: clamp(0.75rem, 2vh, 1rem) 0 clamp(0.5rem, 1vh, 0.75rem);
}
.flip-card-wrap {
  width: clamp(140px, 38vw, 180px);
  height: clamp(218px, 59vw, 280px);
  margin: clamp(0.5rem, 1.5vh, 0.75rem) auto;
  perspective: 1000px;
  cursor: pointer;
}
.flip-card-wrap--flipped .flip-card {
  transform: rotateY(180deg);
}
.flip-card {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.flip-card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: var(--aj-radius);
  overflow: hidden;
  filter: drop-shadow(0 2px 12px rgba(74, 74, 74, 0.06));
}
.flip-card-back {
  background: transparent;
}
.flip-card-front {
  transform: rotateY(180deg);
  background: linear-gradient(160deg, #e2ddd8 0%, #e8e4df 100%);
}
.card-back-img {
  width: 100%;
  height: 100%;
  display: block;
}
.flip-card-front .tarot-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  opacity: 0;
  transition: opacity 0.4s ease-out;
}
.flip-card-front .tarot-image--loaded {
  opacity: 1;
}
.flip-card-front .tarot-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--aj-text-soft);
  font-size: 0.8125rem;
}
.reveal-wrap {
  margin-top: clamp(0.5rem, 1.5vh, 0.75rem);
}
.card-col {
  text-align: center;
  margin-bottom: clamp(0.75rem, 2vh, 1rem);
}
.tarot-image {
  width: clamp(140px, 38vw, 180px);
  height: clamp(218px, 59vw, 280px);
  object-fit: contain;
  border-radius: var(--aj-radius);
  filter: drop-shadow(0 2px 12px rgba(74, 74, 74, 0.06));
}
.tarot-image--reversed {
  transform: rotate(180deg);
}
.tarot-placeholder {
  width: clamp(140px, 38vw, 180px);
  height: clamp(218px, 59vw, 280px);
  margin: 0 auto;
  background: linear-gradient(160deg, #e2ddd8 0%, #e8e4df 100%);
  border-radius: var(--aj-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--aj-text-soft);
  font-size: 0.8125rem;
  filter: drop-shadow(0 2px 12px rgba(74, 74, 74, 0.06));
}
.mirror-output {
  margin-top: clamp(0.5rem, 1.5vh, 0.75rem);
  padding: clamp(0.75rem, 2.5vw, 1rem);
  background: var(--aj-bg-paper);
  border-radius: var(--aj-radius);
  border: 1px solid var(--aj-border);
  color: var(--aj-text);
  font-size: 0.8125rem;
  line-height: 1.75;
}
.mirror-fade-in {
  animation: mirrorFadeIn 0.6s ease-out forwards;
}
@keyframes mirrorFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.card-name {
  font-weight: 300;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
  color: var(--aj-text);
  font-size: 0.9375rem;
}
.reversed-intro {
  font-size: 0.75rem;
  color: var(--aj-text-soft);
  margin-bottom: 0.5rem;
}
.two-col {
  display: flex;
  flex-direction: row;
  gap: clamp(1rem, 4vw, 2rem);
  margin-top: 0.5rem;
  align-items: flex-start;
}
.col-left {
  flex: 1;
  min-width: 0;
  text-align: left;
}
.col-right {
  flex: 1;
  min-width: 0;
  text-align: right;
}
.label {
  font-weight: 700;
  margin-top: 0.5rem;
  margin-bottom: 0.2rem;
  color: var(--aj-text-soft);
  font-size: 0.6875rem;
  letter-spacing: 0.06em;
}
.two-col .label:first-child {
  margin-top: 0;
}
.narrative-text {
  margin-top: 0.2rem;
  white-space: pre-wrap;
}
.artwork-meta {
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  color: var(--aj-text-soft);
}
.col-right .artwork-meta {
  margin-top: 0.2rem;
}
.link {
  color: var(--aj-accent);
  text-decoration: underline;
  margin-top: 0.25rem;
  display: inline-block;
  letter-spacing: 0.04em;
  font-size: 0.8125rem;
  cursor: pointer;
}
.link:active {
  opacity: 0.8;
}
.artwork-reason {
  font-size: 0.8125rem;
  margin-top: 0.5rem;
  color: var(--aj-text-muted);
}
.intro-after {
  font-size: 0.8125rem;
  color: var(--aj-text-muted);
  margin-top: 0.75rem;
}
.disclaimer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  font-size: 0.6875rem;
  color: var(--aj-text-muted);
  font-style: italic;
  padding: clamp(0.75rem, 2vh, 1rem) clamp(1rem, 6vw, 3rem);
  padding-bottom: calc(clamp(0.75rem, 2vh, 1rem) + env(safe-area-inset-bottom, 0));
  border-top: 1px solid var(--aj-border);
  text-align: center;
  background: linear-gradient(to top, rgba(250, 218, 221, 0.95), rgba(232, 230, 240, 0.9));
}
</style>
