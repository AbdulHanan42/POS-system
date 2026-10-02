<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '../../components/common/BaseButton.vue'
import DeleteProductModal from '../../components/products/DeleteProductModal.vue'
import ProductFilter from '../../components/products/ProductFilter.vue'
import ProductSearch from '../../components/products/ProductSearch.vue'
import ProductTable from '../../components/products/ProductTable.vue'
import { useProductStore } from '../../stores/product.js'

const router = useRouter()
const productStore = useProductStore()
const search = ref('')
const category = ref('All')
const status = ref('all')
const productToDelete = ref(null)

const filteredProducts = computed(() => productStore.items.filter((product) => {
	const matchesSearch = product.name.toLowerCase().includes(search.value.toLowerCase())
	const matchesCategory = category.value === 'All' || product.category === category.value
	const matchesStatus = status.value === 'all' || product.status === status.value
	return matchesSearch && matchesCategory && matchesStatus
}))

async function deleteProduct() {
	try {
		await productStore.deleteProduct(productToDelete.value.id)
		productToDelete.value = null
	} catch {
		// Keep the dialog open so the user can retry.
	}
}
</script>

<template>
	<section class="min-h-screen bg-background px-6 py-8 lg:px-10">
		<div class="mx-auto max-w-7xl">
			<header class="flex flex-col justify-between gap-5 border-b border-border pb-6 sm:flex-row sm:items-end">
				<div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu management</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Products</h1><p class="mt-2 text-sm text-muted">Manage the dishes and drinks available at your restaurant.</p></div>
				<BaseButton @click="router.push('/menu/products/create')">+ Add product</BaseButton>
			</header>
			<div class="mt-6 flex flex-col gap-3 rounded-lg border border-border bg-surface p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between"><ProductSearch v-model="search" /><ProductFilter v-model:category="category" v-model:status="status" :categories="productStore.categories" /></div>
			<div class="mt-6 flex items-center justify-between"><p class="text-sm text-muted"><strong class="text-ink">{{ filteredProducts.length }}</strong> products</p><span class="text-xs text-muted">Updated just now</span></div>
			<p v-if="productStore.error" role="alert" class="mt-3 text-sm text-danger">{{ productStore.error }}</p>
			<div class="mt-3"><ProductTable :products="filteredProducts" @view="(product) => router.push(`/menu/products/${product.id}`)" @edit="(product) => router.push(`/menu/products/${product.id}/edit`)" @delete="productToDelete = $event" /></div>
		</div>
		<DeleteProductModal :open="Boolean(productToDelete)" :product="productToDelete" @cancel="productToDelete = null" @confirm="deleteProduct" />
	</section>
</template>
