<script setup>
import { computed, onMounted, ref } from 'vue'
import { Plus, Search, Pencil, Trash2, X, Tag } from 'lucide-vue-next'
import { useCategoryStore } from '../../stores/category.js'

const categoryStore = useCategoryStore()
const search = ref('')
const showForm = ref(false)
const editingCategory = ref(null)
const deletingCategory = ref(null)
const saving = ref(false)
const actionError = ref('')
const form = ref({ name: '', description: '', isPizza: false })

const visibleCategories = computed(() => {
  const query = search.value.trim().toLowerCase()
  return categoryStore.items.filter((category) =>
    `${category.name} ${category.description}`.toLowerCase().includes(query),
  )
})
const totalProducts = computed(() => categoryStore.items.reduce((sum, category) => sum + category.productCount, 0))

onMounted(() => categoryStore.load().catch(() => undefined))

function startCreate() {
  editingCategory.value = null
  form.value = { name: '', description: '', isPizza: false }
  actionError.value = ''
  showForm.value = true
}

function startEdit(category) {
  editingCategory.value = category
  form.value = { name: category.name, description: category.description, isPizza: category.isPizza }
  actionError.value = ''
  showForm.value = true
}

async function saveCategory() {
  saving.value = true
  actionError.value = ''
  const payload = {
    name: form.value.name.trim(),
    description: form.value.description.trim(),
    isPizza: form.value.isPizza,
  }
  try {
    if (editingCategory.value) {
      await categoryStore.update({ ...payload, id: editingCategory.value.id })
    } else {
      await categoryStore.add(payload)
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
    await categoryStore.remove(deletingCategory.value.id)
    deletingCategory.value = null
  } catch (error) {
    actionError.value = error.message
  }
}
</script>

<template>
  <section class="min-h-screen bg-background px-5 py-7 sm:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <header class="flex flex-col justify-between gap-5 border-b border-border pb-6 sm:flex-row sm:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu management</p>
          <h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Categories</h1>
          <p class="mt-2 text-sm text-muted">Organize menu items into clear sections.</p>
        </div>
        <button type="button" class="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand" @click="startCreate"><Plus :size="17" aria-hidden="true" /> Add category</button>
      </header>

      <div class="mt-6 grid gap-3 sm:grid-cols-2">
        <article class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-sm font-medium text-muted">Categories</span><strong class="text-2xl text-ink">{{ categoryStore.items.length }}</strong></article>
        <article class="flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white shadow-sm"><span class="text-sm font-medium text-white/75">Products categorized</span><strong class="text-2xl">{{ totalProducts }}</strong></article>
      </div>

      <div class="mt-6 flex flex-col gap-4 border-b border-border pb-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-muted"><strong class="text-ink">{{ visibleCategories.length }}</strong> categories</p>
        <label class="relative block w-full sm:max-w-xs"><span class="sr-only">Search categories</span><Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" /><input v-model="search" type="search" placeholder="Search categories" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none focus:border-brand" /></label>
      </div>

      <p v-if="actionError" role="alert" class="mb-4 rounded-sm border border-border bg-background px-4 py-3 text-sm text-danger">{{ actionError }}</p>
      <div v-if="categoryStore.loading" class="py-16 text-center text-sm text-muted" role="status">Loading categories...</div>
      <div v-else-if="categoryStore.error" class="py-16 text-center"><p class="text-sm text-danger">Could not load categories: {{ categoryStore.error }}</p><button type="button" class="mt-3 text-sm font-semibold text-brand hover:underline" @click="categoryStore.load().catch(() => undefined)">Try again</button></div>
      <div v-else-if="visibleCategories.length" class="grid gap-4 py-5 sm:grid-cols-2 xl:grid-cols-3">
        <article v-for="category in visibleCategories" :key="category.id" class="rounded-md border border-border bg-surface p-5 shadow-sm">
          <div class="flex items-start justify-between gap-3">
            <div class="flex min-w-0 items-start gap-3"><span class="grid size-10 shrink-0 place-items-center rounded-sm bg-background text-brand"><Tag :size="18" aria-hidden="true" /></span><div class="min-w-0"><h2 class="truncate text-lg font-bold text-ink">{{ category.name }}</h2><p class="mt-1 min-h-10 text-sm leading-5 text-muted">{{ category.description || 'No description' }}</p></div></div>
            <span v-if="category.isPizza" class="shrink-0 rounded-sm bg-background px-2 py-1 text-xs font-bold text-brand">Size pricing</span>
          </div>
          <div class="mt-4 flex items-center justify-between border-t border-border pt-4"><p class="text-sm text-muted"><strong class="text-ink">{{ category.productCount }}</strong> {{ category.productCount === 1 ? 'product' : 'products' }}</p><div class="flex gap-1"><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-ink" :aria-label="`Edit ${category.name}`" @click="startEdit(category)"><Pencil :size="16" aria-hidden="true" /></button><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-danger disabled:cursor-not-allowed disabled:opacity-40" :aria-label="`Delete ${category.name}`" :disabled="category.productCount > 0" :title="category.productCount ? 'Move products out of this category before deleting it' : 'Delete category'" @click="deletingCategory = category; actionError = ''"><Trash2 :size="16" aria-hidden="true" /></button></div></div>
        </article>
      </div>
      <div v-else class="py-16 text-center"><p class="font-semibold text-ink">{{ categoryStore.items.length ? 'No matching categories' : 'No categories yet' }}</p><p class="mt-1 text-sm text-muted">{{ categoryStore.items.length ? 'Try another search.' : 'Create a category to organize your menu.' }}</p><button v-if="!categoryStore.items.length" type="button" class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand hover:underline" @click="startCreate"><Plus :size="16" aria-hidden="true" /> Add category</button></div>
    </div>

    <div v-if="showForm" class="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="category-form-title">
      <form class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl" @submit.prevent="saveCategory">
        <div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Menu organization</p><h2 id="category-form-title" class="mt-1 text-xl font-bold text-ink">{{ editingCategory ? 'Edit category' : 'Add category' }}</h2></div><button type="button" class="grid size-8 place-items-center rounded-sm text-muted hover:bg-background" aria-label="Close category form" @click="showForm = false"><X :size="18" aria-hidden="true" /></button></div>
        <label class="mt-5 grid gap-2 text-sm font-semibold text-ink">Category name<input v-model.trim="form.name" required maxlength="80" autofocus class="h-10 rounded-sm border border-border bg-surface px-3 font-normal text-ink outline-none focus:border-brand" placeholder="e.g. Breakfast" /></label>
        <label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Description <span class="font-normal text-muted">Optional</span><textarea v-model.trim="form.description" maxlength="240" rows="3" class="rounded-sm border border-border bg-surface px-3 py-2 font-normal text-ink outline-none focus:border-brand" placeholder="What belongs in this category?" /></label>
        <label class="mt-4 flex cursor-pointer items-start gap-3 rounded-sm border border-border p-3 text-sm text-ink"><input v-model="form.isPizza" type="checkbox" class="mt-0.5 size-4 accent-brand" /><span><strong class="block">Use size-based pricing</strong><span class="mt-1 block text-xs text-muted">Show small, medium and large price fields on products in this category.</span></span></label>
        <p v-if="actionError" role="alert" class="mt-4 text-sm text-danger">{{ actionError }}</p>
        <div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" :disabled="saving" @click="showForm = false">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="saving">{{ saving ? 'Saving...' : editingCategory ? 'Save changes' : 'Add category' }}</button></div>
      </form>
    </div>

    <div v-if="deletingCategory" class="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="delete-category-title"><div class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl"><h2 id="delete-category-title" class="text-lg font-bold text-ink">Delete category?</h2><p class="mt-2 text-sm leading-6 text-muted">Delete <strong class="text-ink">{{ deletingCategory.name }}</strong>? This action cannot be undone.</p><p v-if="actionError" role="alert" class="mt-3 text-sm text-danger">{{ actionError }}</p><div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" @click="deletingCategory = null">Cancel</button><button type="button" class="min-h-10 rounded-sm bg-danger px-4 text-sm font-semibold text-white hover:bg-red-800" @click="confirmDelete">Delete category</button></div></div></div>
  </section>
</template>