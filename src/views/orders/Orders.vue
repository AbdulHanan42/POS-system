<script setup>
import { computed, onMounted, ref } from 'vue'
import BaseButton from '../../components/common/BaseButton.vue'
import BaseModal from '../../components/common/BaseModal.vue'
import { useOrderStore } from '../../stores/order.js'

const orderStore = useOrderStore()
const search = ref('')
const status = ref('all')
const channel = ref('all')
const period = ref('all')
const selectedOrder = ref(null)
const refundCandidate = ref(null)
const orderError = ref('')
const page = ref(1)
const pageSize = 6

onMounted(async () => {
	try {
		await orderStore.loadOrders()
	} catch (error) {
		orderError.value = error.message
	}
})

const formatCurrency = (value) => `$${Number(value).toFixed(2)}`
const formatDate = (date) => new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date(date))
const relativeTime = (date) => {
	const minutes = Math.max(1, Math.round((Date.now() - new Date(date).getTime()) / 60000))
	return minutes < 60 ? `${minutes} min ago` : `${Math.round(minutes / 60)} hr ago`
}
const periodStart = computed(() => {
	if (period.value === 'all') return 0
	const days = period.value === 'today' ? 1 : Number(period.value)
	return Date.now() - days * 24 * 60 * 60 * 1000
})
const filteredOrders = computed(() => {
	const query = search.value.trim().toLowerCase()
	return orderStore.orders.filter((order) => {
		const searchable = `${order.id} ${order.customer} ${order.type} ${order.table} ${order.paymentMethod}`.toLowerCase()
		const matchesSearch = !query || searchable.includes(query)
		const matchesStatus = status.value === 'all' || order.status === status.value
		const matchesChannel = channel.value === 'all' || order.type === channel.value
		const matchesPeriod = new Date(order.createdAt).getTime() >= periodStart.value
		return matchesSearch && matchesStatus && matchesChannel && matchesPeriod
	})
})
const pageCount = computed(() => Math.max(1, Math.ceil(filteredOrders.value.length / pageSize)))
const pagedOrders = computed(() => filteredOrders.value.slice((page.value - 1) * pageSize, page.value * pageSize))
const paidOrders = computed(() => orderStore.orders.filter((order) => order.status === 'paid'))
const paidRevenue = computed(() => paidOrders.value.reduce((sum, order) => sum + order.total, 0))
const refundedRevenue = computed(() => orderStore.orders.filter((order) => order.status === 'refunded').reduce((sum, order) => sum + order.total, 0))
const averageOrder = computed(() => paidOrders.value.length ? paidRevenue.value / paidOrders.value.length : 0)

function resetPage() { page.value = 1 }
function clearFilters() { search.value = ''; status.value = 'all'; channel.value = 'all'; period.value = 'all'; resetPage() }
function openOrder(order) { selectedOrder.value = order }
function requestRefund(order) { refundCandidate.value = order }
async function refundOrder() {
	orderError.value = ''
	try {
		const updated = await orderStore.updateStatus(refundCandidate.value.id, 'refunded')
		if (selectedOrder.value?.id === updated.id) selectedOrder.value = updated
		refundCandidate.value = null
	} catch (error) {
		orderError.value = error.message
	}
}
function printOrder() { window.print() }
</script>

<template>
	<section class="orders-page">
		<header class="orders-header">
			<div><p class="eyebrow">Revenue control</p><h1>Orders</h1><p class="muted">Track every ticket from the counter to payment.</p></div>
			<div class="header-actions"><span class="register-status"><i></i> Register open</span><RouterLink class="primary-action" to="/pos">New order <span aria-hidden="true">-&gt;</span></RouterLink></div>
		</header>
		<p v-if="orderError" role="alert" class="mb-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger">{{ orderError }}</p>
		<p v-if="orderStore.loading" role="status" class="mb-4 text-sm text-muted">Loading orders...</p>

		<div class="summary-grid">
			<article><span class="summary-label">All orders</span><strong>{{ orderStore.orders.length }}</strong><small>Across all channels</small></article>
			<article><span class="summary-label">Paid revenue</span><strong>{{ formatCurrency(paidRevenue) }}</strong><small>{{ paidOrders.length }} completed orders</small></article>
			<article><span class="summary-label">Average ticket</span><strong>{{ formatCurrency(averageOrder) }}</strong><small>Per paid order</small></article>
			<article><span class="summary-label">Refunded</span><strong>{{ formatCurrency(refundedRevenue) }}</strong><small>{{ orderStore.orders.filter((order) => order.status === 'refunded').length }} refunded orders</small></article>
		</div>

		<section class="orders-panel">
			<div class="filter-bar">
				<label class="search-box"><span aria-hidden="true">/</span><input v-model="search" type="search" placeholder="Search order, customer or table" @input="resetPage" /><kbd>Ctrl K</kbd></label>
				<select v-model="period" aria-label="Filter by period" @change="resetPage"><option value="all">All time</option><option value="today">Today</option><option value="7">Last 7 days</option><option value="30">Last 30 days</option></select>
				<select v-model="status" aria-label="Filter by status" @change="resetPage"><option value="all">All statuses</option><option value="awaiting_payment">Awaiting payment</option><option value="paid">Paid</option><option value="refunded">Refunded</option></select>
				<select v-model="channel" aria-label="Filter by order channel" @change="resetPage"><option value="all">All channels</option><option>Dine in</option><option>Takeaway</option><option>Delivery</option></select>
				<BaseButton v-if="search || status !== 'all' || channel !== 'all' || period !== 'all'" variant="ghost" @click="clearFilters">Clear filters</BaseButton>
			</div>
			<div class="list-toolbar"><span><strong>{{ filteredOrders.length }}</strong> orders found</span><span class="toolbar-hint">Select an order to view its full receipt</span></div>

			<div v-if="pagedOrders.length" class="orders-table">
				<div class="order-row order-row--head"><span>Order</span><span>Customer</span><span>Channel</span><span>Payment</span><span>Total</span><span>Status</span><span></span></div>
				<button v-for="order in pagedOrders" :key="order.id" type="button" class="order-row order-row--button" @click="openOrder(order)"><span class="order-id"><strong>#{{ order.id }}</strong><small>{{ relativeTime(order.createdAt) }}</small></span><span><strong>{{ order.customer }}</strong><small v-if="order.table">{{ order.table }}</small></span><span>{{ order.type }}</span><span>{{ order.paymentMethod }}</span><strong>{{ formatCurrency(order.total) }}</strong><span class="status-pill" :class="`status-pill--${order.status}`">{{ order.status }}</span><span class="view-arrow" aria-hidden="true">-&gt;</span></button>
			</div>
			<div v-else class="empty-state"><span class="empty-icon">?</span><h2>No matching orders</h2><p>Try a different search or clear the filters to see your order history.</p><BaseButton variant="secondary" @click="clearFilters">Reset filters</BaseButton></div>

			<footer v-if="filteredOrders.length" class="pagination"><span>Showing {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, filteredOrders.length) }} of {{ filteredOrders.length }}</span><div><button type="button" aria-label="Previous page" :disabled="page === 1" @click="page--">&lt;</button><button v-for="number in pageCount" :key="number" type="button" :class="{ active: page === number }" @click="page = number">{{ number }}</button><button type="button" aria-label="Next page" :disabled="page === pageCount" @click="page++">&gt;</button></div></footer>
		</section>

		<BaseModal :open="Boolean(selectedOrder)"><aside v-if="selectedOrder" class="order-detail"><header><div><p class="eyebrow">Order detail</p><h2>#{{ selectedOrder.id }}</h2><p class="muted">{{ formatDate(selectedOrder.createdAt) }}</p></div><button type="button" class="close-button" aria-label="Close order details" @click="selectedOrder = null">&times;</button></header><div class="detail-status"><span class="status-pill" :class="`status-pill--${selectedOrder.status}`">{{ selectedOrder.status }}</span><span>{{ selectedOrder.type }}<span v-if="selectedOrder.table"> · {{ selectedOrder.table }}</span></span></div><div class="customer-block"><span class="avatar">{{ selectedOrder.customer.split(' ').map((part) => part[0]).join('').slice(0, 2) }}</span><div><strong>{{ selectedOrder.customer }}</strong><small>Customer</small></div></div><div class="detail-items"><div v-for="item in selectedOrder.items" :key="item.name" class="detail-item"><span>{{ item.quantity }} x {{ item.name }}<small v-if="item.modifiers?.length" class="mt-1 block text-muted">{{ item.modifiers.map((modifier) => `${modifier.group}: ${modifier.name}`).join(', ') }}</small></span><strong>{{ formatCurrency(item.quantity * item.price) }}</strong></div></div><div class="detail-total"><span>Total paid</span><strong>{{ formatCurrency(selectedOrder.total) }}</strong></div><div class="payment-line"><span>Payment method</span><strong>{{ selectedOrder.paymentMethod }}</strong></div><footer><BaseButton variant="secondary" @click="printOrder">Print receipt</BaseButton><BaseButton v-if="selectedOrder.status === 'paid'" variant="danger" @click="requestRefund(selectedOrder)">Refund order</BaseButton></footer></aside></BaseModal>
		<BaseModal :open="Boolean(refundCandidate)"><div v-if="refundCandidate" class="confirm-dialog"><p class="eyebrow">Financial action</p><h2>Refund order #{{ refundCandidate.id }}?</h2><p class="muted">This will mark {{ formatCurrency(refundCandidate.total) }} as refunded. The action will be visible in your order history.</p><footer><BaseButton variant="secondary" @click="refundCandidate = null">Keep order</BaseButton><BaseButton variant="danger" @click="refundOrder">Confirm refund</BaseButton></footer></div></BaseModal>
	</section>
</template>

<style scoped>
.orders-page { min-height: 100vh; padding: 2rem clamp(1.25rem, 3vw, 3rem); color: var(--color-ink); }
.orders-header, .header-actions, .filter-bar, .list-toolbar, .pagination, .order-detail header, .detail-status, .customer-block, .detail-item, .detail-total, .payment-line { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.orders-header { align-items: flex-end; margin-bottom: 2rem; }.eyebrow, .summary-label { margin: 0; color: var(--color-brand); font-size: .68rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }h1 { margin: .4rem 0; font-size: clamp(1.8rem, 3vw, 2.45rem); letter-spacing: -.04em; }.muted { color: var(--color-muted); font-size: .8rem; line-height: 1.5; }.header-actions { flex-wrap: wrap; justify-content: flex-end; }.register-status { display: inline-flex; align-items: center; gap: .5rem; color: var(--color-success); font-size: .75rem; font-weight: 700; }.register-status i { width: .45rem; height: .45rem; border-radius: 50%; background: var(--color-success); }.primary-action { display: inline-flex; align-items: center; gap: .6rem; min-height: 2.5rem; border-radius: var(--radius-sm); background: var(--color-brand); padding: 0 .9rem; color: white; font-size: .8rem; font-weight: 700; text-decoration: none; }
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }.summary-grid article { display: grid; gap: .55rem; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); padding: 1.1rem 1.25rem; box-shadow: var(--shadow-sm); }.summary-grid strong { font-size: 1.55rem; letter-spacing: -.03em; }.summary-grid small { color: var(--color-muted); font-size: .72rem; }
.orders-panel { margin-top: 1.25rem; overflow: hidden; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); box-shadow: var(--shadow-sm); }.filter-bar { flex-wrap: wrap; padding: 1rem; border-bottom: 1px solid var(--color-border); }.search-box { display: flex; align-items: center; flex: 1 1 18rem; gap: .6rem; min-height: 2.5rem; border: 1px solid var(--color-border); border-radius: var(--radius-sm); padding: 0 .75rem; color: var(--color-brand); }.search-box input { min-width: 0; flex: 1; border: 0; outline: 0; color: var(--color-ink); font-size: .8rem; }.search-box kbd { color: var(--color-muted); font-size: .65rem; }.filter-bar select { min-height: 2.5rem; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-surface); padding: 0 .7rem; color: var(--color-ink); font-size: .78rem; }.list-toolbar { padding: 1rem; color: var(--color-muted); font-size: .75rem; }.list-toolbar strong { color: var(--color-ink); }.toolbar-hint { font-size: .7rem; }
.orders-table { overflow-x: auto; }.order-row { display: grid; grid-template-columns: 1fr 1.35fr 1fr 1fr .8fr .8fr 1rem; align-items: center; gap: 1rem; width: 100%; min-width: 52rem; border-top: 1px solid var(--color-border); padding: 1rem; font-size: .78rem; text-align: left; }.order-row--head { border-top: 0; padding-top: 0; color: var(--color-muted); font-size: .65rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }.order-row--button { border-right: 0; border-bottom: 0; border-left: 0; background: var(--color-surface); color: var(--color-ink); cursor: pointer; transition: background .15s ease; }.order-row--button:hover, .order-row--button:focus-visible { background: #fff7ed; outline: 0; }.order-row span, .order-row strong { display: grid; gap: .25rem; }.order-row small { color: var(--color-muted); font-size: .68rem; font-weight: 400; }.order-id strong { color: var(--color-brand-dark); }.view-arrow { color: var(--color-brand); font-size: 1rem; }.status-pill { width: fit-content; border-radius: 99px; padding: .3rem .55rem; font-size: .65rem; font-weight: 800; text-transform: capitalize; }.status-pill--paid { background: #f0fdf4; color: var(--color-success); }.status-pill--refunded { background: #fef2f2; color: var(--color-danger); }
.pagination { border-top: 1px solid var(--color-border); padding: .9rem 1rem; color: var(--color-muted); font-size: .72rem; }.pagination div { display: flex; gap: .3rem; }.pagination button { min-width: 2rem; height: 2rem; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-surface); color: var(--color-muted); cursor: pointer; }.pagination button.active { border-color: var(--color-brand); background: var(--color-brand); color: white; }.pagination button:disabled { cursor: not-allowed; opacity: .4; }
.empty-state { display: grid; justify-items: center; gap: .5rem; border-top: 1px solid var(--color-border); padding: 4rem 1rem; text-align: center; }.empty-icon { display: grid; width: 2.5rem; height: 2.5rem; place-items: center; border-radius: 50%; background: #fff7ed; color: var(--color-brand); font-weight: 800; }.empty-state h2 { margin: .5rem 0 0; }.empty-state p { margin: 0 0 1rem; }
.order-detail, .confirm-dialog { width: min(100%, 30rem); border-radius: var(--radius-md); background: var(--color-surface); padding: 1.5rem; box-shadow: 0 20px 50px rgb(15 23 42 / 20%); }.order-detail h2, .confirm-dialog h2 { margin: .35rem 0; font-size: 1.45rem; }.close-button { border: 0; background: transparent; color: var(--color-muted); font-size: 1.5rem; cursor: pointer; }.detail-status { margin: 1.25rem 0; border-block: 1px solid var(--color-border); padding: .85rem 0; color: var(--color-muted); font-size: .75rem; }.customer-block { justify-content: flex-start; margin-bottom: 1.25rem; }.avatar { display: grid; width: 2.5rem; height: 2.5rem; place-items: center; border-radius: 50%; background: #ffedd5; color: var(--color-brand-dark); font-size: .75rem; font-weight: 800; }.customer-block div { display: grid; gap: .2rem; }.customer-block small { color: var(--color-muted); font-size: .7rem; }.detail-items { display: grid; gap: .75rem; border-block: 1px dashed var(--color-border); padding: 1rem 0; }.detail-item { font-size: .8rem; }.detail-total { margin-top: 1rem; font-size: .9rem; }.detail-total strong { color: var(--color-brand-dark); font-size: 1.2rem; }.payment-line { margin-top: .7rem; color: var(--color-muted); font-size: .75rem; }.payment-line strong { color: var(--color-ink); }.order-detail footer, .confirm-dialog footer { display: flex; justify-content: flex-end; gap: .5rem; margin-top: 1.5rem; }
@media print { .orders-page > *:not(.orders-panel), .filter-bar, .list-toolbar, .pagination { display: none; }.orders-panel { border: 0; box-shadow: none; } }
@media (max-width: 800px) { .summary-grid { grid-template-columns: repeat(2, 1fr); }.orders-header { display: block; }.header-actions { justify-content: flex-start; margin-top: 1rem; } }
@media (max-width: 560px) { .orders-page { padding: 1.25rem; }.summary-grid { gap: .65rem; }.summary-grid article { padding: .9rem; }.summary-grid strong { font-size: 1.2rem; }.toolbar-hint { display: none; }.filter-bar { align-items: stretch; }.filter-bar select, .filter-bar .search-box { flex: 1 1 100%; }.pagination { align-items: flex-start; flex-direction: column; } }
</style>
