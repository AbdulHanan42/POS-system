import { defineStore } from 'pinia'
import customers from '../data/customers.js'

export const useCustomerStore = defineStore('customer', {
  state: () => ({ items: [...customers] }),
  actions: {
    addCustomer(customer) {
      this.items.push({ ...customer, id: Date.now(), totalOrders: 0, totalSpent: 0, lastOrder: 'No orders yet', recentOrders: [] })
    },
    updateCustomer(customer) {
      const index = this.items.findIndex((item) => item.id === customer.id)
      if (index !== -1) this.items[index] = { ...this.items[index], ...customer }
    },
    deleteCustomer(id) {
      this.items = this.items.filter((customer) => customer.id !== id)
    },
  },
})
