<script setup>
defineProps({
	status: { type: String, required: true },
})

const labels = {
	queued: 'New',
	preparing: 'Preparing',
	ready: 'Ready',
	completed: 'Completed',
}
</script>

<template>
	<span class="inline-flex min-h-6 items-center rounded-sm px-2 text-xs font-bold" :class="{
		'bg-brand/10 text-brand-dark': status === 'queued',
		'bg-amber-100 text-amber-900': status === 'preparing',
		'bg-success/10 text-success': status === 'ready' || status === 'completed',
	}">{{ labels[status] || status }}</span>
</template>
