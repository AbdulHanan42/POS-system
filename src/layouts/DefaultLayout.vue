<script setup>
import AppSidebar from '../components/layout/AppSidebar.vue'
</script>

<template>
  <div class="default-layout">
    <AppSidebar />
    <main><RouterView /></main>
  </div>
</template>

<style scoped>
.default-layout {
  display: flex;
  min-height: 100vh;
}

main {
  flex: 1;
}
</style>
