<script setup>
import Cart from '../../components/pos/Cart.vue'
import ProductCard from '../../components/pos/ProductCard.vue'
import products from '../../data/products.js'
import { useCartStore } from '../../stores/cart.js'

const cart = useCartStore()
</script>

<template>
  <section class="pos-page">
    <div class="products">
      <header>
        <h1>Point of Sale</h1>
        <p>Select products to start an order.</p>
      </header>
      <div class="product-grid">
        <ProductCard v-for="product in products" :key="product.id" :product="product" @add="cart.addItem" />
      </div>
    </div>
    <Cart
      :items="cart.items"
      :subtotal="cart.total"
      @increment="cart.addItem"
      @decrement="cart.decreaseItem"
      @remove="cart.removeItem"
      @clear="cart.clear"
    />
  </section>
</template>

<style scoped>
.pos-page {
  display: grid;
  grid-template-columns: 1fr 20rem;
  min-height: 100vh;
}

.products {
  padding: 2rem;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
  gap: 1rem;
}

@media (max-width: 820px) {
  .pos-page {
    grid-template-columns: 1fr;
  }

  .products {
    padding: 1.25rem;
  }
}
</style>
