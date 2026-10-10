<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { LogOut, MapPin, Plus, Trash2, User } from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";
import { customerAuth } from "../services/customerAuth";

const router = useRouter();
const auth = useAuthStore();

const showAddressModal = ref(false);
const addressForm = ref({
  label: "Home",
  address: "",
  zone: "",
  isDefault: false,
});
const editingAddress = ref(null);
const addresses = ref([]);
const orders = ref([]);
const loading = ref(false);
const error = ref("");

const customer = computed(() => auth.customer);

onMounted(async () => {
  await Promise.all([loadAddresses(), loadOrders()]);
});

async function loadAddresses() {
  loading.value = true;
  error.value = "";
  try {
    addresses.value = await customerAuth.getAddresses();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function loadOrders() {
  loading.value = true;
  error.value = "";
  try {
    orders.value = await customerAuth.getOrders();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function handleLogout() {
  await auth.logout();
  router.push("/login");
}

function openAddressModal(address = null) {
  if (address) {
    editingAddress.value = address;
    addressForm.value = { ...address };
  } else {
    editingAddress.value = null;
    addressForm.value = {
      label: "Home",
      address: "",
      zone: "",
      isDefault: false,
    };
  }
  showAddressModal.value = true;
}

async function saveAddress() {
  loading.value = true;
  error.value = "";
  try {
    if (editingAddress.value) {
      await customerAuth.updateAddress(editingAddress.value.id, addressForm.value);
    } else {
      await customerAuth.createAddress(addressForm.value);
    }
    showAddressModal.value = false;
    editingAddress.value = null;
    await loadAddresses();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function deleteAddress(id) {
  if (!confirm("Are you sure you want to delete this address?")) return;
  loading.value = true;
  error.value = "";
  try {
    await customerAuth.deleteAddress(id);
    await loadAddresses();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

const statusLabels = {
  awaiting_payment: "Awaiting payment",
  paid: "Paid",
  refunded: "Refunded",
};

const deliveryStatusLabels = {
  pending: "Pending",
  confirmed: "Confirmed",
  preparing: "Preparing",
  ready: "Ready",
  out_for_delivery: "Out for delivery",
  delivered: "Delivered",
  cancelled: "Cancelled",
};
</script>

<template>
  <main class="min-h-screen bg-[var(--paper)] px-5 py-8">
    <div class="mx-auto max-w-4xl">
      <header class="mb-8 flex items-center justify-between border-b border-stone-200 pb-6">
        <div>
          <h1 class="font-serif text-3xl text-[var(--forest)]">My Profile</h1>
          <p class="mt-1 text-sm text-[var(--muted)]">Manage your account and orders</p>
        </div>
        <button
          @click="handleLogout"
          class="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-stone-600 hover:text-[var(--forest)]"
        >
          <LogOut :size="18" />
          Sign out
        </button>
      </header>

      <p v-if="error" class="mb-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
        {{ error }}
      </p>

      <!-- Profile Info -->
      <section class="mb-8 rounded-md border border-stone-200 bg-white p-6">
        <h2 class="mb-4 text-lg font-semibold text-[var(--ink)]">Account Information</h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <span class="block text-xs text-[var(--muted)]">Name</span>
            <p class="text-sm font-medium text-[var(--ink)]">{{ customer?.name }}</p>
          </div>
          <div>
            <span class="block text-xs text-[var(--muted)]">Email</span>
            <p class="text-sm font-medium text-[var(--ink)]">{{ customer?.email }}</p>
          </div>
          <div>
            <span class="block text-xs text-[var(--muted)]">Phone</span>
            <p class="text-sm font-medium text-[var(--ink)]">{{ customer?.phone || "Not provided" }}</p>
          </div>
        </div>
      </section>

      <!-- Saved Addresses -->
      <section class="mb-8">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-[var(--ink)]">Saved Addresses</h2>
          <button
            @click="openAddressModal()"
            class="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-[var(--forest)] hover:bg-[var(--forest)]/10"
          >
            <Plus :size="18" />
            Add address
          </button>
        </div>

        <div v-if="addresses.length === 0" class="rounded-md border border-dashed border-stone-300 bg-white p-8 text-center text-sm text-[var(--muted)]">
          No saved addresses yet
        </div>

        <div v-else class="grid gap-4 sm:grid-cols-2">
          <article
            v-for="addr in addresses"
            :key="addr.id"
            class="rounded-md border border-stone-200 bg-white p-4"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-[var(--ink)]">{{ addr.label }}</span>
                  <span
                    v-if="addr.isDefault"
                    class="rounded-full bg-[var(--forest)]/10 px-2 py-0.5 text-xs font-semibold text-[var(--forest)]"
                  >
                    Default
                  </span>
                </div>
                <p class="mt-1 text-sm text-[var(--muted)]">{{ addr.address }}</p>
                <p class="mt-1 text-sm text-[var(--muted)]">Zone: {{ addr.zone }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="openAddressModal(addr)"
                  class="p-2 text-stone-400 hover:text-[var(--forest)]"
                  title="Edit"
                >
                  <MapPin :size="18" />
                </button>
                <button
                  @click="deleteAddress(addr.id)"
                  class="p-2 text-stone-400 hover:text-red-600"
                  title="Delete"
                >
                  <Trash2 :size="18" />
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Order History -->
      <section>
        <h2 class="mb-4 text-lg font-semibold text-[var(--ink)]">Order History</h2>

        <div v-if="orders.length === 0" class="rounded-md border border-dashed border-stone-300 bg-white p-8 text-center text-sm text-[var(--muted)]">
          No orders yet
        </div>

        <div v-else class="space-y-4">
          <article
            v-for="order in orders"
            :key="order.id"
            class="rounded-md border border-stone-200 bg-white p-4"
          >
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold text-[var(--ink)]">Order #{{ order.id }}</p>
                <p class="mt-1 text-sm text-[var(--muted)]">
                  {{ new Date(order.createdAt).toLocaleDateString() }} · {{ order.items.length }} items
                </p>
                <p class="mt-1 text-sm text-[var(--muted)]">
                  Total: ${{ Number(order.total).toFixed(2) }}
                </p>
              </div>
              <div class="text-right">
                <span class="block text-xs text-[var(--muted)]">Status</span>
                <p class="text-sm font-medium text-[var(--ink)]">{{ statusLabels[order.status] || order.status }}</p>
                <p v-if="order.deliveryStatus" class="text-sm text-[var(--muted)]">
                  {{ deliveryStatusLabels[order.deliveryStatus] || order.deliveryStatus }}
                </p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- Address Modal -->
      <div
        v-if="showAddressModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      >
        <div class="w-full max-w-md rounded-md border border-stone-200 bg-white p-6 shadow-xl">
          <h2 class="text-lg font-bold text-[var(--ink)]">
            {{ editingAddress ? "Edit Address" : "Add Address" }}
          </h2>
          <form @submit.prevent="saveAddress" class="mt-4 space-y-4">
            <label class="block">
              <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Label</span>
              <input
                v-model="addressForm.label"
                required
                class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
                placeholder="Home, Work, etc."
              />
            </label>
            <label class="block">
              <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Address</span>
              <textarea
                v-model="addressForm.address"
                required
                rows="2"
                class="w-full border border-stone-300 bg-white px-3 py-2 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)] resize-y"
                placeholder="Street address, apartment, etc."
              />
            </label>
            <label class="block">
              <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Delivery Zone</span>
              <input
                v-model="addressForm.zone"
                required
                class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
                placeholder="Zone name"
              />
            </label>
            <label class="flex items-center gap-2">
              <input
                v-model="addressForm.isDefault"
                type="checkbox"
                class="h-4 w-4"
              />
              <span class="text-sm text-[var(--ink)]">Set as default address</span>
            </label>
            <div class="flex justify-end gap-2 pt-4">
              <button
                type="button"
                @click="showAddressModal = false"
                class="px-4 py-2 text-sm font-semibold text-stone-600 hover:text-[var(--ink)]"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="px-4 py-2 text-sm font-semibold bg-[var(--forest)] text-white hover:bg-[#1f3b30] disabled:opacity-50"
              >
                {{ loading ? "Saving..." : "Save" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </main>
</template>
