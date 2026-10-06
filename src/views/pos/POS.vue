<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import BaseButton from "../../components/common/BaseButton.vue";
import Cart from "../../components/pos/Cart.vue";
import CategoryTabs from "../../components/pos/CategoryTabs.vue";
import PaymentModal from "../../components/pos/PaymentModal.vue";
import ProductCard from "../../components/pos/ProductCard.vue";
import ReceiptModal from "../../components/pos/ReceiptModal.vue";
import SearchProduct from "../../components/pos/SearchProduct.vue";
import { useCartStore } from "../../stores/cart.js";
import { useCategoryStore } from "../../stores/category.js";
import { useInventoryStore } from "../../stores/inventory.js";
import { useOrderStore } from "../../stores/order.js";
import { useAuthStore } from "../../stores/auth.js";
import { useSettingsStore } from "../../stores/settings.js";
import { useModifierStore } from "../../stores/modifier.js";
import { useProductStore } from "../../stores/product.js";

const cart = useCartStore();
const orders = useOrderStore();
const auth = useAuthStore();
const productStore = useProductStore();
const categoryStore = useCategoryStore();
const inventoryStore = useInventoryStore();
const modifierStore = useModifierStore();
const settingsStore = useSettingsStore();
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
const sendingToKitchen = ref(false);
const savedOrderId = ref(null);
const selectedKitchenOrder = ref(null);
const receiptOrder = ref(null);
const payment = ref({ method: "", received: 0, change: 0 });
const categories = computed(() => ["All", ...categoryStore.items.map((category) => category.name)]);
const inventoryByProduct = computed(() => new Map(inventoryStore.items.map((item) => [item.productId, item.quantity])));
const readyKitchenOrders = computed(() => orders.readyForPayment.slice().sort((left, right) => new Date(left.createdAt) - new Date(right.createdAt)));
const receiptItems = computed(() => (receiptOrder.value?.items || cart.items).map((item, index) => ({
  ...item,
  id: item.productId ?? item.id,
  itemKey: item.itemKey || `${item.productId ?? item.id}-${item.selectedSize || "default"}-${index}`,
})));
const receiptSubtotal = computed(() => receiptOrder.value
  ? receiptOrder.value.items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
  : cart.total);
const receiptDiscount = computed(() => receiptOrder.value?.discount ?? discount.value);
const receiptTotal = computed(() => receiptOrder.value?.total ?? discountedTotal.value);
const receiptTaxRate = computed(() => Number(receiptOrder.value?.taxRate ?? settingsStore.taxRate));
const receiptType = computed(() => receiptOrder.value?.type ?? orderType.value);
const receiptTable = computed(() => receiptOrder.value?.table ?? (orderType.value === "Dine in" ? table.value : ""));
let orderRefreshTimer;

onMounted(() => {
  if (!categoryStore.items.length) categoryStore.load().catch(() => undefined);
  inventoryStore.load().catch(() => undefined);
  modifierStore.load().catch(() => undefined);
  settingsStore.load().catch(() => undefined);
  orders.loadOrders().catch(() => undefined);
  orderRefreshTimer = window.setInterval(() => orders.loadOrders().catch(() => undefined), 15000);
});

onUnmounted(() => window.clearInterval(orderRefreshTimer));

const filteredProducts = computed(() =>
  productStore.items.filter((product) => {
    const query = search.value.trim().toLowerCase();
    return (
      (activeCategory.value === "All" || product.category === activeCategory.value) &&
      (!query || `${product.name} ${product.category}`.toLowerCase().includes(query))
    );
  })
);
const discountedTotal = computed(() => Math.max(0, cart.total - discount.value) * (1 + Number(settingsStore.taxRate)));

async function sendOrderToKitchen() {
  if (!cart.items.length) return;
  orderError.value = "";
  sendingToKitchen.value = true;
  try {
    const order = await orders.sendToKitchen({
      createdAt: new Date().toISOString(),
      type: orderType.value,
      table: orderType.value === "Dine in" ? table.value : "",
      customer: "Walk-in customer",
      discount: Number(discount.value),
      taxRate: Number(settingsStore.taxRate),
      items: cart.items.map(({ id, name, quantity, price, selectedSize, modifiers }) => ({ productId: id, name, quantity, price, selectedSize, modifiers })),
    });
    cart.clear();
    discount.value = 0;
    notice.value = `Order #${order.id} sent to the kitchen. Payment is due when it is ready.`;
    window.setTimeout(() => { notice.value = ""; }, 6000);
  } catch (error) {
    orderError.value = error.message || "Could not send the order to the kitchen. Please try again.";
  } finally {
    sendingToKitchen.value = false;
  }
}

function continueToPayment(order) {
  orderError.value = "";
  receiptOrder.value = null;
  selectedKitchenOrder.value = order;
  showPayment.value = true;
}

function closePayment() {
  showPayment.value = false;
  selectedKitchenOrder.value = null;
}

async function completePayment(paymentDetails) {
  orderError.value = "";
  submittingOrder.value = true;
  try {
    const order = selectedKitchenOrder.value
      ? await orders.completeKitchenPayment(selectedKitchenOrder.value.id, paymentDetails.method)
      : await orders.addOrder({
        createdAt: new Date().toISOString(),
        status: "paid",
        type: orderType.value,
        table: orderType.value === "Dine in" ? table.value : "",
        customer: "Walk-in customer",
        paymentMethod: paymentDetails.method,
        discount: Number(discount.value),
        taxRate: Number(settingsStore.taxRate),
        total: discountedTotal.value,
        items: cart.items.map(({ id, name, quantity, price, selectedSize, modifiers }) => ({ productId: id, name, quantity, price, selectedSize, modifiers })),
      });
    inventoryStore.load().catch(() => undefined);
    inventoryStore.loadMovements().catch(() => undefined);
    savedOrderId.value = order.id;
    notice.value = `Order #${order.id} saved. Payment received via ${paymentDetails.method}.`;
    payment.value = paymentDetails;
    receiptOrder.value = order;
    selectedKitchenOrder.value = null;
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
  if (receiptOrder.value?.status === "paid") return;
  showReceipt.value = false;
  closePayment();
}

function previewBill() {
  showPayment.value = false;
  receiptOrder.value = selectedKitchenOrder.value;
  showReceipt.value = true;
}

function finishOrder() {
  showReceipt.value = false;
  savedOrderId.value = null;
  receiptOrder.value = null;
  selectedKitchenOrder.value = null;
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
          {{ settingsStore.restaurantName }}
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
    <section v-if="auth.can('orders:payment') && readyKitchenOrders.length" class="mx-5 mt-4 rounded-md border border-success/30 bg-success/5 px-4 py-4 lg:mx-8" aria-labelledby="ready-payments-heading">
      <div class="flex flex-col justify-between gap-3 sm:flex-row sm:items-center"><div><p class="text-xs font-bold uppercase tracking-[0.14em] text-success">Kitchen ready</p><h2 id="ready-payments-heading" class="mt-1 text-base font-bold text-ink">Ready for payment</h2></div><span class="text-xs text-muted">{{ readyKitchenOrders.length }} {{ readyKitchenOrders.length === 1 ? 'order' : 'orders' }}</span></div>
      <div class="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-3"><article v-for="order in readyKitchenOrders" :key="order.id" class="flex items-center justify-between gap-3 rounded-sm border border-border bg-surface px-3 py-3"><div class="min-w-0"><strong class="block truncate text-sm text-ink">Order #{{ order.id }} · {{ order.table || order.type }}</strong><span class="mt-1 block text-xs text-muted">{{ order.items.reduce((sum, item) => sum + item.quantity, 0) }} items · ${{ Number(order.total).toFixed(2) }}</span></div><BaseButton class="shrink-0 px-3 text-xs" @click="continueToPayment(order)">Continue to payment</BaseButton></article></div>
    </section>
    <p v-if="orderError" role="alert" class="mx-5 mt-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger lg:mx-8">{{ orderError }}</p>
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
            :modifier-groups="modifierStore.items"
            :inventory-quantity="inventoryByProduct.get(product.id)"
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
        :tax-rate="Number(settingsStore.taxRate)"
        :order-type="orderType"
        :table="table"
        :sending-to-kitchen="sendingToKitchen"
        :allow-direct-checkout="auth.can('orders:payment')"
        @increment="cart.addItem"
        @decrement="cart.decreaseItem"
        @remove="cart.removeItem"
        @clear="cart.clear"
        @update-discount="discount = $event"
        @checkout="showReceipt = true"
        @send-to-kitchen="sendOrderToKitchen"
      />
    </div>
    <PaymentModal
      :open="showPayment"
      :total="selectedKitchenOrder?.total ?? discountedTotal"
      :error="orderError"
      :submitting="submittingOrder"
      @close="closePayment"
      @edit="editBill"
      @print="previewBill"
      @paid="completePayment"
    />
    <ReceiptModal
      :open="showReceipt"
      :items="receiptItems"
      :subtotal="receiptSubtotal"
      :discount="receiptDiscount"
      :tax-rate="receiptTaxRate"
      :total="receiptTotal"
      :restaurant-name="settingsStore.restaurantName"
      :receipt-footer="settingsStore.receiptFooter"
      :order-type="receiptType"
      :table="receiptTable"
      :paid="Boolean(receiptOrder?.status === 'paid')"
      :received="payment.received"
      :change="payment.change"
      :payment-method="receiptOrder?.paymentMethod || payment.method"
      :order-id="receiptOrder?.id ?? savedOrderId"
      @close="showReceipt = false"
      @edit="editBill"
      @pay="showPayment = true"
      @save="finishOrder"
    />
  </section>
</template>
