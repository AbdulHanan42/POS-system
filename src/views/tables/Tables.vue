<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus, Search, Pencil, Trash2, X } from 'lucide-vue-next'
import BaseModal from '../../components/common/BaseModal.vue'
import { useTableStore } from '../../stores/table.js'

const tableStore = useTableStore()
const search = ref('')
const activeStatus = ref('all')
const showForm = ref(false)
const editingTable = ref(null)
const deletingTable = ref(null)
const saving = ref(false)
const actionError = ref('')
const form = ref({ name: '', seats: 2, status: 'available' })

const statuses = [
  { value: 'all', label: 'All tables' },
  { value: 'available', label: 'Available' },
  { value: 'occupied', label: 'Occupied' },
  { value: 'reserved', label: 'Reserved' },
]
const counts = computed(() => Object.fromEntries(
  statuses.slice(1).map(({ value }) => [value, tableStore.items.filter((table) => table.status === value).length]),
))
const visibleTables = computed(() => {
  const query = search.value.trim().toLowerCase()
  return tableStore.items.filter((table) => {
    const matchesSearch = !query || table.name.toLowerCase().includes(query)
    return matchesSearch && (activeStatus.value === 'all' || table.status === activeStatus.value)
  })
})

onMounted(() => tableStore.load().catch(() => undefined))

function startCreate() {
  editingTable.value = null
  form.value = { name: '', seats: 2, status: 'available' }
  actionError.value = ''
  showForm.value = true
}

function startEdit(table) {
  editingTable.value = table
  form.value = { name: table.name, seats: table.seats, status: table.status }
  actionError.value = ''
  showForm.value = true
}

async function saveTable() {
  saving.value = true
  actionError.value = ''
  const payload = { ...form.value, seats: Number(form.value.seats) }
  try {
    if (editingTable.value) {
      await tableStore.update({ ...payload, id: editingTable.value.id })
    } else {
      await tableStore.add(payload)
    }
    showForm.value = false
  } catch (error) {
    actionError.value = error.message
  } finally {
    saving.value = false
  }
}

async function changeStatus(table, status) {
  actionError.value = ''
  try {
    await tableStore.update({ ...table, status })
  } catch (error) {
    actionError.value = error.message
  }
}

async function confirmDelete() {
  actionError.value = ''
  try {
    await tableStore.remove(deletingTable.value.id)
    deletingTable.value = null
  } catch (error) {
    actionError.value = error.message
  }
}

function statusClass(status) {
  return {
    available: 'bg-emerald-50 text-emerald-800',
    occupied: 'bg-orange-50 text-orange-800',
    reserved: 'bg-sky-50 text-sky-800',
  }[status]
}
</script>

<template>
  <section class="min-h-screen bg-background px-5 py-7 sm:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <header class="flex flex-col justify-between gap-5 border-b border-border pb-6 sm:flex-row sm:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Floor management</p>
          <h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Restaurant tables</h1>
          <p class="mt-2 text-sm text-muted">Manage seating, availability and reservations.</p>
        </div>
        <button type="button" class="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand" @click="startCreate">
          <Plus :size="17" aria-hidden="true" /> Add table
        </button>
      </header>

      <div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
        <article v-for="status in statuses.slice(1)" :key="status.value" class="rounded-md border border-border bg-surface px-4 py-3 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-wide text-muted">{{ status.label }}</p>
          <strong class="mt-1 block text-2xl text-ink">{{ counts[status.value] }}</strong>
        </article>
        <article class="col-span-2 flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white shadow-sm sm:col-span-1">
          <span class="text-sm font-medium text-white/75">Total tables</span>
          <strong class="text-2xl">{{ tableStore.items.length }}</strong>
        </article>
      </div>

      <p v-if="actionError" role="alert" class="mt-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger">{{ actionError }}</p>
      <div class="mt-6 flex flex-col gap-4 border-b border-border pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex flex-wrap gap-1" aria-label="Filter tables by status">
          <button v-for="status in statuses" :key="status.value" type="button" class="rounded-sm px-3 py-2 text-sm font-semibold transition-colors" :class="activeStatus === status.value ? 'bg-ink text-white' : 'text-muted hover:bg-white hover:text-ink'" :aria-pressed="activeStatus === status.value" @click="activeStatus = status.value">{{ status.label }}</button>
        </div>
        <label class="relative block w-full sm:max-w-xs">
          <span class="sr-only">Search tables</span>
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" />
          <input v-model="search" type="search" placeholder="Search table name" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm outline-none focus:border-brand" />
        </label>
      </div>

      <div v-if="tableStore.loading" class="py-16 text-center text-sm text-muted" role="status">Loading tables...</div>
      <div v-else-if="tableStore.error" class="py-16 text-center">
        <p class="text-sm text-danger">Could not load tables: {{ tableStore.error }}</p>
        <button type="button" class="mt-3 text-sm font-semibold text-brand hover:underline" @click="tableStore.load().catch(() => undefined)">Try again</button>
      </div>
      <div v-else-if="visibleTables.length" class="grid gap-4 py-5 sm:grid-cols-2 xl:grid-cols-3">
        <article v-for="table in visibleTables" :key="table.id" class="rounded-md border border-border bg-surface p-5 shadow-sm">
          <div class="flex items-start justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-ink">{{ table.name }}</h2>
              <p class="mt-1 text-sm text-muted">{{ table.seats }} {{ table.seats === 1 ? 'seat' : 'seats' }}</p>
            </div>
            <span class="rounded-sm px-2.5 py-1 text-xs font-bold capitalize" :class="statusClass(table.status)">{{ table.status }}</span>
          </div>
          <div class="mt-5 flex items-center justify-between border-t border-border pt-4">
            <label class="flex items-center gap-2 text-xs font-semibold text-muted">
              <span>Status</span>
              <select :value="table.status" :aria-label="`Status for ${table.name}`" class="h-9 rounded-sm border border-border bg-white px-2 text-sm font-medium capitalize text-ink outline-none focus:border-brand" @change="changeStatus(table, $event.target.value)">
                <option v-for="option in statuses.slice(1)" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <div class="flex gap-1">
              <button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-ink" :aria-label="`Edit ${table.name}`" @click="startEdit(table)"><Pencil :size="16" aria-hidden="true" /></button>
              <button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-red-50 hover:text-danger" :aria-label="`Delete ${table.name}`" @click="deletingTable = table; actionError = ''"><Trash2 :size="16" aria-hidden="true" /></button>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="py-16 text-center">
        <p class="font-semibold text-ink">{{ tableStore.items.length ? 'No matching tables' : 'No tables yet' }}</p>
        <p class="mt-1 text-sm text-muted">{{ tableStore.items.length ? 'Change the search or status filter.' : 'Add your first table to start managing the floor.' }}</p>
        <button v-if="!tableStore.items.length" type="button" class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand hover:underline" @click="startCreate"><Plus :size="16" aria-hidden="true" /> Add table</button>
      </div>
    </div>

    <BaseModal :open="showForm">
      <form class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl" @submit.prevent="saveTable">
        <div class="flex items-start justify-between">
          <div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Table details</p><h2 class="mt-1 text-xl font-bold text-ink">{{ editingTable ? 'Edit table' : 'Add table' }}</h2></div>
          <button type="button" class="grid size-8 place-items-center rounded-sm text-muted hover:bg-background" aria-label="Close table form" @click="showForm = false"><X :size="18" /></button>
        </div>
        <label class="mt-5 grid gap-2 text-sm font-semibold text-ink">Table name<input v-model.trim="form.name" required maxlength="80" autofocus class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" placeholder="e.g. Patio 1" /></label>
        <label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Seats<input v-model.number="form.seats" required type="number" min="1" max="50" class="h-10 rounded-sm border border-border px-3 font-normal outline-none focus:border-brand" /></label>
        <label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Status<select v-model="form.status" class="h-10 rounded-sm border border-border bg-white px-3 font-normal outline-none focus:border-brand"><option v-for="status in statuses.slice(1)" :key="status.value" :value="status.value">{{ status.label }}</option></select></label>
        <p v-if="actionError" role="alert" class="mt-4 text-sm text-danger">{{ actionError }}</p>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" :disabled="saving" @click="showForm = false">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="saving">{{ saving ? 'Saving...' : editingTable ? 'Save changes' : 'Add table' }}</button></div>
      </form>
    </BaseModal>

    <BaseModal :open="Boolean(deletingTable)">
      <div class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl">
        <h2 class="text-lg font-bold text-ink">Delete table?</h2>
        <p class="mt-2 text-sm leading-6 text-muted">Remove <strong class="text-ink">{{ deletingTable?.name }}</strong> from the floor plan?</p>
        <p v-if="actionError" role="alert" class="mt-3 text-sm text-danger">{{ actionError }}</p>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" @click="deletingTable = null">Cancel</button><button type="button" class="min-h-10 rounded-sm bg-danger px-4 text-sm font-semibold text-white hover:bg-red-800" @click="confirmDelete">Delete table</button></div>
      </div>
    </BaseModal>
  </section>
</template>