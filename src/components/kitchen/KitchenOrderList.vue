<script setup>
import KitchenOrderCard from './KitchenOrderCard.vue'

defineProps({
	orders: { type: Array, default: () => [] },
	loading: { type: Boolean, default: false },
	updatingId: { type: [Number, String], default: null },
	emptyMessage: { type: String, default: 'No orders in this view.' },
})

defineEmits(['advance'])
</script>

<template>
	<div v-if="loading && !orders.length" role="status" class="py-16 text-center text-sm text-muted">Loading kitchen orders...</div>
	<div v-else-if="orders.length" class="grid items-stretch gap-4 sm:grid-cols-2 2xl:grid-cols-3">
		<KitchenOrderCard v-for="order in orders" :key="order.id" :order="order" :updating="updatingId === order.id" @advance="$emit('advance', $event)" />
	</div>
	<div v-else class="py-16 text-center"><p class="text-base font-semibold text-ink">{{ emptyMessage }}</p><p class="mt-1 text-sm text-muted">New paid orders will appear here automatically.</p></div>
</template>
