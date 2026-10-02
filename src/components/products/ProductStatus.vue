<script setup>
defineProps({ status: { type: String, default: 'active' } })
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold capitalize"
    :class="status === 'active' ? 'bg-green-50 text-success' : 'bg-gray-100 text-muted'"
  >
    <span class="size-1.5 rounded-full" :class="status === 'active' ? 'bg-success' : 'bg-gray-400'" />
    {{ status }}
  </span>
</template>
