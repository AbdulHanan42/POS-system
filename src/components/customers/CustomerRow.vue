<script setup>
import BaseButton from '../common/BaseButton.vue'

defineProps({ customer: { type: Object, required: true } })
const emit = defineEmits(['view', 'edit', 'delete'])
const formatCurrency = (value) => `Rs ${Number(value).toLocaleString('en-PK')}`
</script>

<template>
  <tr class="border-b border-border last:border-0 hover:bg-background">
    <td class="px-5 py-4"><div class="flex items-center gap-3"><span class="grid size-10 shrink-0 place-items-center rounded-full bg-orange-50 font-bold text-brand">{{ customer.name.charAt(0) }}</span><div><p class="font-semibold text-ink">{{ customer.name }}</p><span class="text-xs text-muted">{{ customer.type }}</span></div></div></td>
    <td class="px-5 py-4 text-sm text-muted">{{ customer.phone }}</td>
    <td class="px-5 py-4 text-sm font-semibold text-ink">{{ customer.totalOrders }}</td>
    <td class="px-5 py-4 text-sm font-semibold text-ink">{{ formatCurrency(customer.totalSpent) }}</td>
    <td class="px-5 py-4 text-sm text-muted">{{ customer.lastOrder }}</td>
    <td class="px-5 py-4"><div class="flex justify-end gap-1"><BaseButton variant="ghost" class="min-h-8 px-2 text-xs" @click="emit('view', customer)">View</BaseButton><BaseButton variant="ghost" class="min-h-8 px-2 text-xs" @click="emit('edit', customer)">Edit</BaseButton><BaseButton variant="ghost" class="min-h-8 px-2 text-xs text-danger hover:text-danger" @click="emit('delete', customer)">Delete</BaseButton></div></td>
  </tr>
</template>
