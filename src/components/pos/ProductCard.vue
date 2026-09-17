<script setup>
import { ref } from 'vue'
import BaseButton from '../common/BaseButton.vue'

const props = defineProps({ product: { type: Object, required: true } })
const emit = defineEmits(['add'])
const selectedSize = ref('medium')

function addProduct() {
  const isPizza = Boolean(props.product.prices)
  const size = isPizza ? selectedSize.value : null
  emit('add', { ...props.product, price: isPizza ? props.product.prices[size] : props.product.price, selectedSize: size })
}
</script>

<template>
  <article class="group overflow-hidden rounded-lg border border-border bg-surface shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
    <div class="relative h-36 overflow-hidden bg-orange-50">
      <img v-if="product.image" :src="product.image" :alt="product.name" class="size-full object-cover transition duration-300 group-hover:scale-105" />
      <span v-if="product.pizzaCategory" class="absolute left-3 top-3 rounded-full bg-surface/90 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-brand">{{ product.pizzaCategory }}</span>
    </div>
    <div class="grid gap-3 p-4">
      <div><h3 class="font-semibold text-ink">{{ product.name }}</h3><p class="mt-1 text-xs text-muted">{{ product.category }}</p></div>
      <div v-if="product.prices" class="flex gap-1 rounded-sm bg-background p-1">
        <button v-for="size in ['small', 'medium', 'large']" :key="size" type="button" class="flex-1 rounded px-1 py-1.5 text-[10px] font-semibold capitalize" :class="selectedSize === size ? 'bg-surface text-brand shadow-sm' : 'text-muted'" @click="selectedSize = size">{{ size.charAt(0).toUpperCase() }} <span class="block font-normal">${{ product.prices[size].toFixed(2) }}</span></button>
      </div>
      <div class="flex items-center justify-between"><strong class="text-base text-ink">${{ Number(product.prices ? product.prices[selectedSize] : product.price).toFixed(2) }}</strong><BaseButton class="min-h-9 px-3 text-xs" @click="addProduct">Add</BaseButton></div>
    </div>
  </article>
</template>
