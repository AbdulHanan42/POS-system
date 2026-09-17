<script setup>
defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <aside class="cart">
    <h2>Current order</h2>
    <p v-if="!items.length">No items added yet.</p>
    <ul v-else>
      <li v-for="item in items" :key="item.id">{{ item.name }} x {{ item.quantity }}</li>
    </ul>
  </aside>
</template>

<style scoped>
.cart {
  padding: 1.25rem;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
}

ul {
  padding: 0;
  list-style: none;
}
</style>
