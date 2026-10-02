import { defineStore } from 'pinia'
import { productService } from '../services/productService.js'

export const useProductStore = defineStore('product', {
  state: () => ({ items: [], loading: false, error: '' }),
  getters: {
    categories: (state) => [...new Set(state.items.map((product) => product.category))],
  },
  actions: {
    async loadProducts() {
      this.loading = true
      this.error = ''
      try {
        this.items = await productService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async addProduct(product) {
      this.error = ''
      try {
        const created = await productService.create({ ...product, status: product.status || 'active' })
        this.items.push(created)
        return created
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async updateProduct(product) {
      this.error = ''
      try {
        const updated = await productService.update(product.id, product)
        const index = this.items.findIndex((item) => item.id === updated.id)
        if (index !== -1) this.items[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async deleteProduct(id) {
      this.error = ''
      try {
        await productService.remove(id)
        this.items = this.items.filter((product) => product.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async toggleStatus(product) {
      return await this.updateProduct({
        ...product,
        status: product.status === 'active' ? 'inactive' : 'active',
      })
    },
  },
})
