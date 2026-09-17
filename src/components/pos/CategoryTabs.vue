<script setup>
defineProps({ categories: { type: Array, default: () => [] }, active: { type: String, default: 'All' } })
defineEmits(['update:active'])
</script>

<template>
  <div class="flex gap-1 overflow-x-auto rounded-lg bg-background p-1">
    <button v-for="category in categories" :key="category" type="button" class="whitespace-nowrap rounded-md px-4 py-2 text-sm font-semibold transition" :class="active === category ? 'bg-surface text-brand shadow-sm' : 'text-muted hover:text-ink'" @click="$emit('update:active', category)">{{ category }}</button>
  </div>
</template>
