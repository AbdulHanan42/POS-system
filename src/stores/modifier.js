import { defineStore } from 'pinia'
import { modifierService } from '../services/modifierService.js'

export const useModifierStore = defineStore('modifier', {
  state: () => ({ items: [], loading: false, error: '' }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.items = await modifierService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async add(group) {
      this.error = ''
      try {
        const created = await modifierService.create(group)
        this.items.push(created)
        this.items.sort((left, right) => left.name.localeCompare(right.name))
        return created
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    async update(group) {
      this.error = ''
      try {
        const updated = await modifierService.update(group.id, group)
        const index = this.items.findIndex((item) => item.id === updated.id)
        if (index !== -1) this.items[index] = updated
        this.items.sort((left, right) => left.name.localeCompare(right.name))
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    async remove(id) {
      this.error = ''
      try {
        await modifierService.remove(id)
        this.items = this.items.filter((group) => group.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
  },
})