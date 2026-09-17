<script setup>
import ProductStatus from './ProductStatus.vue'

defineProps({ product: { type: Object, required: true } })
</script>

<template>
  <article class="rounded-lg border border-border bg-surface p-6 shadow-sm">
    <img v-if="product.image" :src="product.image" :alt="product.name" class="mb-6 h-56 w-full rounded-lg object-cover" />
    <div class="flex items-start justify-between gap-4">
      <div><p class="text-xs font-semibold uppercase tracking-wide text-muted">Product details</p><h2 class="mt-2 text-2xl font-bold text-ink">{{ product.name }}</h2></div>
      <ProductStatus :status="product.status" />
    </div>
    <dl class="mt-6 grid gap-4 sm:grid-cols-2"><div><dt class="text-xs text-muted">Category</dt><dd class="mt-1 font-semibold text-ink">{{ product.category }}<span v-if="product.pizzaCategory" class="ml-2 text-brand">{{ product.pizzaCategory }}</span></dd></div><div v-if="product.prices"><dt class="text-xs text-muted">Pizza sizes</dt><dd class="mt-1 flex gap-3 text-sm font-semibold text-ink"><span>Small ${{ product.prices.small.toFixed(2) }}</span><span>Medium ${{ product.prices.medium.toFixed(2) }}</span><span>Large ${{ product.prices.large.toFixed(2) }}</span></dd></div><div v-else><dt class="text-xs text-muted">Price</dt><dd class="mt-1 font-semibold text-ink">${{ Number(product.price).toFixed(2) }}</dd></div></dl>
    <p class="mt-6 border-t border-border pt-5 text-sm leading-6 text-muted">{{ product.description }}</p>
  </article>
</template>
