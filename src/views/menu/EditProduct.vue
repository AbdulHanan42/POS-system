<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProductForm from '../../components/products/ProductForm.vue'
import { useProductStore } from '../../stores/product.js'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const product = computed(() => productStore.items.find((item) => item.id === Number(route.params.id)))
function updateProduct(value) { productStore.updateProduct({ ...value, id: product.value.id }); router.push('/menu/products') }
</script>

<template>
	<section class="min-h-screen bg-background px-6 py-8 lg:px-10"><div v-if="product" class="mx-auto max-w-3xl"><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu management</p><h1 class="mt-2 text-3xl font-bold text-ink">Edit product</h1><p class="mt-2 text-sm text-muted">Update pricing, details, and availability.</p><div class="mt-6"><ProductForm :initial-product="product" submit-label="Save changes" @submit="updateProduct" @cancel="router.push('/menu/products')" /></div></div><div v-else class="mx-auto max-w-3xl text-sm text-muted">Product not found.</div></section>
</template>
