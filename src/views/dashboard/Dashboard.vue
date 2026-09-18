<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useCustomerStore } from '../../stores/customer.js'
import { useOrderStore } from '../../stores/order.js'
import { useProductStore } from '../../stores/product.js'
import { useTableStore } from '../../stores/table.js'

const customerStore = useCustomerStore()
const orderStore = useOrderStore()
const productStore = useProductStore()
const tableStore = useTableStore()
const range = ref('today')
const ranges = { today: 1, week: 7, month: 30 }

const formatCurrency = (value) => `$${Number(value).toFixed(2)}`
const rangeLabel = computed(() => ({ today: 'Today', week: 'Last 7 days', month: 'Last 30 days' }[range.value]))
const startDate = computed(() => Date.now() - ranges[range.value] * 24 * 60 * 60 * 1000)
const periodOrders = computed(() => orderStore.paidOrders.filter((order) => new Date(order.createdAt).getTime() >= startDate.value))
const previousOrders = computed(() => orderStore.paidOrders.filter((order) => {
  const created = new Date(order.createdAt).getTime()
  return created < startDate.value && created >= startDate.value - ranges[range.value] * 24 * 60 * 60 * 1000
}))
const revenue = computed(() => periodOrders.value.reduce((sum, order) => sum + order.total, 0))
const previousRevenue = computed(() => previousOrders.value.reduce((sum, order) => sum + order.total, 0))
const revenueChange = computed(() => previousRevenue.value ? ((revenue.value - previousRevenue.value) / previousRevenue.value) * 100 : 0)
const averageOrder = computed(() => periodOrders.value.length ? revenue.value / periodOrders.value.length : 0)
const topProducts = computed(() => {
  const totals = new Map()
  periodOrders.value.forEach((order) => order.items.forEach((item) => totals.set(item.name, (totals.get(item.name) || 0) + item.quantity)))
  return [...totals.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4).map(([name, quantity]) => ({ name, quantity, product: productStore.items.find((item) => item.name === name) }))
})
const maxProductQuantity = computed(() => Math.max(...topProducts.value.map((item) => item.quantity), 1))
const salesByDay = computed(() => {
  const days = range.value === 'today' ? 7 : ranges[range.value]
  return Array.from({ length: Math.min(days, 7) }, (_, index) => {
    const date = new Date(Date.now() - (Math.min(days, 7) - index - 1) * 24 * 60 * 60 * 1000)
    const key = date.toDateString()
    const total = periodOrders.value.filter((order) => new Date(order.createdAt).toDateString() === key).reduce((sum, order) => sum + order.total, 0)
    return { label: date.toLocaleDateString('en-US', { weekday: 'short' }), total }
  })
})
const chartMax = computed(() => Math.max(...salesByDay.value.map((day) => day.total), 1))
const lowStockProducts = computed(() => productStore.items.filter((product) => product.status === 'inactive'))
const occupiedTables = computed(() => tableStore.items.filter((table) => table.status === 'occupied').length)
const recentOrders = computed(() => orderStore.orders.slice(0, 5))
const relativeTime = (date) => {
  const minutes = Math.max(1, Math.round((Date.now() - new Date(date).getTime()) / 60000))
  return minutes < 60 ? `${minutes} min ago` : `${Math.round(minutes / 60)} hr ago`
}
</script>

<template>
  <section class="dashboard-page">
    <header class="dashboard-header">
      <div><p class="eyebrow">Operations overview</p><h1>Good morning, Alex</h1><p class="muted">Here is what is happening across your restaurant.</p></div>
      <div class="header-actions"><label class="range-control"><span class="sr-only">Sales period</span><select v-model="range"><option value="today">Today</option><option value="week">Last 7 days</option><option value="month">Last 30 days</option></select></label><RouterLink class="primary-action" to="/pos">Open register <span aria-hidden="true">-&gt;</span></RouterLink></div>
    </header>

    <div class="metric-grid">
      <article class="metric-card metric-card--accent"><span class="metric-label">Net sales</span><strong>{{ formatCurrency(revenue) }}</strong><span :class="revenueChange >= 0 ? 'trend trend--up' : 'trend trend--down'">{{ revenueChange >= 0 ? '+' : '' }}{{ revenueChange.toFixed(1) }}% vs previous period</span></article>
      <article class="metric-card"><span class="metric-label">Orders</span><strong>{{ periodOrders.length }}</strong><span class="metric-note">{{ periodOrders.filter((order) => order.type === 'Dine in').length }} dine-in orders</span></article>
      <article class="metric-card"><span class="metric-label">Average order</span><strong>{{ formatCurrency(averageOrder) }}</strong><span class="metric-note">Across paid orders</span></article>
      <article class="metric-card"><span class="metric-label">Tables occupied</span><strong>{{ occupiedTables }}<small> / {{ tableStore.items.length }}</small></strong><RouterLink class="metric-link" to="/tables">View floor plan</RouterLink></article>
    </div>

    <div v-if="lowStockProducts.length" class="alert-bar"><strong>Inventory attention</strong><span>{{ lowStockProducts.length }} menu item{{ lowStockProducts.length === 1 ? '' : 's' }} marked inactive.</span><RouterLink to="/inventory">Review inventory -&gt;</RouterLink></div>

    <div class="dashboard-grid">
      <section class="panel sales-panel"><div class="panel-heading"><div><p class="eyebrow">{{ rangeLabel }}</p><h2>Sales performance</h2></div><RouterLink to="/reports">Full report -&gt;</RouterLink></div><div class="chart" role="img" :aria-label="`Sales chart for ${rangeLabel}`"><div v-for="day in salesByDay" :key="day.label" class="chart-column"><span class="chart-value">{{ formatCurrency(day.total) }}</span><div class="chart-track"><div class="chart-bar" :style="{ height: `${Math.max((day.total / chartMax) * 100, day.total ? 8 : 2)}%` }"></div></div><span class="chart-label">{{ day.label }}</span></div></div></section>
      <section class="panel"><div class="panel-heading"><div><p class="eyebrow">Menu mix</p><h2>Top products</h2></div><RouterLink to="/menu/products">Manage menu -&gt;</RouterLink></div><ul class="product-list"><li v-for="item in topProducts" :key="item.name"><div class="product-line"><span>{{ item.name }}</span><strong>{{ item.quantity }} sold</strong></div><div class="progress-track"><div class="progress-fill" :style="{ width: `${(item.quantity / maxProductQuantity) * 100}%` }"></div></div></li><li v-if="!topProducts.length" class="muted">No sales in this period.</li></ul></section>
    </div>

    <section class="panel recent-panel"><div class="panel-heading"><div><p class="eyebrow">Live activity</p><h2>Recent orders</h2></div><RouterLink to="/orders">View all orders -&gt;</RouterLink></div><div class="orders-table"><div class="order-row order-row--head"><span>Order</span><span>Customer</span><span>Type</span><span>Total</span><span>Status</span></div><div v-for="order in recentOrders" :key="order.id" class="order-row"><strong>#{{ order.id }}</strong><span>{{ order.customer }}</span><span>{{ order.type }}<small v-if="order.table"> · {{ order.table }}</small></span><strong>{{ formatCurrency(order.total) }}</strong><span class="status-pill" :class="`status-pill--${order.status}`">{{ order.status }} · {{ relativeTime(order.createdAt) }}</span></div></div></section>
    <p class="dashboard-footnote">Last updated just now · {{ customerStore.items.length }} customers on file</p>
  </section>
</template>

<style scoped>
.dashboard-page { min-height: 100vh; padding: 2rem clamp(1.25rem, 3vw, 3rem); color: var(--color-ink); }
.dashboard-header, .panel-heading, .header-actions, .product-line { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.dashboard-header { margin-bottom: 2rem; align-items: flex-end; }
h1 { margin: .35rem 0 .45rem; font-size: clamp(1.75rem, 3vw, 2.4rem); letter-spacing: -.04em; }
h2 { margin: .25rem 0 0; font-size: 1.05rem; }
.eyebrow, .metric-label { margin: 0; color: var(--color-brand); font-size: .68rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
.muted, .metric-note, .dashboard-footnote { color: var(--color-muted); font-size: .8rem; }
.header-actions { flex-wrap: wrap; justify-content: flex-end; }
.range-control select, .primary-action { min-height: 2.5rem; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-surface); padding: 0 .9rem; color: var(--color-ink); font-size: .8rem; font-weight: 700; }
.primary-action { display: inline-flex; align-items: center; gap: .65rem; border-color: var(--color-brand); background: var(--color-brand); color: white; text-decoration: none; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }
.metric-card, .panel { border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); box-shadow: var(--shadow-sm); }
.metric-card { display: grid; gap: .65rem; padding: 1.25rem; }
.metric-card strong { font-size: 1.8rem; letter-spacing: -.04em; }
.metric-card small { color: var(--color-muted); font-size: .9rem; font-weight: 500; }
.metric-card--accent { border-top: 3px solid var(--color-brand); }
.trend, .metric-link, .panel-heading a, .alert-bar a { font-size: .72rem; font-weight: 700; text-decoration: none; }
.trend--up { color: var(--color-success); }.trend--down { color: var(--color-danger); }.metric-link, .panel-heading a, .alert-bar a { color: var(--color-brand); }
.alert-bar { display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; margin: 1rem 0; border: 1px solid #fed7aa; border-left: 3px solid var(--color-brand); border-radius: var(--radius-sm); background: #fff7ed; padding: .85rem 1rem; font-size: .8rem; }
.alert-bar a { margin-left: auto; }
.dashboard-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(18rem, 1fr); gap: 1rem; margin-top: 1rem; }
.panel { padding: 1.25rem; }.chart { display: grid; grid-template-columns: repeat(7, 1fr); align-items: end; gap: .65rem; height: 15rem; margin-top: 1.5rem; border-bottom: 1px solid var(--color-border); }
.chart-column { display: grid; grid-template-rows: 1.2rem 1fr 1.2rem; align-items: end; gap: .4rem; height: 100%; text-align: center; }.chart-value, .chart-label { color: var(--color-muted); font-size: .62rem; }.chart-value { min-height: 1rem; }.chart-track { display: flex; height: 100%; align-items: end; justify-content: center; }.chart-bar { width: min(2.2rem, 70%); min-height: 2px; border-radius: 4px 4px 0 0; background: var(--color-brand); transition: height .25s ease; }
.product-list { display: grid; gap: 1.15rem; margin: 1.75rem 0 0; padding: 0; list-style: none; }.product-line { font-size: .8rem; }.product-line strong { color: var(--color-muted); font-size: .72rem; }.progress-track { height: .4rem; margin-top: .55rem; overflow: hidden; border-radius: 99px; background: #f1f5f9; }.progress-fill { height: 100%; border-radius: inherit; background: var(--color-brand); }
.recent-panel { margin-top: 1rem; }.orders-table { margin-top: 1rem; }.order-row { display: grid; grid-template-columns: .7fr 1.4fr 1.1fr .7fr 1.2fr; align-items: center; gap: 1rem; border-top: 1px solid var(--color-border); padding: .9rem 0; font-size: .78rem; }.order-row small { color: var(--color-muted); }.order-row--head { border-top: 0; padding-top: 0; color: var(--color-muted); font-size: .65rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }.status-pill { width: fit-content; border-radius: 99px; padding: .3rem .55rem; font-size: .65rem; font-weight: 700; }.status-pill--paid { background: #f0fdf4; color: var(--color-success); }.status-pill--refunded { background: #fef2f2; color: var(--color-danger); }.dashboard-footnote { margin: 1rem 0 0; text-align: right; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); }
@media (max-width: 900px) { .metric-grid { grid-template-columns: repeat(2, 1fr); }.dashboard-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) { .dashboard-page { padding: 1.25rem; }.dashboard-header { display: block; }.header-actions { justify-content: flex-start; margin-top: 1rem; }.metric-grid { grid-template-columns: 1fr 1fr; gap: .65rem; }.metric-card { padding: .9rem; }.metric-card strong { font-size: 1.35rem; }.order-row { grid-template-columns: 1fr auto; gap: .35rem .75rem; }.order-row--head, .order-row span:nth-child(2), .order-row span:nth-child(3), .order-row strong:nth-child(4) { display: none; }.status-pill { justify-self: end; }.chart { gap: .25rem; } }
</style>
