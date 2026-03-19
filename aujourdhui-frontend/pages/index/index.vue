<template>
  <view class="stage">
    <Opening />
  </view>
</template>

<script setup>
import Opening from '../../components/Opening.vue'
</script>

<style scoped>
.stage {
  width: 100vw;
  min-height: 100vh;
  box-sizing: border-box;
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top, 0);
  background: linear-gradient(to right, #8b571c, #e4d4a4);
}
</style>
