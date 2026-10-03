import { defineStore } from 'pinia'
import { inventoryService } from '../services/inventoryService.js'

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: [],
    movements: [],
    loading: false,
    loadingMovements: false,
    error: '',
    movementError: '',
  }),
  getters: {
    lowStockItems: (state) => state.items.filter((item) => item.quantity > 0 && item.quantity <= item.reorderLevel),
    outOfStockItems: (state) => state.items.filter((item) => item.quantity === 0),
    totalStockValue: (state) => state.items.reduce((total, item) => total + item.stockValue, 0),
  },
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.items = await inventoryService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async loadMovements(productId) {
      this.loadingMovements = true
      this.movementError = ''
      try {
        this.movements = await inventoryService.movements(productId)
      } catch (error) {
        this.movementError = error.message
        throw error
      } finally {
        this.loadingMovements = false
      }
    },
    async adjust(adjustment) {
      this.error = ''
      try {
        const updated = await inventoryService.adjust(adjustment)
        const index = this.items.findIndex((item) => item.productId === updated.productId)
        if (index !== -1) this.items[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    async updateReorderLevel(productId, reorderLevel) {
      this.error = ''
      try {
        const updated = await inventoryService.updateReorderLevel(productId, reorderLevel)
        const index = this.items.findIndex((item) => item.productId === productId)
        if (index !== -1) this.items[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
  },
})