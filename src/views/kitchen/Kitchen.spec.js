import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { orderService } from '../../services/orderService.js'
import Kitchen from './Kitchen.vue'

enableAutoUnmount(afterEach)

vi.mock('../../services/orderService.js', () => ({
  orderService: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    updateStatus: vi.fn(),
    updateKitchenStatus: vi.fn(),
  },
}))

const queuedOrder = {
  id: 12,
  createdAt: '2026-10-04T08:30:00Z',
  status: 'paid',
  kitchenStatus: 'queued',
  type: 'Dine in',
  table: 'Table 02',
  customer: 'Walk-in customer',
  paymentMethod: 'Cash',
  total: 25,
  items: [{ productId: 1, name: 'Classic Burger', quantity: 2, price: 12.5, selectedSize: null, modifiers: [] }],
}

beforeEach(() => {
  vi.resetAllMocks()
  orderService.list.mockResolvedValue([queuedOrder])
  orderService.updateKitchenStatus.mockImplementation(async (id, kitchenStatus) => ({ ...queuedOrder, id, kitchenStatus }))
})

describe('Kitchen', () => {
  it('advances cooking progress without changing the payment status', async () => {
    const wrapper = mount(Kitchen, { global: { plugins: [createPinia()] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Classic Burger')
    const startButton = wrapper.findAll('button').find((button) => button.text().includes('Start preparing'))
    await startButton.trigger('click')
    await flushPromises()

    expect(orderService.updateKitchenStatus).toHaveBeenCalledWith(12, 'preparing')
    expect(wrapper.text()).toContain('Mark ready')
    expect(wrapper.text()).toContain('Preparing')
  })
})