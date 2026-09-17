import { defineStore } from 'pinia'
import tables from '../data/tables.js'

export const useTableStore = defineStore('table', {
  state: () => ({ items: tables }),
})
