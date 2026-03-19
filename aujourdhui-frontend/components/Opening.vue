<template>
  <view class="opening">
    <view class="page-head">
      <text class="page-head-title">aujourd'hui</text>
    </view>
    <!-- 画作 + 画作信息：artwork-block 固定相对位置，不随画幅变化 -->
    <view class="artwork-fixed-container">
      <view class="artwork-block">
        <view class="artwork-img-wrap">
          <image
            class="artwork-img"
            :src="artworkSrc"
            mode="aspectFit"
            @error="onArtworkLoadError"
          />
        </view>
        <view class="artwork-label">
          <view class="artwork-title">The Magic Circle</view>
          <view class="artwork-author">1886, John William Waterhouse</view>
        </view>
      </view>
    </view>
    <!-- 文字和按钮：锁定板块，不固定，可滚动 -->
    <view class="stage-body">
      <view class="narrative-block">
        <text class="tagline">tell me about today</text>
        <view class="jump-wrap">
          <view class="jump-dot" @click="onMainAction" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const ARTWORK_LOCAL = '/static/visual/the%20magic%20circle.jpg'
const ARTWORK_FALLBACK = 'https://upload.wikimedia.org/wikipedia/commons/3/33/The_Magic_Circle_-_John_William_Waterhouse.jpg'

const artworkSrc = ref(ARTWORK_LOCAL)

function onArtworkLoadError() {
  artworkSrc.value = ARTWORK_FALLBACK
}

function onMainAction() {
  uni.navigateTo({ url: '/pages/draw/draw' })
}
</script>

<style scoped>
.opening {
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
}

.page-head {
  width: 100%;
  padding: clamp(0.75rem, 2vh, 1.25rem) clamp(1rem, 4vw, 2rem);
  text-align: center;
  box-sizing: border-box;
  background: transparent;
}

.page-head-title {
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(0.9rem, 2.2vw, 1.05rem);
  font-weight: 400;
  letter-spacing: 0.15em;
  color: rgba(51, 51, 51, 0.92);
}

/* 整体固定布局：画作+标签锁定为一体，严格靠左 */
.artwork-fixed-container {
  position: fixed;
  left: 3vw;
  top: env(safe-area-inset-top, 0);
  width: 44vw;
  z-index: 1;
  padding-top: 10vh;
  box-sizing: border-box;
  pointer-events: none;
}

.artwork-fixed-container * {
  pointer-events: auto;
}

/* 画作模块：画作与标签相对位置固定，用 rem 不随画幅变化 */
.artwork-block {
  display: block;
  width: 100%;
}

.artwork-img-wrap {
  display: block;
  width: 100%;
  height: 68vh;
  min-height: 220px;
}

.artwork-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: left center;
  margin: 0;
  filter: drop-shadow(0 2px 12px rgba(74, 74, 74, 0.06));
}

/* 画作信息：画作正下方、偏左，与画作间距固定（rem） */
.artwork-label {
  display: block;
  margin-top: 0.5rem;
  margin-left: 10vw;
  padding: 0;
  width: 100%;
  text-align: left;
  box-sizing: border-box;
}

.artwork-label .artwork-title {
  font-family: "Calibri", "Calibri MS", sans-serif;
  font-size: 0.95rem;
  font-weight: 400;
  color: #333;
  line-height: 1.35;
}

.artwork-label .artwork-author {
  font-family: "Calibri", "Calibri MS", sans-serif;
  font-size: 0.8rem;
  font-weight: 400;
  color: #555;
  margin-top: 2px;
}

.stage-body {
  margin-left: 50vw;
  padding: clamp(2rem, 6vh, 4rem) clamp(1.5rem, 4vw, 3rem);
  box-sizing: border-box;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.narrative-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.tagline {
  font-family: "Times New Roman", Times, serif;
  font-size: 1rem;
  font-weight: 400;
  color: #614d37;
  line-height: 1.5;
}

.jump-wrap {
  margin-top: 1.5vh;
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.jump-dot {
  width: 3vh;
  height: 3vh;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b571c 0%, #614d37 50%, #5a4530 100%);
  border: none;
  cursor: pointer;
  animation: breathe 2.5s ease-in-out infinite;
}

.jump-dot:active {
  opacity: 0.9;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}
</style>
