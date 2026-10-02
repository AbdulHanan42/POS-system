<script setup>
import { onMounted } from 'vue'
import DefaultLayout from './layouts/DefaultLayout.vue'
import { useProductStore } from './stores/product.js'

const productStore = useProductStore()

onMounted(async () => {
  try {
    await productStore.loadProducts()
  } catch {
    // The store retains the API error for product screens to display.
  }
})
</script>

<template>
  <DefaultLayout />
</template>
