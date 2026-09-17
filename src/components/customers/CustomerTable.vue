<script setup>
import CustomerRow from './CustomerRow.vue'

defineProps({ customers: { type: Array, default: () => [] } })
const emit = defineEmits(['view', 'edit', 'delete'])
</script>

<template>
  <div class="overflow-x-auto rounded-lg border border-border bg-surface shadow-sm"><table class="w-full min-w-[850px] text-left"><thead class="border-b border-border bg-background text-xs uppercase tracking-wide text-muted"><tr><th class="px-5 py-3 font-semibold">Customer</th><th class="px-5 py-3 font-semibold">Phone</th><th class="px-5 py-3 font-semibold">Orders</th><th class="px-5 py-3 font-semibold">Spent</th><th class="px-5 py-3 font-semibold">Last order</th><th class="px-5 py-3 text-right font-semibold">Actions</th></tr></thead><tbody><CustomerRow v-for="customer in customers" :key="customer.id" :customer="customer" @view="emit('view', $event)" @edit="emit('edit', $event)" @delete="emit('delete', $event)" /><tr v-if="!customers.length"><td colspan="6" class="px-5 py-12 text-center text-sm text-muted">No customers match your search.</td></tr></tbody></table></div>
</template>
