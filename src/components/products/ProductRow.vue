<script setup>
import ProductActions from './ProductActions.vue'
import ProductStatus from './ProductStatus.vue'

defineProps({ product: { type: Object, required: true } })
const emit = defineEmits(['view', 'edit', 'delete'])
</script>

<template>
  <tr class="border-b border-border last:border-0 hover:bg-background">
    <td class="px-5 py-4">
      <div class="flex items-center gap-3">
        <img v-if="product.image" :src="product.image" :alt="product.name" class="size-11 shrink-0 rounded-lg object-cover" />
        <div v-else class="grid size-11 shrink-0 place-items-center rounded-lg bg-orange-50 font-bold text-brand">{{ product.name.charAt(0) }}</div>
        <div>
          <p class="font-semibold text-ink">{{ product.name }}</p>
          <p class="mt-1 max-w-xs truncate text-xs text-muted">{{ product.description }}</p>
        </div>
      </div>
    </td>
    <td class="px-5 py-4 text-sm text-muted">{{ product.category }}<span v-if="product.pizzaCategory" class="mt-1 block text-xs text-brand">{{ product.pizzaCategory }}</span></td>
    <td class="px-5 py-4 font-semibold text-ink">${{ Number(product.price).toFixed(2) }}</td>
    <td class="px-5 py-4"><ProductStatus :status="product.status" /></td>
    <td class="px-5 py-4"><ProductActions :product="product" @view="emit('view', product)" @edit="emit('edit', product)" @delete="emit('delete', product)" /></td>
  </tr>
</template>
