import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const total = computed(() => items.value.reduce((sum, item) => sum + item.price * item.quantity, 0))

  function addItem(product) {
    const itemKey = `${product.id}-${product.selectedSize || 'default'}`
    const existingItem = items.value.find((item) => item.itemKey === itemKey)
    if (existingItem) {
      existingItem.quantity += 1
      return
    }
    items.value.push({ ...product, itemKey, quantity: 1 })
  }

  function decreaseItem(product) {
    const existingItem = items.value.find((item) => item.itemKey === product.itemKey)
    if (!existingItem) return
    if (existingItem.quantity === 1) {
      removeItem(product)
      return
    }
    existingItem.quantity -= 1
  }

  function removeItem(product) {
    items.value = items.value.filter((item) => item.itemKey !== product.itemKey)
  }

  function clear() {
    items.value = []
  }

  return { items, total, addItem, decreaseItem, removeItem, clear }
})
