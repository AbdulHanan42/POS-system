<script setup>
import { computed, onMounted, ref } from 'vue'
import { Download, RefreshCw } from 'lucide-vue-next'
import { reportService } from '../../services/reportService.js'

const ranges = [
	{ value: 'today', label: 'Today' },
	{ value: 'week', label: '7 days' },
	{ value: 'month', label: '30 days' },
	{ value: 'custom', label: 'Custom' },
]
const range = ref('week')
const startDate = ref('')
const endDate = ref('')
const report = ref(null)
const loading = ref(false)
const error = ref('')

const maxDailySales = computed(() => Math.max(1, ...((report.value?.salesByDay || []).map((day) => day.sales))))
const maxProductSales = computed(() => Math.max(1, ...((report.value?.topProducts || []).map((product) => product.sales))))
const dateLabel = computed(() => {
	if (!report.value) return ''
	const format = (value) => new Date(`${value}T00:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
	return report.value.startDate === report.value.endDate
		? format(report.value.startDate)
		: `${format(report.value.startDate)} - ${format(report.value.endDate)}`
})
const summaries = computed(() => {
	if (!report.value) return []
	const data = report.value.summary
	return [
		{ label: 'Gross sales', value: formatCurrency(data.grossSales), detail: `${data.orderCount} paid orders`, tone: 'text-ink' },
		{ label: 'Net sales', value: formatCurrency(data.netSales), detail: `${data.refundCount} refunds`, tone: 'text-success' },
		{ label: 'Refunds', value: formatCurrency(data.refunds), detail: `${data.refundCount} refunded orders`, tone: 'text-danger' },
		{ label: 'Average order', value: formatCurrency(data.averageOrder), detail: `${formatCurrency(data.discounts)} discounts`, tone: 'text-brand-dark' },
	]
})

function formatCurrency(value) {
	return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(Number(value || 0))
}

async function loadReport() {
	if (range.value === 'custom' && (!startDate.value || !endDate.value)) {
		error.value = 'Choose both a start date and an end date.'
		return
	}
	loading.value = true
	error.value = ''
	const params = new URLSearchParams({ range: range.value })
	if (range.value === 'custom') {
		params.set('startDate', startDate.value)
		params.set('endDate', endDate.value)
	}
	try {
		report.value = await reportService.sales(`?${params.toString()}`)
	} catch (requestError) {
		error.value = requestError.message || 'Could not load the sales report.'
	} finally {
		loading.value = false
	}
}

function selectRange(value) {
	range.value = value
	if (value !== 'custom') loadReport()
}

function exportCsv() {
	if (!report.value?.recentOrders.length) return
	const columns = ['Order', 'Date', 'Customer', 'Channel', 'Payment method', 'Status', 'Total']
	const rows = report.value.recentOrders.map((order) => [
		order.id,
		new Date(order.createdAt).toISOString(),
		order.customer,
		order.type,
		order.paymentMethod,
		order.status,
		Number(order.total).toFixed(2),
	])
	const csv = [columns, ...rows].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\r\n')
	const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
	const link = document.createElement('a')
	link.href = url
	link.download = `sales-report-${report.value.startDate}-to-${report.value.endDate}.csv`
	link.click()
	URL.revokeObjectURL(url)
}

onMounted(loadReport)
</script>

<template>
	<section class="min-h-screen min-w-0 bg-background px-5 py-7 sm:px-8 lg:px-10">
		<div class="mx-auto max-w-7xl">
			<header class="flex flex-col justify-between gap-5 border-b border-border pb-6 lg:flex-row lg:items-end">
				<div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Performance</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Sales report</h1><p class="mt-2 text-sm text-muted">{{ dateLabel || 'Review sales activity' }}</p></div>
				<div class="flex flex-col gap-2 sm:flex-row">
					<button type="button" class="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm border border-border bg-surface px-4 text-sm font-semibold text-ink hover:bg-background disabled:opacity-50" :disabled="loading || !report?.recentOrders.length" @click="exportCsv"><Download :size="16" aria-hidden="true" />Export CSV</button>
					<button type="button" class="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="loading" @click="loadReport"><RefreshCw :size="16" aria-hidden="true" :class="loading ? 'animate-spin' : ''" />Refresh</button>
				</div>
			</header>

			<div class="mt-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
				<div class="flex gap-1 overflow-x-auto" aria-label="Report date range"><button v-for="option in ranges" :key="option.value" type="button" class="shrink-0 rounded-sm px-3 py-2 text-sm font-semibold" :class="range === option.value ? 'bg-ink text-white' : 'text-muted hover:bg-surface hover:text-ink'" :aria-pressed="range === option.value" @click="selectRange(option.value)">{{ option.label }}</button></div>
				<form v-if="range === 'custom'" class="flex flex-col gap-2 sm:flex-row" @submit.prevent="loadReport"><label class="sr-only" for="report-start">Start date</label><input id="report-start" v-model="startDate" required type="date" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand" /><span class="hidden self-center text-muted sm:block">to</span><label class="sr-only" for="report-end">End date</label><input id="report-end" v-model="endDate" required type="date" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand" /><button type="submit" class="min-h-10 rounded-sm border border-border bg-surface px-4 text-sm font-semibold text-ink hover:bg-background">Apply</button></form>
			</div>

			<p v-if="error" role="alert" class="mt-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger">{{ error }}</p>
			<div v-if="loading && !report" role="status" class="py-16 text-center text-sm text-muted">Loading sales report...</div>

			<template v-if="report">
				<p v-if="loading" role="status" class="mt-3 text-xs text-muted">Updating report...</p>
				<div class="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
					<article v-for="summary in summaries" :key="summary.label" class="rounded-md border border-border bg-surface px-4 py-4 shadow-sm"><span class="text-sm font-medium text-muted">{{ summary.label }}</span><strong class="mt-2 block text-2xl" :class="summary.tone">{{ summary.value }}</strong><small class="mt-1 block text-xs text-muted">{{ summary.detail }}</small></article>
				</div>

				<div class="mt-7 grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(18rem,1fr)]">
					<section class="min-w-0 border-b border-border pb-6 xl:border-b-0" aria-labelledby="daily-sales-title">
						<div class="flex items-end justify-between gap-3"><div><h2 id="daily-sales-title" class="text-lg font-bold text-ink">Daily sales</h2><p class="mt-1 text-sm text-muted">{{ dateLabel }} · refunds shown separately</p></div><strong class="text-sm text-ink">{{ formatCurrency(report.summary.grossSales) }}</strong></div>
						<div class="mt-5 grid min-h-52 grid-cols-[repeat(auto-fit,minmax(2.3rem,1fr))] items-end gap-2 border-b border-border pb-2" role="img" :aria-label="`Daily sales chart for ${dateLabel}`">
							<div v-for="day in report.salesByDay" :key="day.date" class="flex h-full min-w-0 flex-col items-center justify-end gap-2"><span class="max-w-full truncate text-[10px] font-medium text-muted">{{ day.sales ? formatCurrency(day.sales) : '' }}</span><div class="flex h-36 w-full items-end justify-center"><div class="w-full max-w-10 rounded-t-sm bg-brand" :style="{ height: `${Math.max(day.sales ? 7 : 0, day.sales / maxDailySales * 100)}%` }" :title="`${day.label}: ${formatCurrency(day.sales)} sales`"></div></div><span class="text-[10px] font-semibold text-muted">{{ day.label }}</span></div>
						</div>
					</section>

					<section aria-labelledby="payment-mix-title"><h2 id="payment-mix-title" class="text-lg font-bold text-ink">Payment methods</h2><p class="mt-1 text-sm text-muted">Paid orders by tender</p><div v-if="report.paymentMethods.length" class="mt-4 grid gap-4"><div v-for="method in report.paymentMethods" :key="method.name"><div class="flex justify-between gap-3 text-sm"><strong class="text-ink">{{ method.name }}</strong><span class="text-muted">{{ method.orderCount }} orders · {{ formatCurrency(method.sales) }}</span></div><div class="mt-2 h-2 overflow-hidden rounded-sm bg-background"><div class="h-full rounded-sm bg-success" :style="{ width: `${report.summary.grossSales ? method.sales / report.summary.grossSales * 100 : 0}%` }"></div></div></div></div><p v-else class="mt-5 text-sm text-muted">No paid orders in this period.</p>
						<div class="mt-6 border-t border-border pt-4"><h3 class="text-sm font-bold text-ink">Order channels</h3><div v-if="report.orderTypes.length" class="mt-3 grid gap-2"><div v-for="type in report.orderTypes" :key="type.name" class="flex justify-between gap-3 text-sm"><span class="text-muted">{{ type.name }} · {{ type.orderCount }}</span><strong class="text-ink">{{ formatCurrency(type.sales) }}</strong></div></div><p v-else class="mt-2 text-sm text-muted">No channel data yet.</p></div>
					</section>
				</div>

				<section class="mt-7 border-t border-border pt-6" aria-labelledby="top-products-title"><div><h2 id="top-products-title" class="text-lg font-bold text-ink">Top products</h2><p class="mt-1 text-sm text-muted">Ranked by quantity sold</p></div><div v-if="report.topProducts.length" class="mt-4 overflow-x-auto"><table class="w-full min-w-[520px] border-collapse text-left"><thead><tr class="border-b border-border text-xs font-bold uppercase tracking-wide text-muted"><th class="py-3 pr-4">Product</th><th class="px-3 py-3">Units</th><th class="px-3 py-3">Sales</th><th class="px-3 py-3">Mix</th></tr></thead><tbody><tr v-for="product in report.topProducts" :key="product.name" class="border-b border-border"><td class="py-3 pr-4 text-sm font-semibold text-ink">{{ product.name }}</td><td class="px-3 py-3 text-sm text-muted">{{ product.quantity }}</td><td class="px-3 py-3 text-sm font-semibold text-ink">{{ formatCurrency(product.sales) }}</td><td class="px-3 py-3"><div class="h-2 w-full max-w-40 rounded-sm bg-background"><div class="h-full rounded-sm bg-brand" :style="{ width: `${product.sales / maxProductSales * 100}%` }"></div></div></td></tr></tbody></table></div><p v-else class="py-8 text-sm text-muted">No product sales in this period.</p></section>

				<section class="mt-7 border-t border-border pt-6" aria-labelledby="transactions-title"><div class="flex flex-col justify-between gap-2 sm:flex-row sm:items-end"><div><h2 id="transactions-title" class="text-lg font-bold text-ink">Recent transactions</h2><p class="mt-1 text-sm text-muted">Latest {{ report.recentOrders.length }} paid and refunded orders in this period</p></div></div><div v-if="report.recentOrders.length" class="mt-4 overflow-x-auto"><table class="w-full min-w-[740px] border-collapse text-left"><thead><tr class="border-b border-border text-xs font-bold uppercase tracking-wide text-muted"><th class="py-3 pr-4">Order</th><th class="px-3 py-3">Date</th><th class="px-3 py-3">Customer</th><th class="px-3 py-3">Channel</th><th class="px-3 py-3">Payment</th><th class="px-3 py-3">Status</th><th class="py-3 pl-3 text-right">Total</th></tr></thead><tbody><tr v-for="order in report.recentOrders" :key="order.id" class="border-b border-border"><td class="py-3 pr-4 text-sm font-semibold text-ink">#{{ order.id }}</td><td class="px-3 py-3 text-xs text-muted">{{ new Date(order.createdAt).toLocaleString() }}</td><td class="px-3 py-3 text-sm text-ink">{{ order.customer }}</td><td class="px-3 py-3 text-sm text-muted">{{ order.type }}</td><td class="px-3 py-3 text-sm text-muted">{{ order.paymentMethod }}</td><td class="px-3 py-3"><span class="rounded-sm px-2 py-1 text-xs font-bold capitalize" :class="order.status === 'paid' ? 'bg-success/10 text-success' : 'bg-red-50 text-danger'">{{ order.status }}</span></td><td class="py-3 pl-3 text-right text-sm font-semibold text-ink">{{ formatCurrency(order.total) }}</td></tr></tbody></table></div><p v-else class="py-8 text-sm text-muted">No completed transactions for this period.</p></section>
			</template>
		</div>
	</section>
</template>
