import { defineStore } from 'pinia'
import { orderService } from '../services/orderService.js'

export const useOrderStore = defineStore('order', {
  state: () => ({ orders: [], loading: false, error: '' }),
  getters: {
    paidOrders: (state) => state.orders.filter((order) => order.status === 'paid'),
    waitingForKitchen: (state) => state.orders.filter((order) => order.status === 'awaiting_payment'),
    readyForPayment: (state) => state.orders.filter((order) => order.status === 'awaiting_payment' && order.kitchenStatus === 'ready'),
  },
  actions: {
    async loadOrders() {
      this.loading = true
      this.error = ''
      try {
        this.orders = await orderService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async addOrder(order) {
      this.error = ''
      try {
        const created = await orderService.create(order)
        this.orders.unshift(created)
        return created
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async sendToKitchen(order) {
      this.error = ''
      try {
        const created = await orderService.createKitchenOrder(order)
        this.orders.unshift(created)
        return created
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async completeKitchenPayment(id, paymentMethod) {
      this.error = ''
      try {
        const updated = await orderService.completeKitchenPayment(id, paymentMethod)
        const index = this.orders.findIndex((item) => item.id === updated.id)
        if (index === -1) this.orders.unshift(updated)
        else this.orders[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async updateStatus(id, status) {
      this.error = ''
      try {
        const updated = await orderService.updateStatus(id, status)
        const index = this.orders.findIndex((item) => item.id === updated.id)
        if (index !== -1) this.orders[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async updateKitchenStatus(id, kitchenStatus) {
      this.error = ''
      try {
        const updated = await orderService.updateKitchenStatus(id, kitchenStatus)
        const index = this.orders.findIndex((item) => item.id === updated.id)
        if (index !== -1) this.orders[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
  },
})
