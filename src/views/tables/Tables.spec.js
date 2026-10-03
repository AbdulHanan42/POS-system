import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { tableService } from '../../services/tableService.js'
import Tables from './Tables.vue'

vi.mock('../../services/tableService.js', () => ({
  tableService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
}))

const initialTable = { id: 12, name: 'Patio 1', seats: 4, status: 'available' }

function mountTables() {
  return mount(Tables, { global: { plugins: [createPinia()] } })
}

describe('Tables', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
    tableService.list.mockResolvedValue([initialTable])
    tableService.create.mockImplementation(async (table) => ({ ...table, id: 13 }))
    tableService.update.mockImplementation(async (id, table) => ({ ...table, id }))
    tableService.remove.mockResolvedValue({ message: 'Table deleted' })
  })

  it('loads tables, creates a table, and updates its status', async () => {
    const wrapper = mountTables()
    await flushPromises()

    expect(wrapper.text()).toContain('Patio 1')
    expect(tableService.list).toHaveBeenCalledOnce()

    const tableStatus = wrapper.find('select[aria-label="Status for Patio 1"]')
    await tableStatus.setValue('occupied')
    await flushPromises()
    expect(tableService.update).toHaveBeenCalledWith(12, { ...initialTable, status: 'occupied' })

    const addButton = wrapper.findAll('button').find((button) => button.text().trim() === 'Add table')
    await addButton.trigger('click')
    const form = wrapper.find('form')
    await form.find('input[maxlength="80"]').setValue('Window 2')
    await form.find('input[type="number"]').setValue('2')
    await form.trigger('submit')
    await flushPromises()

    expect(tableService.create).toHaveBeenCalledWith({ name: 'Window 2', seats: 2, status: 'available' })
    expect(wrapper.text()).toContain('Window 2')
  })
})
