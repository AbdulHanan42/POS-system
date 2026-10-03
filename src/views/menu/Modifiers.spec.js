import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { modifierService } from '../../services/modifierService.js'
import { useProductStore } from '../../stores/product.js'
import Modifiers from './Modifiers.vue'
import ProductCard from '../../components/pos/ProductCard.vue'

vi.mock('../../services/modifierService.js', () => ({
  modifierService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
}))

const product = { id: 31, name: 'House burger', category: 'Mains', price: 10 }

beforeEach(() => {
  vi.resetAllMocks()
  modifierService.list.mockResolvedValue([])
  modifierService.create.mockImplementation(async (group) => ({ ...group, id: 7 }))
  modifierService.update.mockImplementation(async (id, group) => ({ ...group, id }))
  modifierService.remove.mockResolvedValue({ message: 'Modifier group deleted' })
})

describe('Modifiers management', () => {
  it('creates a modifier group with options and product assignments', async () => {
    const pinia = createPinia()
    useProductStore(pinia).items = [product]
    const wrapper = mount(Modifiers, { global: { plugins: [pinia] } })
    await flushPromises()

    await wrapper.findAll('button').find((button) => button.text().includes('Add modifier group')).trigger('click')
    await wrapper.get('input[placeholder="e.g. Extra toppings"]').setValue('Burger extras')
    await wrapper.get('input[placeholder="e.g. Cheddar"]').setValue('Cheddar')
    await wrapper.get('input[type="number"]').setValue('1.25')
    await wrapper.findAll('label').find((label) => label.text().includes('House burger')).get('input').setValue(true)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(modifierService.create).toHaveBeenCalledWith({
      name: 'Burger extras',
      description: '',
      isRequired: false,
      allowMultiple: false,
      productIds: [31],
      options: [{ name: 'Cheddar', price: 1.25 }],
    })
    expect(wrapper.text()).toContain('Burger extras')
  })
})

describe('POS modifier pricing', () => {
  it('requires a choice and includes its price and details when adding a product', async () => {
    const group = {
      id: 5,
      name: 'Extras',
      description: '',
      isRequired: true,
      allowMultiple: false,
      productIds: [31],
      options: [{ name: 'Avocado', price: 2 }],
    }
    const wrapper = mount(ProductCard, {
      props: { product, modifierGroups: [group] },
      global: { plugins: [createPinia()] },
    })

    await wrapper.get('button').trigger('click')
    const confirmButton = () => wrapper.findAll('button').find((button) => button.text().trim() === 'Add to order')
    expect(confirmButton().element.disabled).toBe(true)
    await wrapper.get('input[type="radio"]').setValue('Avocado')
    expect(wrapper.text()).toContain('$12.00')
    await confirmButton().trigger('click')

    expect(wrapper.emitted('add')[0][0]).toMatchObject({
      id: 31,
      price: 12,
      modifiers: [{ group: 'Extras', name: 'Avocado', price: 2 }],
    })
  })
})
