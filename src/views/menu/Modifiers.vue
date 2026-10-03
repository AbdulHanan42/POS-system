<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus, Search, Pencil, Trash2, X, SlidersHorizontal } from 'lucide-vue-next'
import { useModifierStore } from '../../stores/modifier.js'
import { useProductStore } from '../../stores/product.js'

const modifierStore = useModifierStore()
const productStore = useProductStore()
const search = ref('')
const showForm = ref(false)
const editingGroup = ref(null)
const deletingGroup = ref(null)
const saving = ref(false)
const actionError = ref('')
const form = ref(blankForm())

function blankForm() {
  return {
    name: '',
    description: '',
    isRequired: false,
    allowMultiple: false,
    productIds: [],
    options: [{ name: '', price: 0 }],
  }
}

const visibleGroups = computed(() => {
  const query = search.value.trim().toLowerCase()
  return modifierStore.items.filter((group) =>
    `${group.name} ${group.description} ${group.options.map((option) => option.name).join(' ')}`.toLowerCase().includes(query),
  )
})
const totalOptions = computed(() => modifierStore.items.reduce((sum, group) => sum + group.options.length, 0))
const productNames = computed(() => new Map(productStore.items.map((product) => [product.id, product.name])))

onMounted(() => {
  modifierStore.load().catch(() => undefined)
  if (!productStore.items.length) productStore.loadProducts().catch(() => undefined)
})

function startCreate() {
  editingGroup.value = null
  form.value = blankForm()
  actionError.value = ''
  showForm.value = true
}

function startEdit(group) {
  editingGroup.value = group
  form.value = {
    name: group.name,
    description: group.description,
    isRequired: group.isRequired,
    allowMultiple: group.allowMultiple,
    productIds: [...group.productIds],
    options: group.options.map((option) => ({ ...option })),
  }
  actionError.value = ''
  showForm.value = true
}

function addOption() {
  form.value.options.push({ name: '', price: 0 })
}

function removeOption(index) {
  if (form.value.options.length > 1) form.value.options.splice(index, 1)
}

async function saveGroup() {
  saving.value = true
  actionError.value = ''
  const payload = {
    name: form.value.name.trim(),
    description: form.value.description.trim(),
    isRequired: form.value.isRequired,
    allowMultiple: form.value.allowMultiple,
    productIds: [...form.value.productIds],
    options: form.value.options.map((option) => ({ name: option.name.trim(), price: Number(option.price) })),
  }
  if (payload.options.some((option) => !option.name)) {
    actionError.value = 'Enter a name for every modifier option.'
    saving.value = false
    return
  }
  try {
    if (editingGroup.value) {
      await modifierStore.update({ ...payload, id: editingGroup.value.id })
    } else {
      await modifierStore.add(payload)
    }
    showForm.value = false
  } catch (error) {
    actionError.value = error.message
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  actionError.value = ''
  try {
    await modifierStore.remove(deletingGroup.value.id)
    deletingGroup.value = null
  } catch (error) {
    actionError.value = error.message
  }
}

function assignedProducts(group) {
  if (!group.productIds.length) return 'All products'
  const names = group.productIds.map((id) => productNames.value.get(id)).filter(Boolean)
  return names.length ? names.join(', ') : `${group.productIds.length} assigned products`
}

const formatPrice = (value) => Number(value) === 0 ? 'Free' : `+$${Number(value).toFixed(2)}`
</script>

<template>
  <section class="min-h-screen bg-background px-5 py-7 sm:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <header class="flex flex-col justify-between gap-5 border-b border-border pb-6 lg:flex-row lg:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu management</p>
          <h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Modifiers</h1>
          <p class="mt-2 text-sm text-muted">Set up add-ons and choices for your menu items.</p>
        </div>
        <button type="button" class="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand" @click="startCreate"><Plus :size="17" aria-hidden="true" /> Add modifier group</button>
      </header>

      <div class="mt-6 grid gap-3 sm:grid-cols-3">
        <article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Modifier groups</span><strong class="text-2xl text-ink">{{ modifierStore.items.length }}</strong></article>
        <article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Options</span><strong class="text-2xl text-ink">{{ totalOptions }}</strong></article>
        <article class="flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white shadow-sm"><span class="text-sm font-medium text-white/75">Menu products</span><strong class="text-2xl">{{ productStore.items.length }}</strong></article>
      </div>

      <div class="mt-6 flex flex-col gap-4 border-b border-border pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-muted"><strong class="text-ink">{{ visibleGroups.length }}</strong> modifier groups</p>
        <label class="relative block w-full sm:max-w-xs"><span class="sr-only">Search modifier groups</span><Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" /><input v-model="search" type="search" placeholder="Search modifiers" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none focus:border-brand" /></label>
      </div>

      <div v-if="actionError" role="alert" class="mb-4 rounded-sm border border-border bg-background px-4 py-3 text-sm text-danger">{{ actionError }}</div>
      <div v-if="modifierStore.loading" role="status" class="py-16 text-center text-sm text-muted">Loading modifier groups...</div>
      <div v-else-if="modifierStore.error" class="py-16 text-center"><p class="text-sm text-danger">Could not load modifiers: {{ modifierStore.error }}</p><button type="button" class="mt-3 text-sm font-semibold text-brand hover:underline" @click="modifierStore.load().catch(() => undefined)">Try again</button></div>
      <div v-else-if="visibleGroups.length" class="grid gap-4 py-5 sm:grid-cols-2 xl:grid-cols-3">
        <article v-for="group in visibleGroups" :key="group.id" class="rounded-md border border-border bg-surface p-5 shadow-sm">
          <div class="flex items-start justify-between gap-3"><div class="flex min-w-0 items-start gap-3"><span class="grid size-10 shrink-0 place-items-center rounded-sm bg-background text-brand"><SlidersHorizontal :size="18" aria-hidden="true" /></span><div class="min-w-0"><h2 class="truncate text-lg font-bold text-ink">{{ group.name }}</h2><p class="mt-1 min-h-10 text-sm leading-5 text-muted">{{ group.description || 'No description' }}</p></div></div><div class="flex gap-1"><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-ink" :aria-label="`Edit ${group.name}`" @click="startEdit(group)"><Pencil :size="16" aria-hidden="true" /></button><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-danger" :aria-label="`Delete ${group.name}`" @click="deletingGroup = group; actionError = ''"><Trash2 :size="16" aria-hidden="true" /></button></div></div>
          <div class="mt-3 flex flex-wrap gap-2"><span class="rounded-sm bg-background px-2 py-1 text-xs font-semibold text-muted">{{ group.isRequired ? 'Required' : 'Optional' }}</span><span class="rounded-sm bg-background px-2 py-1 text-xs font-semibold text-muted">{{ group.allowMultiple ? 'Choose multiple' : 'Choose one' }}</span></div>
          <ul class="mt-4 grid gap-2 border-t border-border pt-4"><li v-for="option in group.options" :key="option.name" class="flex items-center justify-between gap-3 text-sm"><span class="text-ink">{{ option.name }}</span><strong class="shrink-0 text-muted">{{ formatPrice(option.price) }}</strong></li></ul>
          <p class="mt-4 border-t border-border pt-3 text-xs leading-5 text-muted"><span class="font-semibold text-ink">Applies to:</span> {{ assignedProducts(group) }}</p>
        </article>
      </div>
      <div v-else class="py-16 text-center"><p class="font-semibold text-ink">{{ modifierStore.items.length ? 'No matching modifier groups' : 'No modifier groups yet' }}</p><p class="mt-1 text-sm text-muted">{{ modifierStore.items.length ? 'Try a different search.' : 'Create a group of choices to offer product add-ons.' }}</p><button v-if="!modifierStore.items.length" type="button" class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand hover:underline" @click="startCreate"><Plus :size="16" aria-hidden="true" /> Add modifier group</button></div>
    </div>

    <div v-if="showForm" class="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="modifier-form-title">
      <form class="my-auto w-full max-w-2xl rounded-md bg-surface p-6 shadow-xl" @submit.prevent="saveGroup">
        <div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu setup</p><h2 id="modifier-form-title" class="mt-1 text-xl font-bold text-ink">{{ editingGroup ? 'Edit modifier group' : 'Add modifier group' }}</h2></div><button type="button" class="grid size-8 place-items-center rounded-sm text-muted hover:bg-background" aria-label="Close modifier form" @click="showForm = false"><X :size="18" aria-hidden="true" /></button></div>
        <div class="mt-5 grid gap-4 sm:grid-cols-2"><label class="grid gap-2 text-sm font-semibold text-ink">Group name<input v-model.trim="form.name" required maxlength="80" autofocus class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="e.g. Extra toppings" /></label><label class="grid gap-2 text-sm font-semibold text-ink">Description <span class="font-normal text-muted">Optional</span><input v-model.trim="form.description" maxlength="240" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="Shown to staff at checkout" /></label></div>
        <fieldset class="mt-5"><legend class="text-sm font-semibold text-ink">Selection rules</legend><div class="mt-2 grid gap-2 sm:grid-cols-2"><label class="flex cursor-pointer items-start gap-3 rounded-sm border border-border p-3 text-sm text-ink"><input v-model="form.isRequired" type="checkbox" class="mt-0.5 size-4 accent-brand" /><span><strong class="block">Require a choice</strong><span class="mt-1 block text-xs text-muted">Staff must choose at least one option.</span></span></label><label class="flex cursor-pointer items-start gap-3 rounded-sm border border-border p-3 text-sm text-ink"><input v-model="form.allowMultiple" type="checkbox" class="mt-0.5 size-4 accent-brand" /><span><strong class="block">Allow multiple options</strong><span class="mt-1 block text-xs text-muted">Permit more than one option from this group.</span></span></label></div></fieldset>
        <fieldset class="mt-5"><legend class="text-sm font-semibold text-ink">Assigned products</legend><p class="mt-1 text-xs text-muted">Leave all unchecked to apply this group to every product.</p><div class="mt-2 grid max-h-40 gap-1 overflow-y-auto rounded-sm border border-border p-2 sm:grid-cols-2"><label v-for="product in productStore.items" :key="product.id" class="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-ink hover:bg-background"><input v-model="form.productIds" type="checkbox" :value="product.id" class="size-4 accent-brand" /><span class="truncate">{{ product.name }}</span><span class="ml-auto shrink-0 text-xs text-muted">{{ product.category }}</span></label><p v-if="!productStore.items.length" class="p-2 text-sm text-muted">No products loaded.</p></div></fieldset>
        <fieldset class="mt-5"><div class="flex items-center justify-between"><legend class="text-sm font-semibold text-ink">Options</legend><button type="button" class="inline-flex min-h-8 items-center gap-1 rounded-sm px-2 text-xs font-semibold text-brand hover:bg-background" @click="addOption"><Plus :size="14" aria-hidden="true" /> Add option</button></div><div class="mt-2 grid gap-2"><div v-for="(option, index) in form.options" :key="index" class="grid grid-cols-[minmax(0,1fr)_8rem_2.5rem] items-end gap-2"><label class="grid gap-1 text-xs font-semibold text-muted">Option name<input v-model.trim="option.name" required maxlength="80" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-brand" placeholder="e.g. Cheddar" /></label><label class="grid gap-1 text-xs font-semibold text-muted">Extra price<input v-model.number="option.price" required type="number" min="0" step="0.01" class="h-10 rounded-sm border border-border bg-surface px-3 text-sm font-normal text-ink outline-none focus:border-brand" /></label><button type="button" class="grid size-10 place-items-center rounded-sm text-muted hover:bg-background hover:text-danger disabled:opacity-40" :aria-label="`Remove option ${index + 1}`" :disabled="form.options.length === 1" @click="removeOption(index)"><Trash2 :size="16" aria-hidden="true" /></button></div></div></fieldset>
        <p v-if="actionError" role="alert" class="mt-4 text-sm text-danger">{{ actionError }}</p>
        <div class="mt-6 flex justify-end gap-2 border-t border-border pt-4"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" :disabled="saving" @click="showForm = false">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="saving">{{ saving ? 'Saving...' : editingGroup ? 'Save changes' : 'Add modifier group' }}</button></div>
      </form>
    </div>

    <div v-if="deletingGroup" class="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="delete-modifier-title"><div class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl"><h2 id="delete-modifier-title" class="text-lg font-bold text-ink">Delete modifier group?</h2><p class="mt-2 text-sm leading-6 text-muted">Remove <strong class="text-ink">{{ deletingGroup.name }}</strong> and all of its options?</p><p v-if="actionError" role="alert" class="mt-3 text-sm text-danger">{{ actionError }}</p><div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" @click="deletingGroup = null">Cancel</button><button type="button" class="min-h-10 rounded-sm bg-danger px-4 text-sm font-semibold text-white hover:opacity-90" @click="confirmDelete">Delete group</button></div></div></div>
  </section>
</template>