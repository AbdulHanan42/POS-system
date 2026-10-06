import { defineStore } from 'pinia'
import { settingsService } from '../services/settingsService.js'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    id: null,
    restaurantName: 'Restaurant POS',
    email: '',
    phone: '',
    address: '',
    taxRate: 0.1,
    receiptFooter: '',
    updatedAt: null,
    initialized: false,
    loading: false,
    saving: false,
    error: '',
  }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const settings = await settingsService.get()
        Object.assign(this, settings)
        this.initialized = true
        return settings
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async save() {
      this.saving = true
      this.error = ''
      try {
        const settings = await settingsService.update({
          restaurantName: this.restaurantName.trim(),
          email: this.email.trim(),
          phone: this.phone.trim(),
          address: this.address.trim(),
          taxRate: Number(this.taxRate),
          receiptFooter: this.receiptFooter.trim(),
        })
        Object.assign(this, settings)
        return settings
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.saving = false
      }
    },
  },
})
