import { defineStore } from 'pinia'
import { purchaseService } from '../services/purchaseService.js'

export const usePurchaseStore = defineStore('purchase', {
  state: () => ({ purchases: [], loading: false, saving: false, receivingId: null, error: '' }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.purchases = await purchaseService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async create(purchase) {
      this.saving = true
      this.error = ''
      try {
        const created = await purchaseService.create(purchase)
        this.purchases.unshift(created)
        return created
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.saving = false
      }
    },
    async receive(id) {
      this.receivingId = id
      this.error = ''
      try {
        const received = await purchaseService.receive(id)
        const index = this.purchases.findIndex((purchase) => purchase.id === received.id)
        if (index !== -1) this.purchases[index] = received
        return received
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.receivingId = null
      }
    },
  },
})