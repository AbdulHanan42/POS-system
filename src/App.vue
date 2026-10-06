<script setup>
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from './layouts/AuthLayout.vue'
import DefaultLayout from './layouts/DefaultLayout.vue'
import { useAuthStore } from './stores/auth.js'
import { useProductStore } from './stores/product.js'

const authStore = useAuthStore()
const productStore = useProductStore()
const route = useRoute()
const activeLayout = computed(() => route.meta.layout === 'auth' ? AuthLayout : DefaultLayout)

watch(() => authStore.user?.id, async (userId) => {
  if (!userId) {
    productStore.items = []
    return
  }
  await productStore.loadProducts().catch(() => undefined)
}, { immediate: true })
</script>

<template>
  <component :is="activeLayout" />
</template>
