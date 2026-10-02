<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseButton from '../../components/common/BaseButton.vue'
import ProductDetailsCard from '../../components/products/ProductDetailsCard.vue'
import { useProductStore } from '../../stores/product.js'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const product = computed(() => productStore.items.find((item) => item.id === Number(route.params.id)))
</script>

<template>
  <section class="min-h-screen bg-background px-6 py-8 lg:px-10"><div class="mx-auto max-w-3xl"><div class="mb-6 flex items-center justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu management</p><h1 class="mt-2 text-3xl font-bold text-ink">Product details</h1></div><BaseButton variant="secondary" @click="router.push('/menu/products')">Back to products</BaseButton></div><ProductDetailsCard v-if="product" :product="product" /><p v-else class="text-sm text-muted">Product not found.</p></div></section>
</template>
