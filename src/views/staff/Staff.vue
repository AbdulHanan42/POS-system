<script setup>
import { computed, onMounted, ref } from 'vue'
import { Pencil, Plus, Search, Trash2, UserRound, Users, X } from 'lucide-vue-next'
import BaseModal from '../../components/common/BaseModal.vue'
import { useStaffStore } from '../../stores/staff.js'

const staffStore = useStaffStore()
const search = ref('')
const selectedRole = ref('all')
const selectedStatus = ref('all')
const showForm = ref(false)
const editingMember = ref(null)
const deletingMember = ref(null)
const saving = ref(false)
const savingStatusId = ref(null)
const actionError = ref('')
const form = ref(emptyForm())

const roles = ['Administrator', 'Manager', 'Cashier', 'Chef', 'Waiter']
const statuses = [
	{ value: 'all', label: 'All staff' },
	{ value: 'active', label: 'Active' },
	{ value: 'inactive', label: 'Inactive' },
]
const roleCounts = computed(() => Object.fromEntries(
	roles.map((role) => [role, staffStore.items.filter((member) => member.role === role && member.status === 'active').length]),
))
const visibleStaff = computed(() => {
	const query = search.value.trim().toLowerCase()
	return staffStore.items.filter((member) => {
		const matchesSearch = !query || `${member.name} ${member.email} ${member.phone}`.toLowerCase().includes(query)
		const matchesRole = selectedRole.value === 'all' || member.role === selectedRole.value
		const matchesStatus = selectedStatus.value === 'all' || member.status === selectedStatus.value
		return matchesSearch && matchesRole && matchesStatus
	})
})

function emptyForm() {
	return { name: '', email: '', phone: '', role: 'Waiter', status: 'active' }
}

onMounted(() => staffStore.load().catch(() => undefined))

function startCreate() {
	editingMember.value = null
	form.value = emptyForm()
	actionError.value = ''
	showForm.value = true
}

function startEdit(member) {
	editingMember.value = member
	form.value = { name: member.name, email: member.email, phone: member.phone, role: member.role, status: member.status }
	actionError.value = ''
	showForm.value = true
}

async function saveMember() {
	saving.value = true
	actionError.value = ''
	const payload = {
		...form.value,
		name: form.value.name.trim(),
		email: form.value.email.trim().toLowerCase(),
		phone: form.value.phone.trim(),
	}
	try {
		if (editingMember.value) await staffStore.update({ ...payload, id: editingMember.value.id })
		else await staffStore.add(payload)
		showForm.value = false
	} catch (error) {
		actionError.value = error.message
	} finally {
		saving.value = false
	}
}

async function changeStatus(member, status) {
	savingStatusId.value = member.id
	actionError.value = ''
	try {
		await staffStore.update({ ...member, status })
	} catch (error) {
		actionError.value = error.message
	} finally {
		savingStatusId.value = null
	}
}

async function confirmDelete() {
	actionError.value = ''
	try {
		await staffStore.remove(deletingMember.value.id)
		deletingMember.value = null
	} catch (error) {
		actionError.value = error.message
	}
}

function retryLoad() {
	staffStore.load().catch(() => undefined)
}
</script>

<template>
	<section class="min-h-screen min-w-0 bg-background px-5 py-7 sm:px-8 lg:px-10">
		<div class="mx-auto max-w-7xl">
			<header class="flex flex-col justify-between gap-5 border-b border-border pb-6 sm:flex-row sm:items-end">
				<div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">People operations</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Staff</h1><p class="mt-2 text-sm text-muted">Manage staff profiles, roles, and active status.</p></div>
				<button type="button" class="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark" @click="startCreate"><Plus :size="17" aria-hidden="true" /> Add staff member</button>
			</header>

			<p v-if="actionError" role="alert" class="mt-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger">{{ actionError }}</p>
			<p v-if="staffStore.error && !staffStore.items.length" role="alert" class="mt-4 rounded-sm border border-red-200 bg-red-50 px-4 py-3 text-sm text-danger">Could not load staff: {{ staffStore.error }} <button type="button" class="ml-2 font-semibold underline" @click="retryLoad">Try again</button></p>

			<div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
				<article class="flex items-center justify-between rounded-md bg-ink px-4 py-3 text-white"><span class="text-sm font-medium text-white/75">Active staff</span><strong class="text-2xl">{{ staffStore.activeMembers.length }}</strong></article>
				<article v-for="role in roles" :key="role" class="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3 shadow-sm"><span class="text-xs font-semibold text-muted">{{ role }}</span><strong class="text-xl text-ink">{{ roleCounts[role] }}</strong></article>
			</div>

			<div class="mt-6 flex flex-col gap-3 border-b border-border pb-4 lg:flex-row lg:items-center lg:justify-between">
				<div class="flex gap-1 overflow-x-auto" aria-label="Filter staff by status"><button v-for="status in statuses" :key="status.value" type="button" class="shrink-0 rounded-sm px-3 py-2 text-sm font-semibold" :class="selectedStatus === status.value ? 'bg-ink text-white' : 'text-muted hover:bg-surface hover:text-ink'" :aria-pressed="selectedStatus === status.value" @click="selectedStatus = status.value">{{ status.label }}<span v-if="status.value === 'active'" class="ml-1">{{ staffStore.activeMembers.length }}</span></button></div>
				<div class="flex flex-col gap-2 sm:flex-row"><label class="relative block"><span class="sr-only">Search staff</span><Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" aria-hidden="true" /><input v-model="search" type="search" placeholder="Search name, email, phone" class="h-10 w-full rounded-sm border border-border bg-surface pl-9 pr-3 text-sm text-ink outline-none focus:border-brand sm:w-60" /></label><label><span class="sr-only">Filter by role</span><select v-model="selectedRole" class="h-10 w-full rounded-sm border border-border bg-surface px-3 text-sm text-ink outline-none focus:border-brand sm:w-44"><option value="all">All roles</option><option v-for="role in roles" :key="role" :value="role">{{ role }}</option></select></label></div>
			</div>

			<div v-if="staffStore.loading" role="status" class="py-16 text-center text-sm text-muted">Loading staff...</div>
			<div v-else-if="visibleStaff.length" class="overflow-x-auto">
				<table class="w-full min-w-[850px] border-collapse text-left"><thead><tr class="border-b border-border text-xs font-bold uppercase tracking-wide text-muted"><th class="py-3 pr-4">Staff member</th><th class="px-3 py-3">Role</th><th class="px-3 py-3">Phone</th><th class="px-3 py-3">Joined</th><th class="px-3 py-3">Status</th><th class="py-3 pl-3 text-right">Actions</th></tr></thead>
					<tbody><tr v-for="member in visibleStaff" :key="member.id" class="border-b border-border bg-surface/50 hover:bg-surface"><td class="py-4 pr-4"><div class="flex items-center gap-3"><span class="grid size-10 shrink-0 place-items-center rounded-sm bg-background text-sm font-bold text-brand">{{ member.name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase() }}</span><span class="min-w-0"><strong class="block truncate text-sm text-ink">{{ member.name }}</strong><small class="mt-1 block truncate text-xs text-muted">{{ member.email }}</small></span></div></td><td class="px-3 py-4 text-sm font-medium text-ink">{{ member.role }}</td><td class="px-3 py-4 text-sm text-muted">{{ member.phone || '—' }}</td><td class="px-3 py-4 text-sm text-muted">{{ new Date(member.createdAt).toLocaleDateString(undefined, { dateStyle: 'medium' }) }}</td><td class="px-3 py-4"><label class="sr-only" :for="`staff-status-${member.id}`">Status for {{ member.name }}</label><select :id="`staff-status-${member.id}`" :value="member.status" class="h-9 rounded-sm border border-border bg-surface px-2 text-xs font-semibold capitalize text-ink outline-none focus:border-brand disabled:opacity-50" :disabled="savingStatusId === member.id" @change="changeStatus(member, $event.target.value)"><option value="active">Active</option><option value="inactive">Inactive</option></select></td><td class="py-4 pl-3"><div class="flex justify-end gap-1"><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-background hover:text-ink" :aria-label="`Edit ${member.name}`" @click="startEdit(member)"><Pencil :size="16" aria-hidden="true" /></button><button type="button" class="grid size-9 place-items-center rounded-sm text-muted hover:bg-red-50 hover:text-danger" :aria-label="`Delete ${member.name}`" @click="deletingMember = member; actionError = ''"><Trash2 :size="16" aria-hidden="true" /></button></div></td></tr></tbody>
				</table>
			</div>
			<div v-else-if="!staffStore.loading" class="py-16 text-center"><Users :size="26" class="mx-auto text-muted" aria-hidden="true" /><p class="mt-3 font-semibold text-ink">{{ staffStore.items.length ? 'No matching staff' : 'No staff members yet' }}</p><p class="mt-1 text-sm text-muted">{{ staffStore.items.length ? 'Change the search or filters.' : 'Add your first staff profile to start managing the team.' }}</p><button v-if="!staffStore.items.length" type="button" class="mt-4 inline-flex min-h-10 items-center gap-2 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark" @click="startCreate"><Plus :size="16" aria-hidden="true" /> Add staff member</button></div>
		</div>

		<BaseModal :open="showForm">
			<form class="w-full max-w-lg rounded-md bg-surface p-6 shadow-xl" @submit.prevent="saveMember">
				<div class="flex items-start justify-between"><div><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Team profile</p><h2 class="mt-1 text-xl font-bold text-ink">{{ editingMember ? 'Edit staff member' : 'Add staff member' }}</h2></div><button type="button" class="grid size-8 place-items-center rounded-sm text-muted hover:bg-background" aria-label="Close staff form" @click="showForm = false"><X :size="18" aria-hidden="true" /></button></div>
				<label class="mt-5 grid gap-2 text-sm font-semibold text-ink">Full name<input v-model.trim="form.name" required maxlength="120" autocomplete="name" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="e.g. Alex Morgan" /></label>
				<label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Email<input v-model.trim="form.email" required type="email" maxlength="254" autocomplete="email" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="name@example.com" /></label>
				<label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Phone <span class="font-normal text-muted">Optional</span><input v-model.trim="form.phone" type="tel" maxlength="30" autocomplete="tel" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="+1 555 0100" /></label>
				<div class="mt-4 grid gap-4 sm:grid-cols-2"><label class="grid gap-2 text-sm font-semibold text-ink">Role<select v-model="form.role" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand"><option v-for="role in roles" :key="role" :value="role">{{ role }}</option></select></label><label class="grid gap-2 text-sm font-semibold text-ink">Status<select v-model="form.status" class="h-10 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand"><option value="active">Active</option><option value="inactive">Inactive</option></select></label></div>
				<p v-if="actionError" role="alert" class="mt-4 text-sm text-danger">{{ actionError }}</p><div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" :disabled="saving" @click="showForm = false">Cancel</button><button type="submit" class="min-h-10 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="saving">{{ saving ? 'Saving...' : editingMember ? 'Save changes' : 'Add staff member' }}</button></div>
			</form>
		</BaseModal>

		<BaseModal :open="Boolean(deletingMember)"><div class="w-full max-w-md rounded-md bg-surface p-6 shadow-xl"><h2 class="text-lg font-bold text-ink">Delete staff profile?</h2><p class="mt-2 text-sm leading-6 text-muted">Remove <strong class="text-ink">{{ deletingMember?.name }}</strong> from the staff directory?</p><p v-if="actionError" role="alert" class="mt-3 text-sm text-danger">{{ actionError }}</p><div class="mt-6 flex justify-end gap-2"><button type="button" class="min-h-10 rounded-sm px-4 text-sm font-semibold text-muted hover:bg-background" @click="deletingMember = null">Cancel</button><button type="button" class="min-h-10 rounded-sm bg-danger px-4 text-sm font-semibold text-white hover:bg-red-800" @click="confirmDelete">Delete profile</button></div></div></BaseModal>
	</section>
</template>
