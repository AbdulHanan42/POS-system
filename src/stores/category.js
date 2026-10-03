import { defineStore } from 'pinia'
import { categoryService } from '../services/categoryService.js'
import { useProductStore } from './product.js'

export const useCategoryStore = defineStore('category', {
  state: () => ({ items: [], loading: false, error: '' }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.items = await categoryService.list()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    async add(category) {
      this.error = ''
      try {
        const created = await categoryService.create(category)
        this.items.push(created)
        this.items.sort((left, right) => left.name.localeCompare(right.name))
        return created
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    async update(category) {
      this.error = ''
      try {
        const current = this.items.find((item) => item.id === category.id)
        const updated = await categoryService.update(category.id, category)
        const index = this.items.findIndex((item) => item.id === updated.id)
        if (index !== -1) this.items[index] = updated
        if (current && current.name !== updated.name) {
          const productStore = useProductStore()
          productStore.items = productStore.items.map((product) =>
            product.category === current.name ? { ...product, category: updated.name } : product,
          )
        }
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
        await categoryService.remove(id)
        this.items = this.items.filter((category) => category.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
  },
})