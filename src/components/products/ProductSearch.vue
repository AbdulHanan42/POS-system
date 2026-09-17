<script setup>
defineProps({ modelValue: { type: String, default: '' } })
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="relative block">
    <span class="sr-only">Search products</span>
    <span class="pointer-events-none absolute inset-y-0 left-3 grid place-items-center text-muted">⌕</span>
    <input
      :value="modelValue"
      type="search"
      placeholder="Search products..."
      class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none placeholder:text-muted focus:border-brand focus:ring-2 focus:ring-orange-100"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </label>
</template>
