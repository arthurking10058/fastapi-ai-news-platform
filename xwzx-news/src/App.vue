<template>
  <div class="app">
    <router-view v-slot="{ Component, route }">
      <keep-alive :include="KEEP_ALIVE_ROUTE_NAMES">
        <component
          v-if="route.meta.keepAlive"
          :is="Component"
          :key="route.name"
        />
      </keep-alive>
      <component
        v-if="!route.meta.keepAlive"
        :is="Component"
        :key="route.fullPath"
      />
    </router-view>
  </div>
</template>

<script setup>
const KEEP_ALIVE_ROUTE_NAMES = ['Home', 'Category', 'AIChat', 'My']
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 16px;
  background-color: #f7f8fa;
  color: #333;
  height: 100%;
  width: 100%;
}

.app {
  max-width: 750px;
  margin: 0 auto;
  height: 100%;
}

/* 移动端适配 */
@media screen and (max-width: 750px) {
  html {
    font-size: calc(100vw / 750 * 16);
  }
}
</style>
