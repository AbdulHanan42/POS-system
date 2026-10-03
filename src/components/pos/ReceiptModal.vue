<script setup>
import BaseButton from '../common/BaseButton.vue'
import BaseModal from '../common/BaseModal.vue'

const props = defineProps({
  open: Boolean,
  items: { type: Array, default: () => [] },
  subtotal: { type: Number, default: 0 },
  discount: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  orderType: { type: String, default: 'Dine in' },
  table: { type: String, default: '' },
  paid: Boolean,
  received: { type: Number, default: 0 },
  change: { type: Number, default: 0 },
  paymentMethod: { type: String, default: '' },
  orderId: { type: [Number, String], default: '—' },
})

const emit = defineEmits(['close', 'edit', 'pay', 'save'])
const formatCurrency = (value) => `$${Number(value).toFixed(2)}`

function printReceipt() {
  window.print()
}
</script>

<template>
  <BaseModal :open="open">
    <div class="receipt-card max-h-[90vh] w-full max-w-md overflow-y-auto rounded-lg bg-surface p-6 shadow-xl">
      <div class="flex items-start justify-between gap-4">
        <div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">{{ paid ? 'Paid receipt' : 'Bill receipt' }}</p><h2 class="mt-1 text-xl font-bold text-ink">Order #{{ orderId ?? '—' }}</h2><p class="mt-1 text-xs text-muted">{{ orderType }}<span v-if="table"> · {{ table }}</span></p></div>
        <button type="button" class="text-xl text-muted hover:text-ink" aria-label="Close receipt" @click="emit('close')">&times;</button>
      </div>
      <div class="my-5 border-y border-dashed border-border py-4"><div v-for="item in items" :key="item.itemKey" class="flex justify-between gap-4 py-1.5 text-sm"><span>{{ item.quantity }} x {{ item.name }}<small v-if="item.selectedSize" class="ml-1 text-muted">({{ item.selectedSize }})</small><small v-if="item.modifiers?.length" class="mt-1 block text-xs text-muted">{{ item.modifiers.map((modifier) => `${modifier.group}: ${modifier.name}`).join(', ') }}</small></span><strong>{{ formatCurrency(item.price * item.quantity) }}</strong></div></div>
      <div class="grid gap-2 text-sm"><div class="flex justify-between text-muted"><span>Subtotal</span><strong class="text-ink">{{ formatCurrency(subtotal) }}</strong></div><div class="flex justify-between text-muted"><span>Discount</span><strong class="text-success">-{{ formatCurrency(discount) }}</strong></div><div class="flex justify-between text-muted"><span>Tax</span><strong class="text-ink">{{ formatCurrency(Math.max(0, subtotal - discount) * 0.1) }}</strong></div><div class="mt-2 flex justify-between border-t border-border pt-3 text-base font-bold"><span>Total bill</span><strong class="text-brand-dark">{{ formatCurrency(total) }}</strong></div></div>
      <div v-if="paid" class="mt-5 grid gap-2 rounded-md bg-green-50 p-4 text-sm"><div class="flex justify-between text-muted"><span>Payment method</span><strong class="text-ink">{{ paymentMethod }}</strong></div><div class="flex justify-between text-muted"><span>Total received</span><strong class="text-ink">{{ formatCurrency(received) }}</strong></div><div class="flex justify-between font-bold text-success"><span>Return amount</span><strong>{{ formatCurrency(change) }}</strong></div></div>
      <div class="mt-6 grid gap-2 sm:grid-cols-3"><BaseButton variant="secondary" @click="emit('edit')">Edit bill</BaseButton><BaseButton variant="secondary" @click="printReceipt">Print receipt</BaseButton><BaseButton v-if="!paid" @click="emit('pay')">Receive payment</BaseButton><BaseButton v-else @click="emit('save')">Save</BaseButton></div>
    </div>
  </BaseModal>
</template>

<style>
@media print {
  body * {
    visibility: hidden;
  }

  .receipt-card,
  .receipt-card * {
    visibility: visible;
  }

  .receipt-card {
    position: absolute;
    inset: 0;
    max-width: none;
    box-shadow: none;
  }
}
</style>
