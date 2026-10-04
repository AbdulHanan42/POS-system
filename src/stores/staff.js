import { defineStore } from 'pinia'
import { staffService } from '../services/staffService.js'

export const useStaffStore = defineStore('staff', {
  state: () => ({ items: [], loading: false, error: '' }),
  getters: {
    activeMembers: (state) => state.items.filter((member) => member.status === 'active'),
  },
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.items = await staffService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async add(staffMember) {
      this.error = ''
      try {
        const created = await staffService.create(staffMember)
        this.items.push(created)
        return created
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    async update(staffMember) {
      this.error = ''
      try {
        const updated = await staffService.update(staffMember.id, staffMember)
        const index = this.items.findIndex((member) => member.id === updated.id)
        if (index !== -1) this.items[index] = updated
        return updated
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    async remove(id) {
      this.error = ''
      try {
        await staffService.remove(id)
        this.items = this.items.filter((member) => member.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
  },
})