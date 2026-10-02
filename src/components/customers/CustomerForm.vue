<script setup>
import { reactive, ref } from 'vue'
import BaseButton from '../common/BaseButton.vue'

const props = defineProps({ customer: { type: Object, default: () => ({ name: '', phone: '', email: '', address: '', type: 'Regular' }) } })
const emit = defineEmits(['submit', 'cancel'])
const form = reactive({ ...props.customer })
const error = ref('')

function submit() {
  error.value = ''
  if (!form.name.trim()) error.value = 'Customer name is required.'
  else if (!form.phone.trim()) error.value = 'Phone number is required.'
  if (error.value) return
  emit('submit', { ...form })
}
</script>

<template>
  <form class="grid gap-5" @submit.prevent="submit"><div class="grid gap-4 sm:grid-cols-2"><label class="grid gap-2 text-sm font-semibold text-ink">Name<input v-model="form.name" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="e.g. Ahmed Khan" /></label><label class="grid gap-2 text-sm font-semibold text-ink">Phone<input v-model="form.phone" type="tel" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="0300-1234567" /></label><label class="grid gap-2 text-sm font-semibold text-ink">Email <span class="font-normal text-muted">(optional)</span><input v-model="form.email" type="email" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="customer@example.com" /></label><label class="grid gap-2 text-sm font-semibold text-ink">Customer type<select v-model="form.type" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand"><option>Regular</option><option>VIP</option></select></label><label class="grid gap-2 text-sm font-semibold text-ink sm:col-span-2">Address <span class="font-normal text-muted">(optional)</span><textarea v-model="form.address" rows="3" class="rounded-sm border border-border px-3 py-2 font-normal outline-none focus:border-brand" placeholder="Customer address" /></label></div><p v-if="error" class="text-sm text-danger">{{ error }}</p><div class="flex justify-end gap-2 border-t border-border pt-4"><BaseButton variant="secondary" @click="emit('cancel')">Cancel</BaseButton><BaseButton type="submit">Save customer</BaseButton></div></form>
</template>
