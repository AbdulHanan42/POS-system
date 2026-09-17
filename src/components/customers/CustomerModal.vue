<script setup>
import BaseModal from '../common/BaseModal.vue'
import CustomerForm from './CustomerForm.vue'

defineProps({ open: Boolean, customer: { type: Object, default: null } })
const emit = defineEmits(['submit', 'close'])
</script>

<template>
  <BaseModal :open="open"><div class="w-full max-w-2xl rounded-lg bg-surface p-6 shadow-xl"><div class="mb-6 flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Customer profile</p><h2 class="mt-1 text-xl font-bold text-ink">{{ customer ? 'Edit customer' : 'Add customer' }}</h2></div><button type="button" class="text-xl text-muted hover:text-ink" aria-label="Close customer form" @click="emit('close')">&times;</button></div><CustomerForm :customer="customer || undefined" @submit="emit('submit', $event)" @cancel="emit('close')" /></div></BaseModal>
</template>
