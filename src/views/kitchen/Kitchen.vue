<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ChefHat, RefreshCw, Search } from 'lucide-vue-next'
import KitchenOrderList from '../../components/kitchen/KitchenOrderList.vue'
import { useOrderStore } from '../../stores/order.js'

const orderStore = useOrderStore()
const search = ref('')
const activeFilter = ref('active')
const updatingId = ref(null)
const actionError = ref('')
let refreshTimer

const kitchenOrders = computed(() => orderStore.orders
	.filter((order) => ['paid', 'awaiting_payment'].includes(order.status) && order.kitchenStatus)
	.slice()
	.sort((left, right) => new Date(left.createdAt) - new Date(right.createdAt)))
const counts = computed(() => ({
	queued: kitchenOrders.value.filter((order) => order.kitchenStatus === 'queued').length,
	preparing: kitchenOrders.value.filter((order) => order.kitchenStatus === 'preparing').length,
	ready: kitchenOrders.value.filter((order) => order.kitchenStatus === 'ready').length,
	completed: kitchenOrders.value.filter((order) => order.kitchenStatus === 'completed').length,
}))
const activeCount = computed(() => counts.value.queued + counts.value.preparing + counts.value.ready)
const visibleOrders = computed(() => {
	const query = search.value.trim().toLowerCase()
	return kitchenOrders.value.filter((order) => {
		const matchesSearch = `${order.id} ${order.customer} ${order.table} ${order.type} ${order.items.map((item) => item.name).join(' ')}`.toLowerCase().includes(query)
		const matchesFilter = activeFilter.value === 'active'
			? order.kitchenStatus !== 'completed'
			: order.kitchenStatus === activeFilter.value
		return matchesSearch && matchesFilter
	})
})
const filters = computed(() => [
	{ value: 'active', label: 'Active', count: activeCount.value },
	{ value: 'queued', label: 'New', count: counts.value.queued },
	{ value: 'preparing', label: 'Preparing', count: counts.value.preparing },
	{ value: 'ready', label: 'Ready', count: counts.value.ready },
	{ value: 'completed', label: 'Completed', count: counts.value.completed },
])

async function refreshOrders() {
	await orderStore.loadOrders().catch(() => undefined)
}

onMounted(() => {
	refreshOrders()
	refreshTimer = window.setInterval(refreshOrders, 15000)
})

onUnmounted(() => window.clearInterval(refreshTimer))

async function advanceOrder({ order, kitchenStatus }) {
	updatingId.value = order.id
	actionError.value = ''
	try {
		await orderStore.updateKitchenStatus(order.id, kitchenStatus)
	} catch (error) {
		actionError.value = error.message
	} finally {
		updatingId.value = null
	}
}
</script>

<template>
	<section class="min-h-screen min-w-0 bg-background px-5 py-7 sm:px-8 lg:px-10">
		<div class="mx-auto max-w-7xl">
			<header class="flex flex-col justify-between gap-5 border-b border-border pb-6 lg:flex-row lg:items-end">
				<div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Service line</p><h1 class="mt-2 flex items-center gap-3 text-3xl font-bold tracking-tight text-ink"><ChefHat :size="30" aria-hidden="true" /> Kitchen</h1><p class="mt-2 text-sm text-muted">{{ activeCount }} active {{ activeCount === 1 ? 'order' : 'orders' }} · refreshed every 15 seconds</p></div>
				<button type="button" class="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 rounded-sm border border-border bg-surface px-4 text-sm font-semibold text-ink hover:bg-background disabled:opacity-50" :disabled="orderStore.loading" @click="refreshOrders"><RefreshCw :size="16" aria-hidden="true" :class="orderStore.loading ? 'animate-spin' : ''" />Refresh</button>
			</header>

			<p v-if="orderStore.error" role="alert" class="mt-4 rounded-sm border border-border bg-surface px-4 py-3 text-sm text-danger">{{ orderStore.error }}</p>
			<p v-if="actionError" role="alert" class="mt-4 rounded-sm border border-border bg-surface px-4 py-3 text-sm text-danger">{{ actionError }}</p>

			<div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
				<article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3"><span class="text-sm font-medium text-muted">New</span><strong class="text-2xl text-brand-dark">{{ counts.queued }}</strong></article>
				<article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3"><span class="text-sm font-medium text-muted">Preparing</span><strong class="text-2xl text-amber-900">{{ counts.preparing }}</strong></article>
				<article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3"><span class="text-sm font-medium text-muted">Ready</span><strong class="text-2xl text-success">{{ counts.ready }}</strong></article>
				<article class="flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white"><span class="text-sm font-medium text-white/75">Active tickets</span><strong class="text-2xl">{{ activeCount }}</strong></article>
			</div>

			<section class="mt-8" aria-label="Kitchen orders">
				<div class="flex flex-col gap-3 border-b border-border pb-3 lg:flex-row lg:items-center lg:justify-between">
					<div class="flex gap-1 overflow-x-auto" aria-label="Filter kitchen orders"><button v-for="filter in filters" :key="filter.value" type="button" class="shrink-0 rounded-sm px-3 py-2 text-sm font-semibold" :class="activeFilter === filter.value ? 'bg-ink text-white' : 'text-muted hover:bg-surface hover:text-ink'" :aria-pressed="activeFilter === filter.value" @click="activeFilter = filter.value">{{ filter.label }} <span>{{ filter.count }}</span></button></div>
					<label class="relative block"><span class="sr-only">Search kitchen tickets</span><Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" /><input v-model="search" type="search" placeholder="Search tickets or items" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none focus:border-brand sm:w-60" /></label>
				</div>
				<div class="pt-4"><KitchenOrderList :orders="visibleOrders" :loading="orderStore.loading" :updating-id="updatingId" :empty-message="activeFilter === 'active' ? 'No active kitchen orders.' : `No ${activeFilter} orders.`" @advance="advanceOrder" /></div>
			</section>
		</div>
	</section>
</template>
