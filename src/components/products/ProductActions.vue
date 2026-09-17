<script setup>
import BaseButton from '../common/BaseButton.vue'

defineProps({ product: { type: Object, required: true } })
defineEmits(['view', 'edit', 'delete'])
</script>

<template>
  <div class="flex items-center justify-end gap-1">
    <BaseButton variant="ghost" class="min-h-8 px-2 text-xs" @click="$emit('view', product)">View</BaseButton>
    <BaseButton variant="ghost" class="min-h-8 px-2 text-xs" @click="$emit('edit', product)">Edit</BaseButton>
    <BaseButton variant="ghost" class="min-h-8 px-2 text-xs text-danger hover:text-danger" @click="$emit('delete', product)">Delete</BaseButton>
  </div>
</template>
