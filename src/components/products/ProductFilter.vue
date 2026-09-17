<script setup>
defineProps({ category: { type: String, default: 'All' }, status: { type: String, default: 'all' }, categories: { type: Array, default: () => [] } })
defineEmits(['update:category', 'update:status'])
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <select :value="category" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand" @change="$emit('update:category', $event.target.value)">
      <option value="All">All categories</option>
      <option v-for="item in categories" :key="item" :value="item">{{ item }}</option>
    </select>
    <select :value="status" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand" @change="$emit('update:status', $event.target.value)">
      <option value="all">All statuses</option>
      <option value="active">Active</option>
      <option value="inactive">Inactive</option>
    </select>
  </div>
</template>
