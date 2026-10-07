<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import AppSidebar from '../components/layout/AppSidebar.vue'
import { useOrderStore } from '../stores/order.js'

const orders = useOrderStore()
const onlineOrderAlert = ref('')
let socket
let reconnectTimer
let alertTimer
let isDisposed = false

function connectOrderEvents() {
  if (isDisposed) return
  const token = localStorage.getItem('restopilot.accessToken')
  if (!token) return
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const socketUrl = `${protocol}//${window.location.host}/api/ws/pos/orders`
  socket = new WebSocket(socketUrl, [`pos-token.${token}`, 'pos-orders'])
  socket.addEventListener('message', (message) => {
    const event = JSON.parse(message.data)
    orders.loadOrders().catch(() => undefined)
    if (event.type === 'order.created' && event.source === 'website') {
      onlineOrderAlert.value = `New online order #${event.orderId}`
      window.clearTimeout(alertTimer)
      alertTimer = window.setTimeout(() => { onlineOrderAlert.value = '' }, 8000)
    }
  })
  socket.addEventListener('close', () => {
    if (!isDisposed) reconnectTimer = window.setTimeout(connectOrderEvents, 3000)
  })
  socket.addEventListener('error', () => socket.close())
}

onMounted(() => {
  isDisposed = false
  connectOrderEvents()
})
onUnmounted(() => {
  isDisposed = true
  window.clearTimeout(reconnectTimer)
  window.clearTimeout(alertTimer)
  socket?.close()
})
</script>

<template>
  <div class="default-layout">
    <AppSidebar />
    <main class="min-w-0"><RouterView /></main>
    <Transition name="online-alert">
      <button v-if="onlineOrderAlert" class="online-order-alert" type="button" @click="$router.push('/orders')" aria-live="assertive">
        {{ onlineOrderAlert }} · View orders
      </button>
    </Transition>
  </div>
</template>

<style scoped>
.default-layout {
  display: flex;
  min-height: 100vh;
}

main {
  flex: 1;
}

.online-order-alert {
  position: fixed;
  z-index: 60;
  right: 1.25rem;
  bottom: 1.25rem;
  border: 0;
  border-radius: 3px;
  padding: .9rem 1.1rem;
  background: #284b3d;
  color: white;
  box-shadow: 0 8px 24px #0003;
  font-size: .85rem;
  font-weight: 700;
}

.online-alert-enter-active,.online-alert-leave-active { transition: opacity .18s ease, transform .18s ease; }
.online-alert-enter-from,.online-alert-leave-to { opacity: 0; transform: translateY(8px); }
</style>
