<script setup>
import { computed, ref } from "vue";
import BaseButton from "../../components/common/BaseButton.vue";
import Cart from "../../components/pos/Cart.vue";
import CategoryTabs from "../../components/pos/CategoryTabs.vue";
import PaymentModal from "../../components/pos/PaymentModal.vue";
import ProductCard from "../../components/pos/ProductCard.vue";
import ReceiptModal from "../../components/pos/ReceiptModal.vue";
import SearchProduct from "../../components/pos/SearchProduct.vue";
import { useCartStore } from "../../stores/cart.js";
import { useOrderStore } from "../../stores/order.js";
import { useProductStore } from "../../stores/product.js";

const cart = useCartStore();
const orders = useOrderStore();
const productStore = useProductStore();
const search = ref("");
const activeCategory = ref("All");
const orderType = ref("Dine in");
const table = ref("Table 01");
const discount = ref(0);
const showPayment = ref(false);
const showReceipt = ref(false);
const notice = ref("");
const orderError = ref("");
const submittingOrder = ref(false);
const savedOrderId = ref(null);
const payment = ref({ method: "", received: 0, change: 0 });
const categories = computed(() => ["All", ...productStore.categories]);

const filteredProducts = computed(() =>
  productStore.items.filter((product) => {
    const query = search.value.trim().toLowerCase();
    return (
      (activeCategory.value === "All" || product.category === activeCategory.value) &&
      (!query || `${product.name} ${product.category}`.toLowerCase().includes(query))
    );
  })
);
const discountedTotal = computed(() => Math.max(0, cart.total - discount.value) * 1.1);

async function completePayment(paymentDetails) {
  orderError.value = "";
  submittingOrder.value = true;
  try {
    const order = await orders.addOrder({
      createdAt: new Date().toISOString(),
      status: "paid",
      type: orderType.value,
      table: orderType.value === "Dine in" ? table.value : "",
      customer: "Walk-in customer",
      paymentMethod: paymentDetails.method,
      total: discountedTotal.value,
      items: cart.items.map(({ name, quantity, price, selectedSize }) => ({ name, quantity, price, selectedSize })),
    });
    savedOrderId.value = order.id;
    notice.value = `Order #${order.id} saved. Payment received via ${paymentDetails.method}.`;
    payment.value = paymentDetails;
    showPayment.value = false;
    showReceipt.value = true;
    window.setTimeout(() => {
      notice.value = "";
    }, 4000);
  } catch (error) {
    orderError.value = error.message || "Could not save the order. Please try again.";
  } finally {
    submittingOrder.value = false;
  }
}

function editBill() {
  showReceipt.value = false;
  showPayment.value = false;
}

function previewBill() {
  showPayment.value = false;
  showReceipt.value = true;
}

function finishOrder() {
  showReceipt.value = false;
  savedOrderId.value = null;
  cart.clear();
  discount.value = 0;
  notice.value = "";
}
</script>

<template>
  <section class="min-h-screen bg-background">
    <div
      class="flex flex-col border-b border-border bg-surface px-5 py-4 lg:flex-row lg:items-center lg:justify-between lg:px-8"
    >
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">
          Front counter
        </p>
        <h1 class="mt-1 text-2xl font-bold text-ink">Point of Sale</h1>
      </div>
      <div class="mt-4 flex flex-wrap items-center gap-2 lg:mt-0">
        <select
          v-model="orderType"
          class="h-10 rounded-sm border border-border bg-surface px-3 text-sm font-semibold text-ink outline-none focus:border-brand"
        >
          <option>Dine in</option>
          <option>Takeaway</option>
          <option>Delivery</option></select
        ><select
          v-if="orderType === 'Dine in'"
          v-model="table"
          class="h-10 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand"
        >
          <option>Table 01</option>
          <option>Table 02</option>
          <option>Table 03</option>
          <option>Table 04</option></select
        ><span
          class="rounded-full bg-green-50 px-3 py-2 text-xs font-semibold text-success"
          >Register open</span
        >
      </div>
    </div>
    <p
      v-if="notice"
      class="mx-5 mt-4 rounded-sm border border-green-200 bg-green-50 px-4 py-3 text-sm text-success lg:mx-8"
    >
      {{ notice }}
    </p>
    <p v-if="productStore.error" role="alert" class="mx-5 mt-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger lg:mx-8">Could not load products: {{ productStore.error }}</p>
    <div class="grid lg:grid-cols-[minmax(0,1fr)_22rem]">
      <div class="min-w-0 px-5 py-6 lg:px-8">
        <div class="flex flex-col gap-3 sm:flex-row">
          <SearchProduct v-model="search" /><BaseButton
            variant="secondary"
            class="shrink-0"
            @click="search = ''"
            >Clear search</BaseButton
          >
        </div>
        <div class="mt-5">
          <CategoryTabs v-model:active="activeCategory" :categories="categories" />
        </div>
        <div class="mt-5 flex items-center justify-between">
          <p class="text-sm text-muted">
            <strong class="text-ink">{{ filteredProducts.length }}</strong> menu items
          </p>
          <span class="text-xs text-muted">Tap a size before adding a pizza</span>
        </div>
        <div class="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <ProductCard
            v-for="product in filteredProducts"
            :key="product.id"
            :product="product"
            @add="cart.addItem"
          />
          <div
            v-if="!filteredProducts.length"
            class="col-span-full rounded-lg border border-dashed border-border bg-surface p-12 text-center text-sm text-muted"
          >
            No menu items found. Try another search or category.
          </div>
        </div>
      </div>
      <Cart
        :items="cart.items"
        :subtotal="cart.total"
        :discount="discount"
        :order-type="orderType"
        :table="table"
        @increment="cart.addItem"
        @decrement="cart.decreaseItem"
        @remove="cart.removeItem"
        @clear="cart.clear"
        @update-discount="discount = $event"
        @checkout="showReceipt = true"
      />
    </div>
    <PaymentModal
      :open="showPayment"
      :total="discountedTotal"
      :error="orderError"
      :submitting="submittingOrder"
      @close="showPayment = false"
      @edit="editBill"
      @print="previewBill"
      @paid="completePayment"
    />
    <ReceiptModal
      :open="showReceipt"
      :items="cart.items"
      :subtotal="cart.total"
      :discount="discount"
      :total="discountedTotal"
      :order-type="orderType"
      :table="table"
      :paid="Boolean(payment.method)"
      :received="payment.received"
      :change="payment.change"
      :payment-method="payment.method"
      :order-id="savedOrderId"
      @close="showReceipt = false"
      @edit="editBill"
      @pay="showPayment = true"
      @save="finishOrder"
    />
  </section>
</template>
