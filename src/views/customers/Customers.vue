<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '../../components/common/BaseButton.vue'
import BaseModal from '../../components/common/BaseModal.vue'
import CustomerModal from '../../components/customers/CustomerModal.vue'
import CustomerSearch from '../../components/customers/CustomerSearch.vue'
import CustomerTable from '../../components/customers/CustomerTable.vue'
import { useCustomerStore } from '../../stores/customer.js'

const router = useRouter()
const customerStore = useCustomerStore()
const search = ref('')
const type = ref('All Customers')
const showModal = ref(false)
const editingCustomer = ref(null)
const deletingCustomer = ref(null)

const filteredCustomers = computed(() => customerStore.items.filter((customer) => {
	const query = search.value.toLowerCase().trim()
	const matchesSearch = !query || `${customer.name} ${customer.phone}`.toLowerCase().includes(query)
	const matchesType = type.value === 'All Customers' || customer.type === type.value
	return matchesSearch && matchesType
}))

function openCreate() { editingCustomer.value = null; showModal.value = true }
function openEdit(customer) { editingCustomer.value = customer; showModal.value = true }
function saveCustomer(customer) { editingCustomer.value ? customerStore.updateCustomer(customer) : customerStore.addCustomer(customer); showModal.value = false }
function deleteCustomer() { customerStore.deleteCustomer(deletingCustomer.value.id); deletingCustomer.value = null }
</script>

<template>
	<section class="min-h-screen bg-background px-6 py-8 lg:px-10"><div class="mx-auto max-w-7xl"><header class="flex flex-col justify-between gap-5 border-b border-border pb-6 sm:flex-row sm:items-end"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Customer management</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Customers</h1><p class="mt-2 text-sm text-muted">Keep customer contact details available for quick service.</p></div><BaseButton @click="openCreate">+ Add customer</BaseButton></header><div class="mt-6 rounded-lg border border-border bg-surface p-4 shadow-sm"><CustomerSearch v-model="search" v-model:type="type" /></div><div class="mt-6 flex items-center justify-between"><p class="text-sm text-muted"><strong class="text-ink">{{ filteredCustomers.length }}</strong> customers</p><span class="text-xs text-muted">Search by name or phone</span></div><div class="mt-3"><CustomerTable :customers="filteredCustomers" @view="router.push(`/customers/${$event.id}`)" @edit="openEdit" @delete="deletingCustomer = $event" /></div></div><CustomerModal :open="showModal" :customer="editingCustomer" @submit="saveCustomer" @close="showModal = false" /><BaseModal :open="Boolean(deletingCustomer)"><div class="w-full max-w-md rounded-lg bg-surface p-6 shadow-xl"><h2 class="text-lg font-bold text-ink">Delete customer?</h2><p class="mt-2 text-sm leading-6 text-muted">Remove <strong class="text-ink">{{ deletingCustomer?.name }}</strong> from your customer list?</p><div class="mt-6 flex justify-end gap-2"><BaseButton variant="secondary" @click="deletingCustomer = null">Cancel</BaseButton><BaseButton variant="danger" @click="deleteCustomer">Delete customer</BaseButton></div></div></BaseModal></section>
</template>
