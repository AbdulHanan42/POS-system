<script setup>
defineProps({
  product: { type: Object, required: true },
})

defineEmits(['add'])
</script>

<template>
  <article class="product-card">
    <div>
      <h3>{{ product.name }}</h3>
      <p>{{ product.category }}</p>
    </div>
    <strong>${{ product.price.toFixed(2) }}</strong>
    <button type="button" @click="$emit('add', product)">Add</button>
  </article>
</template>

<style scoped>
.product-card {
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

h3,
p {
  margin: 0;
}

p {
  color: var(--color-muted);
}

button {
  color: white;
  background: var(--color-brand);
  border: 0;
  border-radius: var(--radius-sm);
  padding: 0.5rem;
  cursor: pointer;
}
</style>
