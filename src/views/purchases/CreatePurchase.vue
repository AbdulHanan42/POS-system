<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus, Trash2 } from 'lucide-vue-next'
import { useProductStore } from '../../stores/product.js'
import { usePurchaseStore } from '../../stores/purchase.js'

const router = useRouter()
const productStore = useProductStore()
const purchaseStore = usePurchaseStore()
const supplier = ref('')
const items = ref([{ productId: '', quantity: 1, unitCost: '' }])
const formError = ref('')
const total = computed(() => items.value.reduce((sum, item) => sum + Number(item.quantity || 0) * Number(item.unitCost || 0), 0))
const activeProducts = computed(() => productStore.items.filter((product) => product.status === 'active'))
const formatCurrency = (value) => `$${Number(value).toFixed(2)}`

onMounted(() => productStore.loadProducts().catch(() => undefined))

function addItem() {
	items.value.push({ productId: '', quantity: 1, unitCost: '' })
}

function removeItem(index) {
	if (items.value.length > 1) items.value.splice(index, 1)
}

async function submitPurchase() {
	formError.value = ''
	const productIds = items.value.map((item) => Number(item.productId))
	if (productIds.some((id) => !id) || new Set(productIds).size !== productIds.length) {
		formError.value = 'Choose a different product for each line.'
		return
	}
	try {
		await purchaseStore.create({
			supplier: supplier.value.trim(),
			items: items.value.map((item) => ({ productId: Number(item.productId), quantity: Number(item.quantity), unitCost: Number(item.unitCost) })),
		})
		await router.push('/purchases')
	} catch (error) {
		formError.value = error.message
	}
}
</script>

<template>
	<section class="min-h-screen bg-background px-5 py-7 sm:px-8 lg:px-10">
		<div class="mx-auto max-w-4xl">
			<RouterLink to="/purchases" class="inline-flex min-h-9 items-center gap-2 text-sm font-semibold text-muted hover:text-ink"><ArrowLeft :size="16" aria-hidden="true" /> Purchases</RouterLink>
			<header class="mt-5 border-b border-border pb-6"><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Supplier order</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">New purchase</h1><p class="mt-2 text-sm text-muted">Save the order first, then receive it when the delivery arrives.</p></header>
			<p v-if="productStore.error" role="alert" class="mt-4 text-sm text-danger">{{ productStore.error }}</p>
			<form class="mt-6" @submit.prevent="submitPurchase">
				<label class="grid max-w-xl gap-2 text-sm font-semibold text-ink">Supplier name<input v-model.trim="supplier" required maxlength="120" autocomplete="organization" placeholder="Supplier or vendor" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
				<div class="mt-8 flex items-end justify-between gap-4 border-b border-border pb-3"><div><h2 class="text-lg font-bold text-ink">Items</h2><p class="mt-1 text-sm text-muted">Enter the quantity and unit cost for each product.</p></div><button type="button" class="inline-flex min-h-9 shrink-0 items-center gap-2 rounded-sm border border-border bg-surface px-3 text-sm font-semibold text-ink hover:bg-background" @click="addItem"><Plus :size="16" aria-hidden="true" /> Add line</button></div>
				<div class="mt-3 space-y-3"><div v-for="(item, index) in items" :key="index" class="grid gap-3 border-b border-border bg-surface/50 py-4 sm:grid-cols-[minmax(0,1fr)_110px_140px_40px] sm:items-end">
					<label class="grid gap-2 text-xs font-bold uppercase tracking-wide text-muted">Product<select v-model="item.productId" required class="h-10 rounded-sm border border-border bg-surface px-3 text-sm font-normal normal-case tracking-normal text-ink outline-none focus:border-brand"><option value="" disabled>Select product</option><option v-for="product in activeProducts" :key="product.id" :value="String(product.id)" :disabled="items.some((other, otherIndex) => otherIndex !== index && Number(other.productId) === product.id)">{{ product.name }} · {{ product.category }}</option></select></label>
					<label class="grid gap-2 text-xs font-bold uppercase tracking-wide text-muted">Quantity<input v-model.number="item.quantity" required type="number" min="1" step="1" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm font-normal normal-case tracking-normal text-ink outline-none focus:border-brand" /></label>
					<label class="grid gap-2 text-xs font-bold uppercase tracking-wide text-muted">Unit cost<input v-model.number="item.unitCost" required type="number" min="0" step="0.01" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm font-normal normal-case tracking-normal text-ink outline-none focus:border-brand" placeholder="0.00" /></label>
					<button type="button" class="grid size-10 place-items-center rounded-sm text-muted hover:bg-background hover:text-danger disabled:opacity-40" :aria-label="`Remove line ${index + 1}`" :disabled="items.length === 1" @click="removeItem(index)"><Trash2 :size="16" aria-hidden="true" /></button>
				</div></div>
				<div v-if="!productStore.loading && !activeProducts.length" class="mt-4 rounded-sm border border-border bg-surface px-4 py-4 text-sm text-muted">There are no active products to add to a purchase.</div><div v-if="productStore.loading" role="status" class="mt-4 text-sm text-muted">Loading products...</div>
				<div class="mt-6 flex flex-col gap-5 border-t border-border pt-5 sm:flex-row sm:items-center sm:justify-between"><div><span class="text-sm font-medium text-muted">Purchase total</span><strong class="ml-3 text-xl text-ink">{{ formatCurrency(total) }}</strong></div><div class="flex flex-col-reverse gap-2 sm:flex-row"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-surface" :disabled="purchaseStore.saving" @click="router.push('/purchases')">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="purchaseStore.saving || productStore.loading || !activeProducts.length">{{ purchaseStore.saving ? 'Saving...' : 'Save purchase' }}</button></div></div>
				<p v-if="formError" role="alert" class="mt-4 text-sm text-danger">{{ formError }}</p>
			</form>
		</div>
	</section>
</template>
