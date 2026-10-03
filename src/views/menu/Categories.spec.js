import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { categoryService } from '../../services/categoryService.js'
import { useProductStore } from '../../stores/product.js'
import Categories from './Categories.vue'

vi.mock('../../services/categoryService.js', () => ({
  categoryService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
}))

const seededCategory = { id: 1, name: 'Mains', description: 'Main courses.', isPizza: false, productCount: 2 }

function mountCategories() {
  return mount(Categories, { global: { plugins: [createPinia()] } })
}

describe('Categories', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    categoryService.list.mockResolvedValue([seededCategory])
    categoryService.create.mockImplementation(async (category) => ({ ...category, id: 2, productCount: 0 }))
    categoryService.update.mockImplementation(async (id, category) => ({ ...category, id, productCount: 0 }))
    categoryService.remove.mockResolvedValue({ message: 'Category deleted' })
  })

  it('loads categories, creates and renames one, and prevents deleting assigned categories', async () => {
    const pinia = createPinia()
    const wrapper = mount(Categories, { global: { plugins: [pinia] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Mains')
    expect(wrapper.get('button[aria-label="Delete Mains"]').element.disabled).toBe(true)

    await wrapper.findAll('button').find((button) => button.text().trim() === 'Add category').trigger('click')
    await wrapper.get('input[placeholder="e.g. Breakfast"]').setValue('Breakfast')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(categoryService.create).toHaveBeenCalledWith({ name: 'Breakfast', description: '', isPizza: false })
    expect(wrapper.text()).toContain('Breakfast')

    const productStore = useProductStore(pinia)
    productStore.items = [{ id: 9, name: 'Pancakes', category: 'Breakfast' }]
    await wrapper.get('button[aria-label="Edit Breakfast"]').trigger('click')
    await wrapper.get('input[placeholder="e.g. Breakfast"]').setValue('Morning')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(categoryService.update).toHaveBeenCalledWith(2, { name: 'Morning', description: '', isPizza: false, id: 2 })
    expect(wrapper.text()).toContain('Morning')
    expect(productStore.items[0].category).toBe('Morning')

    await wrapper.get('button[aria-label="Delete Morning"]').trigger('click')
    await wrapper.findAll('button').find((button) => button.text().trim() === 'Delete category').trigger('click')
    await flushPromises()
    expect(categoryService.remove).toHaveBeenCalledWith(2)
  })
})
