<script setup>
import BaseButton from '../common/BaseButton.vue'

defineProps({ open: Boolean, product: { type: Object, default: null } })
defineEmits(['confirm', 'cancel'])
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-10 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true">
    <div class="w-full max-w-md rounded-lg bg-surface p-6 shadow-xl">
      <h2 class="text-lg font-bold text-ink">Delete product?</h2>
      <p class="mt-2 text-sm leading-6 text-muted">This will remove <strong class="text-ink">{{ product?.name }}</strong> from your menu.</p>
      <div class="mt-6 flex justify-end gap-2">
        <BaseButton variant="secondary" @click="$emit('cancel')">Cancel</BaseButton>
        <BaseButton variant="danger" @click="$emit('confirm')">Delete product</BaseButton>
      </div>
    </div>
  </div>
</template>
