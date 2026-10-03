import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { inventoryService } from '../../services/inventoryService.js'
import Inventory from './Inventory.vue'

vi.mock('../../services/inventoryService.js', () => ({
  inventoryService: {
    list: vi.fn(),
    movements: vi.fn(),
    adjust: vi.fn(),
    updateReorderLevel: vi.fn(),
  },
}))

const stockItems = [
  { productId: 1, name: 'Beans', category: 'Pantry', image: null, unitPrice: 4, quantity: 2, reorderLevel: 5, updatedAt: '2026-10-03T09:00:00Z', stockValue: 8, status: 'low_stock' },
  { productId: 2, name: 'Rice', category: 'Pantry', image: null, unitPrice: 3, quantity: 0, reorderLevel: 4, updatedAt: '2026-10-03T09:00:00Z', stockValue: 0, status: 'out_of_stock' },
]

beforeEach(() => {
  vi.resetAllMocks()
  inventoryService.list.mockResolvedValue(stockItems)
  inventoryService.movements.mockResolvedValue([])
  inventoryService.adjust.mockResolvedValue({ ...stockItems[0], quantity: 5, stockValue: 20, status: 'low_stock' })
  inventoryService.updateReorderLevel.mockResolvedValue({ ...stockItems[0], quantity: 5, reorderLevel: 8, stockValue: 20, status: 'low_stock' })
})

describe('Inventory', () => {
  it('filters stock and records stock adjustments and reorder levels', async () => {
    const wrapper = mount(Inventory, { global: { plugins: [createPinia()] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Beans')
    expect(wrapper.text()).toContain('Rice')
    expect(wrapper.text()).toContain('Out of stock')

    await wrapper.findAll('button').find((button) => button.text().includes('Low stock')).trigger('click')
    expect(wrapper.text()).toContain('Beans')
    expect(wrapper.get('section[aria-labelledby="stock-heading"] tbody').text()).not.toContain('Rice')

    await wrapper.get('button[aria-label="Receive Beans"]').trigger('click')
    const adjustmentForm = wrapper.get('form')
    await adjustmentForm.get('input[type="number"]').setValue('3')
    await adjustmentForm.get('input[placeholder="e.g. Supplier delivery"]').setValue('Supplier delivery')
    await adjustmentForm.trigger('submit')
    await flushPromises()
    expect(inventoryService.adjust).toHaveBeenCalledWith({ productId: 1, movementType: 'stock_in', quantity: 3, reason: 'Supplier delivery' })

    await wrapper.get('button[aria-label="Set reorder level for Beans"]').trigger('click')
    const reorderForm = wrapper.get('form')
    await reorderForm.get('input[type="number"]').setValue('8')
    await reorderForm.trigger('submit')
    await flushPromises()
    expect(inventoryService.updateReorderLevel).toHaveBeenCalledWith(1, 8)
  })
})
