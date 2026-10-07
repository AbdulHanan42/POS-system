<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ArrowLeft, Check, Circle, LoaderCircle } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { publicApi, trackingProtocols } from '../services/publicApi'

const route = useRoute()
const router = useRouter()
const status = ref(null)
const error = ref('')
const token = computed(() => decodeURIComponent(route.hash.slice(1)))
let refreshTimer
let reconnectTimer
let socket

const steps = computed(() => status.value?.deliveryStatus === 'cancelled'
	? ['Order cancelled']
	: ['Order received', 'Preparing', 'Ready', 'Out for delivery', 'Delivered'])
const activeStep = computed(() => {
	if (!status.value) return -1
	if (status.value.deliveryStatus === 'delivered') return 4
	if (status.value.deliveryStatus === 'out_for_delivery') return 3
	if (status.value.kitchenStatus === 'ready') return 2
	if (status.value.kitchenStatus === 'preparing') return 1
	return 0
})

async function refreshStatus() {
	if (!token.value) {
		error.value = 'This tracking link is missing its secure order token.'
		return
	}
	try {
		status.value = await publicApi.getOrderStatus(route.params.orderId, token.value)
		error.value = ''
	} catch (cause) {
		error.value = cause.message
	}
}

function connectEvents() {
	if (!token.value) return
	socket = new WebSocket(publicApi.orderEventsUrl(route.params.orderId), trackingProtocols(token.value))
	socket.addEventListener('message', refreshStatus)
	socket.addEventListener('close', () => {
		if (!['delivered', 'cancelled'].includes(status.value?.deliveryStatus)) {
			reconnectTimer = window.setTimeout(connectEvents, 3000)
		}
	})
}

onMounted(() => {
	refreshStatus()
	connectEvents()
	refreshTimer = window.setInterval(refreshStatus, 20000)
})

onUnmounted(() => {
	window.clearInterval(refreshTimer)
	window.clearTimeout(reconnectTimer)
	socket?.close()
})
</script>

<template>
	<main class="grid min-h-screen place-items-center bg-[var(--paper)] px-5 py-10 text-[var(--ink)]">
		<section class="w-full max-w-xl bg-white p-6 shadow-sm sm:p-10">
			<button class="mb-8 inline-flex items-center gap-2 text-sm font-semibold text-[var(--forest)]" type="button" @click="router.push({ name: 'home', query: route.query })"><ArrowLeft :size="17" /> Back to menu</button>
			<p class="text-[10px] font-bold uppercase tracking-[.18em] text-[var(--clay)]">Order tracking</p>
			<h1 class="mt-2 font-serif text-4xl text-[var(--forest)]">Order #{{ route.params.orderId }}</h1>
			<p v-if="error" class="mt-4 text-sm text-red-800" role="alert">{{ error }}</p>
			<div v-if="status" class="mt-8 border-y border-stone-200 py-5 text-sm"><div class="flex justify-between"><span>Status</span><strong class="capitalize">{{ status.deliveryStatus.replaceAll('_', ' ') }}</strong></div><div class="mt-3 flex justify-between"><span>Total</span><strong>Rs {{ Number(status.total).toLocaleString('en-PK') }}</strong></div></div>
			<ol v-if="status" class="mt-7 grid gap-0">
				<li v-for="(step, index) in steps" :key="step" class="flex min-h-12 items-start gap-3 text-sm" :class="index <= activeStep ? 'text-[var(--forest)]' : 'text-stone-400'">
					<Check v-if="index < activeStep" :size="18" class="mt-0.5 shrink-0" />
					<LoaderCircle v-else-if="index === activeStep" :size="18" class="mt-0.5 shrink-0 animate-spin" />
					<Circle v-else :size="18" class="mt-0.5 shrink-0" />
					<span class="font-medium">{{ step }}</span>
				</li>
			</ol>
			<p class="mt-6 text-xs text-[var(--muted)]">Status updates automatically, even if this connection drops.</p>
		</section>
	</main>
</template>