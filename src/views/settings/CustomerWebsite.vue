<script setup>
import { computed, onMounted, ref } from 'vue'
import { ExternalLink, Plus, RefreshCw } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import DeleteProductModal from '../../components/products/DeleteProductModal.vue'
import ProductFilter from '../../components/products/ProductFilter.vue'
import ProductSearch from '../../components/products/ProductSearch.vue'
import ProductTable from '../../components/products/ProductTable.vue'
import { useAuthStore } from '../../stores/auth.js'
import { useProductStore } from '../../stores/product.js'
import { useSettingsStore } from '../../stores/settings.js'

const router = useRouter()
const auth = useAuthStore()
const products = useProductStore()
const settings = useSettingsStore()
const search = ref('')
const category = ref('All')
const status = ref('all')
const productToDelete = ref(null)
const pageError = ref('')
const savedMessage = ref('')

const visibleProducts = computed(() => products.items.filter((product) => {
  const matchesSearch = product.name.toLowerCase().includes(search.value.toLowerCase())
  const matchesCategory = category.value === 'All' || product.category === category.value
  const matchesStatus = status.value === 'all' || product.status === status.value
  return matchesSearch && matchesCategory && matchesStatus
}))
const publishedCount = computed(() => products.items.filter((product) => product.status === 'active').length)
const storefrontUrl = computed(() => {
  const url = new URL(import.meta.env.VITE_CUSTOMER_SITE_URL || 'http://127.0.0.1:5174/', window.location.origin)
  url.searchParams.set('tenant', auth.user?.tenantSlug || 'legacy-workspace')
  return url.toString()
})

onMounted(async () => {
  pageError.value = ''
  const requests = [products.loadProducts()]
  if (!settings.initialized) requests.push(settings.load())
  const results = await Promise.allSettled(requests)
  const failedRequest = results.find((result) => result.status === 'rejected')
  if (failedRequest) pageError.value = failedRequest.reason?.message || 'Could not load customer website data.'
})

async function saveWebsiteSettings() {
  pageError.value = ''
  savedMessage.value = ''
  try {
    await settings.save()
    savedMessage.value = 'Website settings saved.'
  } catch (error) {
    pageError.value = error.message || 'Could not save website settings.'
  }
}

async function deleteProduct() {
  pageError.value = ''
  try {
    await products.deleteProduct(productToDelete.value.id)
    productToDelete.value = null
  } catch (error) {
    pageError.value = error.message || 'Could not delete this product.'
  }
}
</script>

<template>
  <section class="min-h-screen bg-background px-5 py-7 sm:px-8 lg:px-10">
    <div class="mx-auto max-w-7xl">
      <header class="flex flex-col justify-between gap-5 border-b border-border pb-6 sm:flex-row sm:items-end">
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Workspace storefront</p>
          <h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Customer website</h1>
          <p class="mt-2 text-sm text-muted">Manage the menu and ordering availability for {{ auth.user?.tenantName || 'your workspace' }}.</p>
        </div>
        <a :href="storefrontUrl" target="_blank" rel="noreferrer" class="inline-flex min-h-10 items-center justify-center gap-2 border border-border bg-surface px-4 text-sm font-semibold text-ink hover:border-brand hover:text-brand">
          <ExternalLink :size="16" /> Preview storefront
        </a>
      </header>

      <p v-if="pageError" role="alert" class="mt-5 border-l-2 border-danger bg-surface px-4 py-3 text-sm text-danger">{{ pageError }}</p>

      <form v-if="settings.initialized" class="mt-6 border-b border-border pb-6" @submit.prevent="saveWebsiteSettings">
        <div class="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
          <div>
            <h2 class="text-lg font-bold text-ink">Storefront availability</h2>
            <p class="mt-1 text-sm text-muted">These controls affect only this workspace’s customer website.</p>
          </div>
          <button type="submit" :disabled="settings.saving" class="inline-flex min-h-10 items-center justify-center gap-2 self-start bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50">
            {{ settings.saving ? 'Saving...' : 'Save availability' }}
          </button>
        </div>
        <div class="mt-5 grid gap-3 md:grid-cols-2">
          <label class="flex items-start gap-3 border border-border bg-surface p-4 text-sm text-ink">
            <input v-model="settings.websiteEnabled" type="checkbox" class="mt-0.5 size-4 accent-brand" />
            <span><strong class="block">Publish customer website</strong><span class="mt-1 block text-xs text-muted">Allow customers to browse this workspace’s storefront.</span></span>
          </label>
          <label class="flex items-start gap-3 border border-border bg-surface p-4 text-sm text-ink">
            <input v-model="settings.orderingOpen" type="checkbox" class="mt-0.5 size-4 accent-brand" />
            <span><strong class="block">Accept online orders</strong><span class="mt-1 block text-xs text-muted">Pause checkout without changing the POS order flow.</span></span>
          </label>
        </div>
        <p v-if="savedMessage" role="status" class="mt-3 text-sm font-semibold text-success">{{ savedMessage }}</p>
      </form>

      <section class="mt-7" aria-labelledby="website-menu-heading">
        <header class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p class="text-xs font-bold uppercase tracking-[0.12em] text-brand">Published menu</p>
            <h2 id="website-menu-heading" class="mt-1 text-xl font-bold text-ink">Products shown on the website</h2>
            <p class="mt-1 text-sm text-muted">Active products appear on the storefront. Inactive products stay in POS but are hidden from customers.</p>
          </div>
          <button type="button" class="inline-flex min-h-10 items-center justify-center gap-2 bg-ink px-4 text-sm font-semibold text-white hover:bg-brand" @click="router.push('/menu/products/create')">
            <Plus :size="16" /> Add product
          </button>
        </header>

        <div class="mt-5 flex flex-col gap-3 border-y border-border py-4 lg:flex-row lg:items-center lg:justify-between">
          <ProductSearch v-model="search" />
          <ProductFilter v-model:category="category" v-model:status="status" :categories="products.categories" />
          <div class="flex shrink-0 gap-5 text-sm text-muted">
            <span><strong class="text-ink">{{ publishedCount }}</strong> published</span>
            <span><strong class="text-ink">{{ products.items.length }}</strong> total</span>
          </div>
        </div>

        <p v-if="products.loading" role="status" class="py-10 text-center text-sm text-muted">Loading products...</p>
        <div v-else class="mt-4">
          <ProductTable
            :products="visibleProducts"
            @view="(product) => router.push(`/menu/products/${product.id}`)"
            @edit="(product) => router.push(`/menu/products/${product.id}/edit`)"
            @delete="productToDelete = $event"
          />
        </div>
        <button type="button" class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand hover:underline" :disabled="products.loading" @click="products.loadProducts().catch((error) => { pageError = error.message })">
          <RefreshCw :size="15" /> Refresh products
        </button>
      </section>
    </div>

    <DeleteProductModal :open="Boolean(productToDelete)" :product="productToDelete" @cancel="productToDelete = null" @confirm="deleteProduct" />
  </section>
</template>
