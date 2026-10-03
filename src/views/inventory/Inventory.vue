<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowDownToLine, ArrowUpFromLine, History, Search, SlidersHorizontal, X } from 'lucide-vue-next'
import { useInventoryStore } from '../../stores/inventory.js'

const inventoryStore = useInventoryStore()
const search = ref('')
const categoryFilter = ref('all')
const stockFilter = ref('all')
const historyProductId = ref('')
const adjustmentProduct = ref(null)
const reorderProduct = ref(null)
const actionError = ref('')
const saving = ref(false)
const adjustment = ref({ movementType: 'stock_in', quantity: 1, reason: '' })
const reorderLevel = ref(5)

const filters = [
  { value: 'all', label: 'All stock' },
  { value: 'in_stock', label: 'In stock' },
  { value: 'low_stock', label: 'Low stock' },
  { value: 'out_of_stock', label: 'Out of stock' },
]
const categories = computed(() => [...new Set(inventoryStore.items.map((item) => item.category))].sort())
const visibleItems = computed(() => {
  const query = search.value.trim().toLowerCase()
  return inventoryStore.items.filter((item) => {
    const matchesQuery = `${item.name} ${item.category}`.toLowerCase().includes(query)
    const matchesCategory = categoryFilter.value === 'all' || item.category === categoryFilter.value
    const matchesStock = stockFilter.value === 'all' || item.status === stockFilter.value
    return matchesQuery && matchesCategory && matchesStock
  })
})
const lowCount = computed(() => inventoryStore.lowStockItems.length)
const outCount = computed(() => inventoryStore.outOfStockItems.length)
const formatCurrency = (value) => `$${Number(value).toFixed(2)}`

onMounted(() => {
  inventoryStore.load().catch(() => undefined)
  inventoryStore.loadMovements().catch(() => undefined)
})

function statusLabel(status) {
  return { in_stock: 'In stock', low_stock: 'Low stock', out_of_stock: 'Out of stock' }[status]
}

function statusClasses(status) {
  return {
    in_stock: 'bg-success/10 text-success',
    low_stock: 'bg-brand/10 text-brand-dark',
    out_of_stock: 'bg-background text-danger',
  }[status]
}

function openAdjustment(item, movementType) {
  adjustmentProduct.value = item
  adjustment.value = { movementType, quantity: 1, reason: '' }
  actionError.value = ''
}

async function saveAdjustment() {
  if (adjustment.value.movementType === 'stock_out' && adjustment.value.quantity > adjustmentProduct.value.quantity) {
    actionError.value = `Only ${adjustmentProduct.value.quantity} units are currently in stock.`
    return
  }
  saving.value = true
  actionError.value = ''
  try {
    await inventoryStore.adjust({
      productId: adjustmentProduct.value.productId,
      movementType: adjustment.value.movementType,
      quantity: Number(adjustment.value.quantity),
      reason: adjustment.value.reason.trim(),
    })
    adjustmentProduct.value = null
    await inventoryStore.loadMovements(historyProductId.value || undefined)
  } catch (error) {
    actionError.value = error.message
  } finally {
    saving.value = false
  }
}

function openReorder(item) {
  reorderProduct.value = item
  reorderLevel.value = item.reorderLevel
  actionError.value = ''
}

async function saveReorderLevel() {
  saving.value = true
  actionError.value = ''
  try {
    await inventoryStore.updateReorderLevel(reorderProduct.value.productId, Number(reorderLevel.value))
    reorderProduct.value = null
  } catch (error) {
    actionError.value = error.message
  } finally {
    saving.value = false
  }
}

async function filterHistory() {
  const productId = historyProductId.value ? Number(historyProductId.value) : undefined
  await inventoryStore.loadMovements(productId).catch(() => undefined)
}

function movementLabel(type) {
  return { stock_in: 'Stock received', stock_out: 'Stock removed', sale: 'Sale', refund: 'Refund' }[type] || type
}

function movementClasses(type) {
  return ['stock_in', 'refund'].includes(type) ? 'text-success' : 'text-muted'
}

function formatDate(value) {
  return new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<template>
  <section class="min-h-screen min-w-0 bg-background px-5 py-7 sm:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <header class="flex flex-col justify-between gap-5 border-b border-border pb-6 lg:flex-row lg:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Operations</p>
          <h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Inventory</h1>
          <p class="mt-2 text-sm text-muted">Monitor stock, receive items, and review every adjustment.</p>
        </div>
        <a href="#inventory-history" class="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-sm border border-border bg-surface px-4 text-sm font-semibold text-ink hover:bg-background"><History :size="16" aria-hidden="true" /> Stock history</a>
      </header>

      <p v-if="inventoryStore.error" role="alert" class="mt-4 rounded-sm border border-border bg-background px-4 py-3 text-sm text-danger">{{ inventoryStore.error }}</p>
      <div class="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Tracked products</span><strong class="text-2xl text-ink">{{ inventoryStore.items.length }}</strong></article>
        <article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Low stock</span><strong class="text-2xl text-brand-dark">{{ lowCount }}</strong></article>
        <article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Out of stock</span><strong class="text-2xl text-danger">{{ outCount }}</strong></article>
        <article class="flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white shadow-sm"><span class="text-sm font-medium text-white/75">Stock value</span><strong class="text-xl">{{ formatCurrency(inventoryStore.totalStockValue) }}</strong></article>
      </div>

      <section class="mt-7" aria-labelledby="stock-heading">
        <div class="flex flex-col gap-4 border-b border-border pb-4 lg:flex-row lg:items-center lg:justify-between">
          <div><h2 id="stock-heading" class="text-lg font-bold text-ink">Stock levels</h2><p class="mt-1 text-sm text-muted">{{ visibleItems.length }} of {{ inventoryStore.items.length }} products</p></div>
          <div class="flex flex-col gap-2 sm:flex-row">
            <label class="relative block"><span class="sr-only">Search inventory</span><Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" /><input v-model="search" type="search" placeholder="Search products" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none focus:border-brand sm:w-56" /></label>
            <label><span class="sr-only">Filter by category</span><select v-model="categoryFilter" class="h-10 w-full rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand sm:w-44"><option value="all">All categories</option><option v-for="category in categories" :key="category" :value="category">{{ category }}</option></select></label>
          </div>
        </div>

        <div class="flex gap-1 overflow-x-auto border-b border-border py-3" aria-label="Filter stock status">
          <button v-for="filter in filters" :key="filter.value" type="button" class="shrink-0 rounded-sm px-3 py-2 text-sm font-semibold" :class="stockFilter === filter.value ? 'bg-ink text-white' : 'text-muted hover:bg-surface hover:text-ink'" :aria-pressed="stockFilter === filter.value" @click="stockFilter = filter.value">{{ filter.label }}<span v-if="filter.value === 'low_stock'" class="ml-1">{{ lowCount }}</span><span v-if="filter.value === 'out_of_stock'" class="ml-1">{{ outCount }}</span></button>
        </div>

        <div v-if="inventoryStore.loading" role="status" class="py-14 text-center text-sm text-muted">Loading inventory...</div>
        <div v-else-if="visibleItems.length" class="overflow-x-auto">
          <table class="w-full min-w-[760px] border-collapse text-left">
            <thead><tr class="border-b border-border text-xs font-bold uppercase tracking-wide text-muted"><th class="py-3 pr-4">Product</th><th class="px-3 py-3">Status</th><th class="px-3 py-3">On hand</th><th class="px-3 py-3">Reorder at</th><th class="px-3 py-3">Stock value</th><th class="py-3 pl-3 text-right">Actions</th></tr></thead>
            <tbody>
              <tr v-for="item in visibleItems" :key="item.productId" class="border-b border-border bg-surface/50 hover:bg-surface">
                <td class="py-4 pr-4"><div class="flex items-center gap-3"><img v-if="item.image" :src="item.image" :alt="''" class="size-11 rounded-sm border border-border object-cover" /><span v-else class="grid size-11 place-items-center rounded-sm bg-background text-xs font-bold text-brand">{{ item.name.slice(0, 2).toUpperCase() }}</span><span class="min-w-0"><strong class="block truncate text-sm text-ink">{{ item.name }}</strong><small class="mt-1 block text-xs text-muted">{{ item.category }} · {{ formatCurrency(item.unitPrice) }} each</small></span></div></td>
                <td class="px-3 py-4"><span class="rounded-sm px-2 py-1 text-xs font-bold" :class="statusClasses(item.status)">{{ statusLabel(item.status) }}</span></td>
                <td class="px-3 py-4"><strong class="text-sm text-ink">{{ item.quantity }}</strong><span class="ml-1 text-xs text-muted">units</span></td>
                <td class="px-3 py-4 text-sm text-muted">{{ item.reorderLevel }} units</td>
                <td class="px-3 py-4 text-sm font-semibold text-ink">{{ formatCurrency(item.stockValue) }}</td>
                <td class="py-4 pl-3"><div class="flex justify-end gap-1"><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-success" :aria-label="`Receive ${item.name}`" title="Receive stock" @click="openAdjustment(item, 'stock_in')"><ArrowDownToLine :size="16" aria-hidden="true" /></button><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-brand" :aria-label="`Remove ${item.name} stock`" title="Remove stock" @click="openAdjustment(item, 'stock_out')"><ArrowUpFromLine :size="16" aria-hidden="true" /></button><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-ink" :aria-label="`Set reorder level for ${item.name}`" title="Set reorder level" @click="openReorder(item)"><SlidersHorizontal :size="16" aria-hidden="true" /></button></div></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="py-14 text-center"><p class="font-semibold text-ink">{{ inventoryStore.items.length ? 'No matching stock items' : 'No products to track' }}</p><p class="mt-1 text-sm text-muted">{{ inventoryStore.items.length ? 'Try changing your search or filters.' : 'Products will appear here when they are added to the menu.' }}</p></div>
      </section>

      <section id="inventory-history" class="mt-10 border-t border-border pt-6" aria-labelledby="history-heading">
        <div class="flex flex-col justify-between gap-3 sm:flex-row sm:items-end"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Audit trail</p><h2 id="history-heading" class="mt-1 text-xl font-bold text-ink">Stock history</h2></div><label><span class="sr-only">Filter history by product</span><select v-model="historyProductId" class="h-10 w-full rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand sm:w-56" @change="filterHistory"><option value="">All products</option><option v-for="item in inventoryStore.items" :key="item.productId" :value="String(item.productId)">{{ item.name }}</option></select></label></div>
        <p v-if="inventoryStore.movementError" role="alert" class="mt-3 text-sm text-danger">{{ inventoryStore.movementError }}</p>
        <div v-if="inventoryStore.loadingMovements" role="status" class="py-8 text-center text-sm text-muted">Loading stock history...</div>
        <div v-else-if="inventoryStore.movements.length" class="mt-4 overflow-x-auto"><table class="w-full min-w-[620px] border-collapse text-left"><thead><tr class="border-b border-border text-xs font-bold uppercase tracking-wide text-muted"><th class="py-3 pr-4">Movement</th><th class="px-3 py-3">Product</th><th class="px-3 py-3">Quantity</th><th class="px-3 py-3">Reason</th><th class="py-3 pl-3 text-right">Date</th></tr></thead><tbody><tr v-for="movement in inventoryStore.movements" :key="movement.id" class="border-b border-border"><td class="py-3 pr-4 text-sm font-semibold" :class="movementClasses(movement.movementType)">{{ movementLabel(movement.movementType) }}</td><td class="px-3 py-3 text-sm text-ink">{{ movement.productName }}</td><td class="px-3 py-3 text-sm text-ink">{{ ['stock_in', 'refund'].includes(movement.movementType) ? '+' : '-' }}{{ movement.quantity }}</td><td class="px-3 py-3 text-sm text-muted">{{ movement.reason }}</td><td class="py-3 pl-3 text-right text-xs text-muted">{{ formatDate(movement.createdAt) }}</td></tr></tbody></table></div>
        <div v-else-if="!inventoryStore.loadingMovements" class="mt-4 rounded-sm border border-dashed border-border bg-surface px-4 py-8 text-center text-sm text-muted">No stock movements recorded yet.</div>
      </section>
    </div>

    <div v-if="adjustmentProduct" class="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="adjustment-title">
      <form class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl" @submit.prevent="saveAdjustment">
        <div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Stock adjustment</p><h2 id="adjustment-title" class="mt-1 text-xl font-bold text-ink">{{ adjustment.movementType === 'stock_in' ? 'Receive stock' : 'Remove stock' }}</h2><p class="mt-1 text-sm text-muted">{{ adjustmentProduct.name }} · {{ adjustmentProduct.quantity }} available</p></div><button type="button" class="grid size-8 place-items-center rounded-sm text-muted hover:bg-background" aria-label="Close adjustment" @click="adjustmentProduct = null"><X :size="18" aria-hidden="true" /></button></div>
        <label class="mt-5 grid gap-2 text-sm font-semibold text-ink">Quantity<input v-model.number="adjustment.quantity" required type="number" min="1" :max="adjustment.movementType === 'stock_out' ? adjustmentProduct.quantity : undefined" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
        <label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Reason<input v-model.trim="adjustment.reason" required maxlength="240" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" :placeholder="adjustment.movementType === 'stock_in' ? 'e.g. Supplier delivery' : 'e.g. Damaged goods'" /></label>
        <p v-if="actionError" role="alert" class="mt-3 text-sm text-danger">{{ actionError }}</p>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" :disabled="saving" @click="adjustmentProduct = null">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="saving">{{ saving ? 'Saving...' : 'Save adjustment' }}</button></div>
      </form>
    </div>

    <div v-if="reorderProduct" class="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="reorder-title">
      <form class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl" @submit.prevent="saveReorderLevel"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Low-stock alert</p><h2 id="reorder-title" class="mt-1 text-xl font-bold text-ink">Reorder level</h2><p class="mt-1 text-sm text-muted">{{ reorderProduct.name }} currently has {{ reorderProduct.quantity }} units.</p></div><label class="mt-5 grid gap-2 text-sm font-semibold text-ink">Alert when stock reaches<input v-model.number="reorderLevel" required type="number" min="0" max="100000" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label><p v-if="actionError" role="alert" class="mt-3 text-sm text-danger">{{ actionError }}</p><div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" :disabled="saving" @click="reorderProduct = null">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="saving">{{ saving ? 'Saving...' : 'Save level' }}</button></div></form>
    </div>
  </section>
</template>