<script setup>
import { computed, onMounted, ref } from 'vue'
import { Check, PackageCheck, Plus, Search } from 'lucide-vue-next'
import { usePurchaseStore } from '../../stores/purchase.js'

const purchaseStore = usePurchaseStore()
const search = ref('')
const statusFilter = ref('all')
const actionError = ref('')
const visiblePurchases = computed(() => {
	const query = search.value.trim().toLowerCase()
	return purchaseStore.purchases.filter((purchase) => {
		const matchesSearch = `${purchase.supplier} ${purchase.id}`.toLowerCase().includes(query)
		return matchesSearch && (statusFilter.value === 'all' || purchase.status === statusFilter.value)
	})
})
const pendingCount = computed(() => purchaseStore.purchases.filter((purchase) => purchase.status === 'pending').length)
const totalSpend = computed(() => purchaseStore.purchases.filter((purchase) => purchase.status === 'received').reduce((total, purchase) => total + Number(purchase.total), 0))
const formatCurrency = (value) => `$${Number(value).toFixed(2)}`
const formatDate = (value) => new Date(value).toLocaleDateString(undefined, { dateStyle: 'medium' })

onMounted(() => purchaseStore.load().catch(() => undefined))

async function receivePurchase(purchase) {
	actionError.value = ''
	try {
		await purchaseStore.receive(purchase.id)
	} catch (error) {
		actionError.value = error.message
	}
}
</script>

<template>
	<section class="min-h-screen min-w-0 bg-background px-5 py-7 sm:px-8 lg:px-10">
		<div class="mx-auto max-w-7xl">
			<header class="flex flex-col justify-between gap-5 border-b border-border pb-6 lg:flex-row lg:items-end">
				<div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Operations</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Purchases</h1><p class="mt-2 text-sm text-muted">Record supplier orders and receive stock into inventory.</p></div>
				<RouterLink to="/purchases/new" class="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark"><Plus :size="16" aria-hidden="true" /> New purchase</RouterLink>
			</header>

			<p v-if="purchaseStore.error" role="alert" class="mt-4 rounded-sm border border-border bg-surface px-4 py-3 text-sm text-danger">{{ purchaseStore.error }}</p>
			<p v-if="actionError" role="alert" class="mt-4 rounded-sm border border-border bg-surface px-4 py-3 text-sm text-danger">{{ actionError }}</p>
			<div class="mt-6 grid gap-3 sm:grid-cols-2">
				<article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Awaiting receipt</span><strong class="text-2xl text-brand-dark">{{ pendingCount }}</strong></article>
				<article class="flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white shadow-sm"><span class="text-sm font-medium text-white/75">Received purchase value</span><strong class="text-xl">{{ formatCurrency(totalSpend) }}</strong></article>
			</div>

			<section class="mt-8" aria-labelledby="purchases-heading">
				<div class="flex flex-col gap-4 border-b border-border pb-4 lg:flex-row lg:items-center lg:justify-between"><div><h2 id="purchases-heading" class="text-lg font-bold text-ink">Purchase records</h2><p class="mt-1 text-sm text-muted">{{ visiblePurchases.length }} of {{ purchaseStore.purchases.length }} purchases</p></div><label class="relative block"><span class="sr-only">Search purchases</span><Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" /><input v-model="search" type="search" placeholder="Search supplier or ID" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none focus:border-brand sm:w-60" /></label></div>
				<div class="flex gap-1 overflow-x-auto border-b border-border py-3" aria-label="Filter purchase status"><button v-for="filter in [{ value: 'all', label: 'All purchases' }, { value: 'pending', label: 'Pending' }, { value: 'received', label: 'Received' }]" :key="filter.value" type="button" class="shrink-0 rounded-sm px-3 py-2 text-sm font-semibold" :class="statusFilter === filter.value ? 'bg-ink text-white' : 'text-muted hover:bg-surface hover:text-ink'" :aria-pressed="statusFilter === filter.value" @click="statusFilter = filter.value">{{ filter.label }}<span v-if="filter.value === 'pending'" class="ml-1">{{ pendingCount }}</span></button></div>

				<div v-if="purchaseStore.loading" role="status" class="py-14 text-center text-sm text-muted">Loading purchases...</div>
				<div v-else-if="visiblePurchases.length" class="overflow-x-auto">
					<table class="w-full min-w-[720px] border-collapse text-left"><thead><tr class="border-b border-border text-xs font-bold uppercase tracking-wide text-muted"><th class="py-3 pr-4">Purchase</th><th class="px-3 py-3">Supplier</th><th class="px-3 py-3">Items</th><th class="px-3 py-3">Total</th><th class="px-3 py-3">Status</th><th class="py-3 pl-3 text-right">Action</th></tr></thead>
						<tbody><tr v-for="purchase in visiblePurchases" :key="purchase.id" class="border-b border-border bg-surface/50 hover:bg-surface">
							<td class="py-4 pr-4"><strong class="block text-sm text-ink">#{{ purchase.id }}</strong><small class="mt-1 block text-xs text-muted">{{ formatDate(purchase.createdAt) }}</small></td><td class="px-3 py-4 text-sm font-medium text-ink">{{ purchase.supplier }}</td><td class="px-3 py-4 text-sm text-muted">{{ purchase.items.length }} lines · {{ purchase.items.reduce((sum, item) => sum + item.quantity, 0) }} units</td><td class="px-3 py-4 text-sm font-semibold text-ink">{{ formatCurrency(purchase.total) }}</td>
							<td class="px-3 py-4"><span class="rounded-sm px-2 py-1 text-xs font-bold" :class="purchase.status === 'received' ? 'bg-success/10 text-success' : 'bg-brand/10 text-brand-dark'">{{ purchase.status === 'received' ? 'Received' : 'Pending' }}</span></td>
							<td class="py-4 pl-3 text-right"><button v-if="purchase.status === 'pending'" type="button" class="inline-flex min-h-9 items-center justify-center gap-2 rounded-sm border border-border bg-surface px-3 text-xs font-semibold text-ink hover:bg-background disabled:opacity-50" :disabled="purchaseStore.receivingId !== null" @click="receivePurchase(purchase)"><PackageCheck :size="15" aria-hidden="true" />{{ purchaseStore.receivingId === purchase.id ? 'Receiving...' : 'Receive stock' }}</button><span v-else class="inline-flex items-center gap-1 text-xs font-semibold text-success"><Check :size="15" aria-hidden="true" />Stock added</span></td>
						</tr></tbody>
					</table>
				</div>
				<div v-else-if="!purchaseStore.loading" class="py-14 text-center"><PackageCheck :size="24" class="mx-auto text-muted" aria-hidden="true" /><p class="mt-3 font-semibold text-ink">{{ purchaseStore.purchases.length ? 'No matching purchases' : 'No purchases recorded' }}</p><p class="mt-1 text-sm text-muted">{{ purchaseStore.purchases.length ? 'Try another search or status filter.' : 'Create a purchase to start tracking supplier deliveries.' }}</p><RouterLink v-if="!purchaseStore.purchases.length" to="/purchases/new" class="mt-4 inline-flex min-h-10 items-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark"><Plus :size="16" aria-hidden="true" /> New purchase</RouterLink></div>
			</section>
		</div>
	</section>
</template>
