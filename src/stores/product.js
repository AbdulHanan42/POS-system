import { defineStore } from 'pinia'
import products from '../data/products.js'

export const useProductStore = defineStore('product', {
  state: () => ({ items: [...products] }),
  getters: {
    categories: (state) => [...new Set(state.items.map((product) => product.category))],
  },
  actions: {
    addProduct(product) {
      this.items.push({ ...product, id: Date.now(), status: product.status || 'active' })
    },
    updateProduct(product) {
      const index = this.items.findIndex((item) => item.id === product.id)
      if (index !== -1) this.items[index] = { ...product }
    },
    deleteProduct(id) {
      this.items = this.items.filter((product) => product.id !== id)
    },
    toggleStatus(product) {
      product.status = product.status === 'active' ? 'inactive' : 'active'
    },
  },
})
