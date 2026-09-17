import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePosStore = defineStore('pos', () => {
  const activeCategory = ref('All')
  const searchTerm = ref('')
  return { activeCategory, searchTerm }
})
