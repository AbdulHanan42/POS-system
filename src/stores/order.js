import { defineStore } from 'pinia'
import seedOrders from '../data/orders.js'

export const useOrderStore = defineStore('order', {
  state: () => ({ orders: [...seedOrders] }),
  getters: {
    paidOrders: (state) => state.orders.filter((order) => order.status === 'paid'),
  },
  actions: {
    addOrder(order) {
      this.orders.unshift({ ...order, id: order.id || String(Date.now()) })
    },
    updateStatus(id, status) {
      const order = this.orders.find((item) => item.id === id)
      if (order) order.status = status
    },
  },
})
