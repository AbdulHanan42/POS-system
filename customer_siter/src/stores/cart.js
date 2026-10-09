import { defineStore } from 'pinia'

const keyFor = (tenant, customerId) =>
  `restaurant-cart:${tenant}:${customerId ? `customer:${customerId}` : 'guest'}`

export const useCartStore = defineStore('customer-cart', {
  state: () => ({ tenant: '', customerId: null, items: [] }),
  getters: {
    count: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    subtotal: (state) => state.items.reduce((sum, item) => sum + item.price * item.quantity, 0),
  },
  actions: {
    initialize(tenant, customerId = null) {
      if (this.tenant === tenant && this.customerId === customerId) return
      this.tenant = tenant
      this.customerId = customerId
      try {
        this.items = JSON.parse(localStorage.getItem(keyFor(tenant, customerId)) || '[]')
      } catch {
        this.items = []
      }
    },
    persist() {
      if (this.tenant) {
        localStorage.setItem(keyFor(this.tenant, this.customerId), JSON.stringify(this.items))
      }
    },
    add(product, size, price) {
      const existing = this.items.find((item) => item.productId === product.id && item.size === size)
      if (existing) existing.quantity += 1
      else this.items.push({ productId: product.id, name: product.name, image: product.image, size, price, quantity: 1 })
      this.persist()
    },
    setQuantity(item, quantity) {
      if (quantity < 1) this.items = this.items.filter((line) => line !== item)
      else item.quantity = quantity
      this.persist()
    },
    clear() {
      this.items = []
      this.persist()
    },
  },
})