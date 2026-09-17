<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  subtotal: { type: Number, default: 0 },
})

defineEmits(['increment', 'decrement', 'remove', 'clear', 'checkout'])

const formatCurrency = (value) => `$${value.toFixed(2)}`
</script>

<template>
  <aside class="cart">
    <header class="cart-header">
      <div>
        <p class="eyebrow">Order 001</p>
        <h2>Current order</h2>
      </div>
      <button v-if="items.length" class="clear-button" type="button" @click="$emit('clear')">
        Clear
      </button>
    </header>

    <div v-if="!items.length" class="empty-cart">
      <span class="empty-icon" aria-hidden="true">+</span>
      <strong>Your order is empty</strong>
      <p>Select a product to start building the order.</p>
    </div>

    <ul v-else class="cart-items">
      <li v-for="item in items" :key="item.id" class="cart-item">
        <div class="item-details">
          <strong>{{ item.name }}</strong>
          <span>{{ formatCurrency(item.price) }} each</span>
        </div>
        <div class="item-actions">
          <div class="quantity-control" :aria-label="`Quantity for ${item.name}`">
            <button type="button" aria-label="Decrease quantity" @click="$emit('decrement', item)">
              -
            </button>
            <span>{{ item.quantity }}</span>
            <button type="button" aria-label="Increase quantity" @click="$emit('increment', item)">
              +
            </button>
          </div>
          <strong class="item-total">{{ formatCurrency(item.price * item.quantity) }}</strong>
          <button class="remove-button" type="button" aria-label="Remove item" @click="$emit('remove', item)">
            x
          </button>
        </div>
      </li>
    </ul>

    <div v-if="items.length" class="order-summary">
      <div><span>Subtotal</span><strong>{{ formatCurrency(subtotal) }}</strong></div>
      <div><span>Tax <small>(10%)</small></span><strong>{{ formatCurrency(subtotal * 0.1) }}</strong></div>
      <div class="summary-total"><span>Total</span><strong>{{ formatCurrency(subtotal * 1.1) }}</strong></div>
      <button class="checkout-button" type="button" @click="$emit('checkout')">
        Continue to payment
        <span aria-hidden="true">-&gt;</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.cart {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 1.5rem 1.25rem;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
}

.cart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--color-brand);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.35rem;
}

button {
  border: 0;
  cursor: pointer;
}

.clear-button {
  padding: 0.25rem 0;
  color: var(--color-muted);
  background: transparent;
  font-size: 0.75rem;
}

.clear-button:hover,
.remove-button:hover {
  color: var(--color-brand);
}

.empty-cart {
  display: grid;
  justify-items: center;
  gap: 0.5rem;
  margin: auto 0;
  padding: 2rem 1rem;
  color: var(--color-muted);
  text-align: center;
}

.empty-icon {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  margin-bottom: 0.25rem;
  color: var(--color-brand);
  background: #fff1e9;
  border-radius: 50%;
  font-size: 1.35rem;
}

.empty-cart strong {
  color: var(--color-ink);
  font-size: 0.9rem;
}

.empty-cart p {
  max-width: 14rem;
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.5;
}

.cart-items {
  display: grid;
  gap: 1rem;
  max-height: 24rem;
  margin: 0;
  padding: 1.25rem 0;
  overflow-y: auto;
  list-style: none;
}

.cart-item {
  display: grid;
  gap: 0.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eef0f2;
}

.item-details {
  display: grid;
  gap: 0.25rem;
}

.item-details strong {
  color: var(--color-ink);
  font-size: 0.85rem;
}

.item-details span {
  color: var(--color-muted);
  font-size: 0.72rem;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.2rem;
  background: #f5f6f7;
  border-radius: 5px;
}

.quantity-control button {
  width: 1.35rem;
  height: 1.35rem;
  color: var(--color-ink);
  background: white;
  border-radius: 4px;
  line-height: 1;
}

.quantity-control button:hover {
  color: white;
  background: var(--color-brand);
}

.quantity-control span {
  min-width: 0.75rem;
  font-size: 0.75rem;
  text-align: center;
}

.item-total {
  margin-left: auto;
  color: var(--color-ink);
  font-size: 0.8rem;
}

.remove-button {
  padding: 0.2rem;
  color: #aab2bb;
  background: transparent;
  font-size: 0.85rem;
}

.order-summary {
  display: grid;
  gap: 0.8rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.order-summary > div {
  display: flex;
  justify-content: space-between;
  color: var(--color-muted);
  font-size: 0.78rem;
}

.order-summary small {
  font-size: 0.68rem;
}

.order-summary strong {
  color: var(--color-ink);
}

.summary-total {
  align-items: baseline;
  margin-top: 0.2rem;
  padding-top: 0.8rem;
  border-top: 1px dashed var(--color-border);
  color: var(--color-ink) !important;
  font-size: 1rem !important;
}

.summary-total strong {
  color: var(--color-brand-dark);
  font-size: 1.15rem;
}

.checkout-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.4rem;
  padding: 0.85rem 1rem;
  color: white;
  background: var(--color-brand);
  border-radius: var(--radius-sm);
  font-weight: 700;
}

.checkout-button:hover {
  background: var(--color-brand-dark);
}
</style>
