<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import BaseButton from '../common/BaseButton.vue'
import ProductImageUpload from './ProductImageUpload.vue'
import { useCategoryStore } from '../../stores/category.js'
import { validateProduct } from '../../utils/productValidation.js'

const props = defineProps({ initialProduct: { type: Object, default: () => ({ name: '', category: 'Mains', pizzaCategory: 'Regular', price: '', prices: { small: '', medium: '', large: '' }, status: 'active', description: '' }) }, submitLabel: { type: String, default: 'Save product' } })
const emit = defineEmits(['submit', 'cancel'])
const form = reactive({ ...props.initialProduct, prices: { small: '', medium: '', large: '', ...props.initialProduct.prices } })
const errors = ref({})
const categoryStore = useCategoryStore()
const isPizzaCategory = computed(() => categoryStore.items.find((category) => category.name === form.category)?.isPizza ?? (form.category === 'Pizza' || Boolean(form.pizzaCategory)))

onMounted(() => {
  if (!categoryStore.items.length) categoryStore.load().catch(() => undefined)
})

function submit() {
  errors.value = validateProduct({ ...form, isPizza: isPizzaCategory.value })
  if (Object.keys(errors.value).length) return
  emit('submit', {
    ...form,
    price: isPizzaCategory.value ? Number(form.prices.medium) : Number(form.price),
    prices: isPizzaCategory.value ? { small: Number(form.prices.small), medium: Number(form.prices.medium), large: Number(form.prices.large) } : undefined,
  })
}
</script>

<template>
  <form class="grid gap-6 rounded-lg border border-border bg-surface p-6 shadow-sm" @submit.prevent="submit">
    <div class="grid gap-5 sm:grid-cols-2">
      <label class="grid gap-2 text-sm font-semibold text-ink sm:col-span-2">Product name<input v-model="form.name" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="e.g. Spicy chicken wrap" /><small v-if="errors.name" class="font-normal text-danger">{{ errors.name }}</small></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">Category<select v-model="form.category" required class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand"><option v-for="category in categoryStore.items" :key="category.id" :value="category.name">{{ category.name }}</option></select><small v-if="errors.category" class="font-normal text-danger">{{ errors.category }}</small><small v-if="categoryStore.error" class="font-normal text-danger">Could not load categories: {{ categoryStore.error }}</small></label>
      <label v-if="!isPizzaCategory" class="grid gap-2 text-sm font-semibold text-ink">Price<input v-model="form.price" type="number" min="0" step="0.01" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="0.00" /><small v-if="errors.price" class="font-normal text-danger">{{ errors.price }}</small></label>
      <div v-else class="grid gap-2 text-sm font-semibold text-ink"><span>Pizza style</span><div class="flex gap-2"><label v-for="type in ['Regular', 'Signature']" :key="type" class="flex flex-1 cursor-pointer items-center gap-2 rounded-sm border border-border px-3 py-2 font-normal"><input v-model="form.pizzaCategory" type="radio" :value="type" class="accent-brand" />{{ type }}</label></div></div>
      <div v-if="isPizzaCategory" class="grid gap-3 sm:col-span-2"><p class="text-sm font-semibold text-ink">Size prices</p><div class="grid gap-3 sm:grid-cols-3"><label v-for="size in ['small', 'medium', 'large']" :key="size" class="grid gap-2 text-xs font-semibold capitalize text-muted">{{ size }}<input v-model="form.prices[size]" type="number" min="0" step="0.01" class="h-10 rounded-sm border border-border px-3 text-sm font-normal text-ink outline-none focus:border-brand" placeholder="0.00" /><small v-if="errors[`${size}Price`]" class="font-normal text-danger">{{ errors[`${size}Price`] }}</small></label></div></div>
      <label class="grid gap-2 text-sm font-semibold text-ink sm:col-span-2">Description<textarea v-model="form.description" rows="4" class="rounded-sm border border-border px-3 py-2 font-normal outline-none focus:border-brand" placeholder="Describe the product for your team." /></label>
      <div class="sm:col-span-2"><p class="mb-2 text-sm font-semibold text-ink">Image</p><ProductImageUpload v-model="form.image" /></div>
    </div>
    <div class="flex justify-end gap-2 border-t border-border pt-5"><BaseButton variant="secondary" @click="$emit('cancel')">Cancel</BaseButton><BaseButton type="submit">{{ submitLabel }}</BaseButton></div>
  </form>
</template>
