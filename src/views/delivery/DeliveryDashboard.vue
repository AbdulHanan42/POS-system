<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useDeliveryStore } from '../../stores/delivery.js'
import { useAuthStore } from '../../stores/auth.js'

const deliveryStore = useDeliveryStore()
const auth = useAuthStore()
const activeTab = ref('orders')
const showZoneModal = ref(false)
const zoneForm = ref({
  name: '',
  description: '',
  fee: 0,
  minOrderAmount: 0,
  estimatedTime: 30,
  status: 'active',
})
const editingZone = ref(null)
const loading = ref(false)
const deliveryError = ref('')
let deliveryRefreshTimer

const deliveryOrders = computed(() => deliveryStore.deliveryOrders)
const zones = computed(() => deliveryStore.zones)

onMounted(() => {
  loadDeliveryData()
  deliveryRefreshTimer = window.setInterval(() => {
    deliveryStore.loadDeliveryOrders().catch((error) => { deliveryError.value = error.message })
  }, 15000)
})

onUnmounted(() => window.clearInterval(deliveryRefreshTimer))

async function loadDeliveryData() {
  try {
    await Promise.all([
      deliveryStore.loadDeliveryOrders(),
      deliveryStore.loadZones(),
    ])
  } catch (error) {
    console.error('Failed to load delivery data:', error)
  }
}

async function updateDeliveryStatus(orderId, status) {
  loading.value = true
  deliveryError.value = ''
  try {
    await deliveryStore.updateDeliveryStatus(orderId, {
      deliveryStatus: status,
      actualDeliveryTime: status === 'delivered' ? new Date().toISOString() : null,
    })
  } catch (error) {
    deliveryError.value = error.message
    console.error('Failed to update delivery status:', error)
  } finally {
    loading.value = false
  }
}

function openZoneModal(zone = null) {
  if (zone) {
    editingZone.value = zone
    zoneForm.value = { ...zone }
  } else {
    editingZone.value = null
    zoneForm.value = {
      name: '',
      description: '',
      fee: 0,
      minOrderAmount: 0,
      estimatedTime: 30,
      status: 'active',
    }
  }
  showZoneModal.value = true
}

async function saveZone() {
  loading.value = true
  try {
    if (editingZone.value) {
      await deliveryStore.updateZone(editingZone.value.id, zoneForm.value)
    } else {
      await deliveryStore.createZone(zoneForm.value)
    }
    showZoneModal.value = false
    editingZone.value = null
  } catch (error) {
    console.error('Failed to save zone:', error)
  } finally {
    loading.value = false
  }
}

async function deleteZone(id) {
  if (!confirm('Are you sure you want to delete this delivery zone?')) return
  loading.value = true
  try {
    await deliveryStore.deleteZone(id)
  } catch (error) {
    console.error('Failed to delete zone:', error)
  } finally {
    loading.value = false
  }
}

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  preparing: 'bg-blue-100 text-blue-800',
  out_for_delivery: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const statusLabels = {
  pending: 'Pending',
  preparing: 'Preparing',
  out_for_delivery: 'Out for Delivery',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}
</script>

<template>
  <section class="min-h-screen bg-background px-5 py-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <header class="border-b border-border pb-6">
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Delivery Management</p>
        <h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Delivery Dashboard</h1>
        <p class="mt-2 text-sm text-muted">Track and manage delivery orders and zones.</p>
      </header>

      <div class="mt-5 flex gap-1 border-b border-border" role="tablist">
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'orders'"
          class="rounded-t-sm px-4 py-3 text-sm font-semibold"
          :class="activeTab === 'orders' ? 'border-b-2 border-brand text-ink' : 'text-muted hover:text-ink'"
          @click="activeTab = 'orders'"
        >
          Active Deliveries ({{ deliveryOrders.length }})
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'zones'"
          class="rounded-t-sm px-4 py-3 text-sm font-semibold"
          :class="activeTab === 'zones' ? 'border-b-2 border-brand text-ink' : 'text-muted hover:text-ink'"
          @click="activeTab = 'zones'"
        >
          Delivery Zones ({{ zones.length }})
        </button>
      </div>

      <!-- Orders Tab -->
      <div v-if="activeTab === 'orders'" class="mt-6">
        <p v-if="deliveryError" role="alert" class="mb-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger">{{ deliveryError }}</p>
        <div v-if="deliveryOrders.length === 0" class="py-12 text-center text-sm text-muted">
          No active delivery orders.
        </div>
        <div v-else class="grid gap-4">
          <article
            v-for="order in deliveryOrders"
            :key="order.id"
            class="rounded-md border border-border bg-surface p-4 shadow-sm"
          >
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="rounded-full px-2 py-1 text-xs font-semibold" :class="statusColors[order.deliveryStatus] || 'bg-gray-100 text-gray-800'">
                    {{ statusLabels[order.deliveryStatus] || order.deliveryStatus }}
                  </span>
                  <strong class="text-ink">Order #{{ order.id }}</strong>
                </div>
                <p class="mt-1 text-sm text-muted">
                  {{ order.customer }} · {{ order.type }}
                </p>
                <p v-if="order.customerPhone" class="mt-1 text-sm text-muted">{{ order.customerPhone }}</p>
                <p v-if="order.source === 'website'" class="mt-1 text-xs font-semibold text-brand">Online website order</p>
                <p class="mt-1 text-sm text-ink">
                  <span class="font-semibold">Address:</span> {{ order.deliveryAddress || 'N/A' }}
                </p>
                <p class="mt-1 text-sm text-ink">
                  <span class="font-semibold">Zone:</span> {{ order.deliveryZone || 'N/A' }}
                </p>
                <p v-if="order.deliveryNotes" class="mt-1 text-sm text-muted">
                  <span class="font-semibold">Notes:</span> {{ order.deliveryNotes }}
                </p>
                <p class="mt-2 text-sm font-semibold text-ink">
                  Total: ${{ Number(order.total).toFixed(2) }}
                  <span v-if="order.deliveryFee" class="text-muted"> (includes ${{ Number(order.deliveryFee).toFixed(2) }} delivery fee)</span>
                </p>
              </div>
              <div class="flex flex-col gap-2">
                <select
                  :value="order.deliveryStatus"
                  @change="updateDeliveryStatus(order.id, $event.target.value)"
                  :disabled="loading"
                  class="h-10 rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand"
                >
                  <option value="pending">Pending</option>
                  <option value="preparing">Preparing</option>
                  <option value="out_for_delivery">Out for Delivery</option>
                  <option value="delivered" :disabled="order.source === 'website' && order.status === 'awaiting_payment' && order.kitchenStatus !== 'ready'">Delivered</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </div>
          </article>
        </div>
      </div>

      <!-- Zones Tab -->
      <div v-if="activeTab === 'zones'" class="mt-6">
        <div class="mb-4 flex justify-end">
          <button
            v-if="auth.can('settings:manage')"
            type="button"
            class="rounded-sm bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-dark"
            @click="openZoneModal()"
          >
            Add Zone
          </button>
        </div>
        <div v-if="zones.length === 0" class="py-12 text-center text-sm text-muted">
          No delivery zones configured.
        </div>
        <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="zone in zones"
            :key="zone.id"
            class="rounded-md border border-border bg-surface p-4 shadow-sm"
          >
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-semibold text-ink">{{ zone.name }}</h3>
                <p v-if="zone.description" class="mt-1 text-sm text-muted">{{ zone.description }}</p>
              </div>
              <span
                class="rounded-full px-2 py-1 text-xs font-semibold"
                :class="zone.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ zone.status }}
              </span>
            </div>
            <div class="mt-3 space-y-1 text-sm">
              <p class="text-ink"><span class="font-semibold">Fee:</span> ${{ Number(zone.fee).toFixed(2) }}</p>
              <p class="text-ink"><span class="font-semibold">Min Order:</span> ${{ Number(zone.minOrderAmount).toFixed(2) }}</p>
              <p class="text-ink"><span class="font-semibold">Est. Time:</span> {{ zone.estimatedTime }} min</p>
            </div>
            <div v-if="auth.can('settings:manage')" class="mt-4 flex gap-2">
              <button
                type="button"
                class="rounded-sm border border-border px-3 py-1 text-sm text-ink hover:bg-background"
                @click="openZoneModal(zone)"
              >
                Edit
              </button>
              <button
                type="button"
                class="rounded-sm border border-red-200 px-3 py-1 text-sm text-danger hover:bg-red-50"
                @click="deleteZone(zone.id)"
              >
                Delete
              </button>
            </div>
          </article>
        </div>
      </div>

      <!-- Zone Modal -->
      <div v-if="showZoneModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div class="w-full max-w-md rounded-md border border-border bg-surface p-6 shadow-xl">
          <h2 class="text-lg font-bold text-ink">{{ editingZone ? 'Edit Zone' : 'Add Zone' }}</h2>
          <form class="mt-4 grid gap-4" @submit.prevent="saveZone">
            <label class="grid gap-2 text-sm font-semibold text-ink">
              Zone Name
              <input v-model="zoneForm.name" required class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-ink">
              Description
              <textarea v-model="zoneForm.description" rows="2" class="rounded-sm border border-border bg-surface px-3 py-2 font-normal outline-none focus:border-brand" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-ink">
              Delivery Fee ($)
              <input v-model.number="zoneForm.fee" type="number" min="0" step="0.01" required class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-ink">
              Min Order Amount ($)
              <input v-model.number="zoneForm.minOrderAmount" type="number" min="0" step="0.01" required class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-ink">
              Estimated Time (minutes)
              <input v-model.number="zoneForm.estimatedTime" type="number" min="5" required class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" />
            </label>
            <label class="grid gap-2 text-sm font-semibold text-ink">
              Status
              <select v-model="zoneForm.status" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" class="rounded-sm border border-border px-4 py-2 text-sm font-semibold text-ink hover:bg-background" @click="showZoneModal = false">
                Cancel
              </button>
              <button type="submit" :disabled="loading" class="rounded-sm bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50">
                {{ loading ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>
