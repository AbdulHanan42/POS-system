import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({ restaurantName: 'Restaurant POS', taxRate: 0.1 }),
})
