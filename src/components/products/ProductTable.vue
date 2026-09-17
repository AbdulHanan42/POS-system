<script setup>
import ProductRow from './ProductRow.vue'

defineProps({ products: { type: Array, default: () => [] } })
const emit = defineEmits(['view', 'edit', 'delete'])
</script>

<template>
  <div class="overflow-x-auto rounded-lg border border-border bg-surface shadow-sm">
    <table class="w-full min-w-[700px] text-left">
      <thead class="border-b border-border bg-background text-xs uppercase tracking-wide text-muted">
        <tr>
          <th class="px-5 py-3 font-semibold">Product</th>
          <th class="px-5 py-3 font-semibold">Category</th>
          <th class="px-5 py-3 font-semibold">Price</th>
          <th class="px-5 py-3 font-semibold">Status</th>
          <th class="px-5 py-3 text-right font-semibold">Actions</th>
        </tr>
      </thead>
      <tbody>
        <ProductRow v-for="product in products" :key="product.id" :product="product" @view="emit('view', $event)" @edit="emit('edit', $event)" @delete="emit('delete', $event)" />
        <tr v-if="!products.length"><td colspan="5" class="px-5 py-12 text-center text-sm text-muted">No products match your filters.</td></tr>
      </tbody>
    </table>
  </div>
</template>
