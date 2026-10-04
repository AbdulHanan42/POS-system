import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { productService } from '../../services/productService.js'
import { purchaseService } from '../../services/purchaseService.js'
import CreatePurchase from './CreatePurchase.vue'
import Purchases from './Purchases.vue'

vi.mock('../../services/productService.js', () => ({ productService: { list: vi.fn() } }))
vi.mock('../../services/purchaseService.js', () => ({ purchaseService: { list: vi.fn(), create: vi.fn(), receive: vi.fn() } }))

const products = [
  { id: 1, name: 'Beans', category: 'Pantry', price: 4, status: 'active' },
  { id: 2, name: 'Rice', category: 'Pantry', price: 3, status: 'active' },
]
const pendingPurchase = {
  id: 10,
  supplier: 'Market Supply',
  status: 'pending',
  createdAt: '2026-10-03T09:00:00Z',
  total: 12,
  items: [{ productId: 1, productName: 'Beans', quantity: 3, unitCost: 4, lineTotal: 12 }],
}
const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/purchases', component: Purchases }] })

async function mountWithRouter(component) {
  await router.push('/purchases')
  await router.isReady()
  return mount(component, { global: { plugins: [createPinia(), router] } })
}

beforeEach(() => {
  vi.resetAllMocks()
  productService.list.mockResolvedValue(products)
  purchaseService.list.mockResolvedValue([pendingPurchase])
  purchaseService.create.mockResolvedValue(pendingPurchase)
  purchaseService.receive.mockResolvedValue({ ...pendingPurchase, status: 'received' })
})

describe('Purchases', () => {
  it('creates a supplier purchase with product quantities and unit costs', async () => {
    const wrapper = await mountWithRouter(CreatePurchase)
    await flushPromises()
    await wrapper.get('input[autocomplete="organization"]').setValue('Market Supply')
    await wrapper.get('select').setValue('1')
    const numbers = wrapper.findAll('input[type="number"]')
    await numbers[0].setValue('3')
    await numbers[1].setValue('4')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(purchaseService.create).toHaveBeenCalledWith({
      supplier: 'Market Supply',
      items: [{ productId: 1, quantity: 3, unitCost: 4 }],
    })
  })

  it('receives a pending purchase from the list', async () => {
    const wrapper = await mountWithRouter(Purchases)
    await flushPromises()
    const receiveButton = wrapper.findAll('button').find((button) => button.text().includes('Receive stock'))
    await receiveButton.trigger('click')
    await flushPromises()

    expect(purchaseService.receive).toHaveBeenCalledWith(10)
    expect(wrapper.text()).toContain('Stock added')
    expect(wrapper.text()).toContain('Received')
  })
})