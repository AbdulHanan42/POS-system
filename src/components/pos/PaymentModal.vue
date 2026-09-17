<script setup>
import { ref, watch } from 'vue'
import BaseModal from '../common/BaseModal.vue'

const props = defineProps({ open: Boolean, total: { type: Number, default: 0 } })
const emit = defineEmits(['close', 'paid', 'edit', 'print'])
const method = ref('Cash')
const received = ref('')
const methods = ['Cash', 'Card', 'Mobile money']

watch(() => props.open, (open) => {
  if (open) {
    method.value = 'Cash'
    received.value = ''
  }
})

function completePayment() {
  emit('paid', { method: method.value, received: method.value === 'Cash' ? Number(received.value) : props.total, change: method.value === 'Cash' ? Number(received.value) - props.total : 0 })
}
</script>

<template>
  <BaseModal :open="open">
    <div class="w-full max-w-md rounded-lg bg-surface p-6 shadow-xl">
      <div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Checkout</p><h2 class="mt-1 text-xl font-bold text-ink">Take payment</h2></div><button type="button" class="text-xl text-muted hover:text-ink" aria-label="Close payment dialog" @click="emit('close')">&times;</button></div>
      <div class="mt-6 rounded-lg bg-background p-4 text-center"><span class="text-xs text-muted">Amount due</span><strong class="mt-1 block text-3xl text-brand-dark">${{ total.toFixed(2) }}</strong></div>
      <div class="mt-5"><p class="text-sm font-semibold text-ink">Payment method</p><div class="mt-2 grid grid-cols-3 gap-2"><button v-for="item in methods" :key="item" type="button" class="rounded-sm border px-2 py-3 text-xs font-semibold" :class="method === item ? 'border-brand bg-orange-50 text-brand' : 'border-border text-muted'" @click="method = item">{{ item }}</button></div></div>
      <label v-if="method === 'Cash'" class="mt-5 grid gap-2 text-sm font-semibold text-ink">Amount received<input v-model="received" type="number" min="0" step="0.01" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="0.00" /></label>
      <div class="mt-6 flex flex-wrap justify-end gap-2"><button type="button" class="rounded-sm px-4 py-2 text-sm font-semibold text-muted hover:bg-background" @click="emit('edit')">Edit bill</button><button type="button" class="rounded-sm px-4 py-2 text-sm font-semibold text-muted hover:bg-background" @click="emit('print')">Print bill</button><button type="button" class="rounded-sm px-4 py-2 text-sm font-semibold text-muted hover:bg-background" @click="emit('close')">Cancel</button><button type="button" class="rounded-sm bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-50" :disabled="method === 'Cash' && Number(received) < total" @click="completePayment">Complete payment</button></div>
    </div>
  </BaseModal>
</template>
