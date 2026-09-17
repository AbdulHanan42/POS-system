<script setup>
defineProps({ modelValue: { type: String, default: '' }, type: { type: String, default: 'All Customers' } })
defineEmits(['update:modelValue', 'update:type'])
</script>

<template>
  <div class="flex flex-col gap-3 sm:flex-row">
    <label class="relative block flex-1"><span class="sr-only">Search customer by name or phone</span><span class="pointer-events-none absolute inset-y-0 left-3 grid place-items-center text-muted">⌕</span><input :value="modelValue" type="search" placeholder="Search name or phone..." class="h-11 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none placeholder:text-muted focus:border-brand focus:ring-2 focus:ring-orange-100" @input="$emit('update:modelValue', $event.target.value)" /></label>
    <select :value="type" class="h-11 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand" @change="$emit('update:type', $event.target.value)"><option>All Customers</option><option>Regular</option><option>VIP</option></select>
  </div>
</template>
