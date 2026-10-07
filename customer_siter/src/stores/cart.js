import { defineStore } from 'pinia'

const keyFor = (tenant) => `restaurant-cart:${tenant}`

export const useCartStore = defineStore('customer-cart', {
  state: () => ({ tenant: '', items: [] }),
  getters: {
    count: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    subtotal: (state) => state.items.reduce((sum, item) => sum + item.price * item.quantity, 0),
  },
  actions: {
    initialize(tenant) {
      if (this.tenant === tenant) return
      this.tenant = tenant
      try {
        this.items = JSON.parse(localStorage.getItem(keyFor(tenant)) || '[]')
      } catch {
        this.items = []
      }
    },
    persist() {
      if (this.tenant) localStorage.setItem(keyFor(this.tenant), JSON.stringify(this.items))
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