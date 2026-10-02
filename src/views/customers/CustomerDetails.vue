<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseButton from '../../components/common/BaseButton.vue'
import ProductStatus from '../../components/products/ProductStatus.vue'
import { useCustomerStore } from '../../stores/customer.js'

const route = useRoute()
const router = useRouter()
const customerStore = useCustomerStore()
const customer = computed(() => customerStore.items.find((item) => item.id === Number(route.params.id)))
const formatCurrency = (value) => `Rs ${Number(value).toLocaleString('en-PK')}`
</script>

<template>
	<section class="min-h-screen bg-background px-6 py-8 lg:px-10"><div class="mx-auto max-w-4xl"><div class="mb-6 flex items-center justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Customer management</p><h1 class="mt-2 text-3xl font-bold text-ink">Customer details</h1></div><BaseButton variant="secondary" @click="router.push('/customers')">Back to customers</BaseButton></div><article v-if="customer" class="rounded-lg border border-border bg-surface p-6 shadow-sm"><div class="flex flex-col justify-between gap-4 border-b border-border pb-6 sm:flex-row sm:items-start"><div class="flex items-center gap-4"><span class="grid size-14 place-items-center rounded-full bg-orange-50 text-xl font-bold text-brand">{{ customer.name.charAt(0) }}</span><div><h2 class="text-2xl font-bold text-ink">{{ customer.name }}</h2><p class="mt-1 text-sm text-muted">{{ customer.phone }}<span v-if="customer.email"> · {{ customer.email }}</span></p></div></div><ProductStatus :status="customer.type === 'VIP' ? 'active' : 'inactive'" /></div><dl class="grid gap-5 border-b border-border py-6 sm:grid-cols-3"><div><dt class="text-xs text-muted">Total orders</dt><dd class="mt-1 text-xl font-bold text-ink">{{ customer.totalOrders }}</dd></div><div><dt class="text-xs text-muted">Total spent</dt><dd class="mt-1 text-xl font-bold text-ink">{{ formatCurrency(customer.totalSpent) }}</dd></div><div><dt class="text-xs text-muted">Last order</dt><dd class="mt-1 text-xl font-bold text-ink">{{ customer.lastOrder }}</dd></div></dl><div class="pt-6"><h3 class="text-lg font-bold text-ink">Recent orders</h3><div class="mt-3 divide-y divide-border rounded-md border border-border"><div v-for="order in customer.recentOrders" :key="order.id" class="flex justify-between px-4 py-3 text-sm"><span class="font-semibold text-ink">{{ order.id }}</span><span class="text-muted">{{ order.date }}</span><strong class="text-ink">{{ formatCurrency(order.total) }}</strong></div><p v-if="!customer.recentOrders.length" class="px-4 py-6 text-sm text-muted">No orders yet.</p></div></div><div class="mt-6 border-t border-border pt-5 text-sm text-muted"><p v-if="customer.address"><strong class="text-ink">Address:</strong> {{ customer.address }}</p><p v-else>No address saved.</p></div></article><p v-else class="text-sm text-muted">Customer not found.</p></div></section>
</template>
