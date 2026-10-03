import { defineStore } from 'pinia'
import { tableService } from '../services/tableService.js'

export const useTableStore = defineStore('table', {
  state: () => ({ items: [], loading: false, error: '' }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.items = await tableService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async add(table) {
      const created = await tableService.create(table)
      this.items.push(created)
      return created
    },
    async update(table) {
      const updated = await tableService.update(table.id, table)
      const index = this.items.findIndex((item) => item.id === table.id)
      if (index !== -1) this.items[index] = updated
      return updated
    },
    async remove(id) {
      await tableService.remove(id)
      this.items = this.items.filter((table) => table.id !== id)
    },
  },
})
