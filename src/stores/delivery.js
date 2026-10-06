import { defineStore } from 'pinia'
import { deliveryService } from '../services/deliveryService.js'

export const useDeliveryStore = defineStore('delivery', {
  state: () => ({
    zones: [],
    deliveryOrders: [],
    loading: false,
    error: '',
    initialized: false,
  }),
  actions: {
    async loadZones() {
      this.loading = true
      this.error = ''
      try {
        this.zones = await deliveryService.getZones()
        this.initialized = true
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async createZone(zoneData) {
      this.loading = true
      this.error = ''
      try {
        const zone = await deliveryService.createZone(zoneData)
        this.zones.push(zone)
        return zone
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateZone(id, zoneData) {
      this.loading = true
      this.error = ''
      try {
        const updated = await deliveryService.updateZone(id, zoneData)
        const index = this.zones.findIndex((z) => z.id === id)
        if (index !== -1) {
          this.zones[index] = updated
        }
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async deleteZone(id) {
      this.loading = true
      this.error = ''
      try {
        await deliveryService.deleteZone(id)
        this.zones = this.zones.filter((z) => z.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async loadDeliveryOrders() {
      this.loading = true
      this.error = ''
      try {
        this.deliveryOrders = await deliveryService.getDeliveryOrders()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async updateDeliveryStatus(orderId, statusData) {
      this.loading = true
      this.error = ''
      try {
        const updated = await deliveryService.updateDeliveryStatus(orderId, statusData)
        const index = this.deliveryOrders.findIndex((o) => o.id === orderId)
        if (index !== -1) {
          this.deliveryOrders[index] = updated
        }
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
  },
})
