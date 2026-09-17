<script setup>
import { useRouter } from 'vue-router'
import ProductForm from '../../components/products/ProductForm.vue'
import { useProductStore } from '../../stores/product.js'

const router = useRouter()
const productStore = useProductStore()
function createProduct(product) { productStore.addProduct(product); router.push('/menu/products') }
</script>

<template>
	<section class="min-h-screen bg-background px-6 py-8 lg:px-10"><div class="mx-auto max-w-3xl"><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu management</p><h1 class="mt-2 text-3xl font-bold text-ink">Add product</h1><p class="mt-2 text-sm text-muted">Create a new item for your restaurant menu.</p><div class="mt-6"><ProductForm submit-label="Create product" @submit="createProduct" @cancel="router.push('/menu/products')" /></div></div></section>
</template>
