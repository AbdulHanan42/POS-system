<script setup>
defineProps({ product: { type: Object, required: true } })
const emit = defineEmits(['view', 'edit', 'delete'])
</script>

<template>
	<div class="flex items-center gap-3 text-xs font-semibold">
		<button type="button" class="text-brand hover:underline" :aria-label="`View ${product.name}`" @click="emit('view')">View</button>
		<button type="button" class="text-ink hover:underline" :aria-label="`Edit ${product.name}`" @click="emit('edit')">Edit</button>
		<button type="button" class="text-danger hover:underline" :aria-label="`Delete ${product.name}`" @click="emit('delete')">Delete</button>
	</div>
</template>
