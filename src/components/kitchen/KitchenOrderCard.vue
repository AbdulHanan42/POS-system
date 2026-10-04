<script setup>
import { computed } from 'vue'
import { Check, CircleCheck, CookingPot } from 'lucide-vue-next'
import OrderStatus from './OrderStatus.vue'

const props = defineProps({
	order: { type: Object, required: true },
	updating: { type: Boolean, default: false },
})
const emit = defineEmits(['advance'])
const nextStatus = computed(() => ({ queued: 'preparing', preparing: 'ready', ready: 'completed' })[props.order.kitchenStatus])
const actionLabel = computed(() => ({ queued: 'Start preparing', preparing: 'Mark ready', ready: 'Complete order' })[props.order.kitchenStatus])
const itemCount = computed(() => props.order.items.reduce((total, item) => total + item.quantity, 0))
const placedTime = computed(() => new Date(props.order.createdAt).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }))

function advance() {
	if (nextStatus.value) emit('advance', { order: props.order, kitchenStatus: nextStatus.value })
}
</script>

<template>
	<article class="flex h-full flex-col rounded-md border border-border bg-surface shadow-sm">
		<header class="flex items-start justify-between gap-3 border-b border-border px-4 py-3">
			<div class="min-w-0"><p class="text-xs font-bold uppercase tracking-wide text-muted">{{ order.type }}<span v-if="order.table"> · {{ order.table }}</span></p><h3 class="mt-1 truncate text-xl font-bold text-ink">#{{ order.id }} <span class="text-sm font-medium text-muted">{{ order.customer }}</span></h3></div>
			<OrderStatus :status="order.kitchenStatus" />
		</header>

		<div class="flex items-center justify-between px-4 py-3 text-xs text-muted"><span>{{ itemCount }} {{ itemCount === 1 ? 'item' : 'items' }}</span><time :datetime="order.createdAt">Placed {{ placedTime }}</time></div>
		<ul class="mx-4 divide-y divide-border border-y border-border">
			<li v-for="(item, index) in order.items" :key="`${item.productId || item.name}-${index}`" class="py-3">
				<div class="flex items-start gap-3"><strong class="min-w-7 rounded-sm bg-background px-2 py-1 text-center text-sm text-ink">{{ item.quantity }}×</strong><div class="min-w-0"><p class="font-semibold text-ink">{{ item.name }}<span v-if="item.selectedSize" class="ml-1 font-normal text-muted">· {{ item.selectedSize }}</span></p><p v-for="modifier in item.modifiers || []" :key="`${modifier.group}-${modifier.name}`" class="mt-1 text-xs text-muted">{{ modifier.group }}: {{ modifier.name }}</p></div></div>
			</li>
		</ul>

		<div v-if="order.kitchenStatus !== 'completed' && (order.kitchenStatus !== 'ready' || order.status === 'paid')" class="mt-auto p-4"><button type="button" class="inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-sm bg-ink px-4 text-sm font-semibold text-white hover:bg-brand disabled:cursor-wait disabled:opacity-60" :disabled="updating" @click="advance"><CookingPot v-if="order.kitchenStatus !== 'ready'" :size="16" aria-hidden="true" /><Check v-else :size="16" aria-hidden="true" />{{ updating ? 'Saving...' : actionLabel }}</button></div>
		<div v-else-if="order.kitchenStatus === 'ready' && order.status === 'awaiting_payment'" class="mt-auto flex items-center justify-center gap-2 p-4 text-sm font-semibold text-brand-dark"><Check :size="17" aria-hidden="true" />Ready for cashier payment</div>
		<div v-else class="mt-auto flex items-center justify-center gap-2 p-4 text-sm font-semibold text-success"><CircleCheck :size="17" aria-hidden="true" />Order complete</div>
	</article>
</template>
