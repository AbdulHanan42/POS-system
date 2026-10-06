<script setup>
import { computed, onMounted, ref } from 'vue'
import { useSettingsStore } from '../../stores/settings.js'

const settings = useSettingsStore()
const activeTab = ref('restaurant')
const savedMessage = ref('')
const taxPercent = computed({
	get: () => Number(settings.taxRate) * 100,
	set: (value) => { settings.taxRate = Number(value) / 100 },
})

onMounted(() => settings.load().catch(() => undefined))

async function saveSettings() {
	savedMessage.value = ''
	try {
		await settings.save()
		savedMessage.value = 'Settings saved.'
		window.setTimeout(() => { savedMessage.value = '' }, 4000)
	} catch {
		savedMessage.value = ''
	}
}
</script>

<template>
	<section class="min-h-screen bg-background px-5 py-7 sm:px-8 lg:px-10">
		<div class="mx-auto max-w-4xl">
			<header class="border-b border-border pb-6"><p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Workspace</p><h1 class="mt-2 text-3xl font-bold tracking-tight text-ink">Settings</h1><p class="mt-2 text-sm text-muted">Restaurant details, tax, and receipt information.</p></header>

			<div class="mt-5 flex gap-1 border-b border-border" role="tablist" aria-label="Settings sections"><button type="button" role="tab" :aria-selected="activeTab === 'restaurant'" class="rounded-t-sm px-4 py-3 text-sm font-semibold" :class="activeTab === 'restaurant' ? 'border-b-2 border-brand text-ink' : 'text-muted hover:text-ink'" @click="activeTab = 'restaurant'">Restaurant details</button><button type="button" role="tab" :aria-selected="activeTab === 'tax'" class="rounded-t-sm px-4 py-3 text-sm font-semibold" :class="activeTab === 'tax' ? 'border-b-2 border-brand text-ink' : 'text-muted hover:text-ink'" @click="activeTab = 'tax'">Tax and receipt</button></div>

			<p v-if="settings.loading" role="status" class="py-12 text-center text-sm text-muted">Loading settings...</p>
			<div v-else-if="!settings.initialized" class="py-12 text-center"><p role="alert" class="text-sm text-danger">{{ settings.error || 'Settings have not loaded.' }}</p><button type="button" class="mt-3 text-sm font-semibold text-brand hover:underline" @click="settings.load().catch(() => undefined)">Try again</button></div>
			<form v-else class="mt-6" @submit.prevent="saveSettings">
				<div v-if="activeTab === 'restaurant'" class="max-w-2xl" role="tabpanel">
					<div class="border-b border-border pb-4"><h2 class="text-lg font-bold text-ink">Restaurant details</h2><p class="mt-1 text-sm text-muted">These details are used across the point of sale and receipts.</p></div>
					<label class="mt-5 grid gap-2 text-sm font-semibold text-ink">Restaurant name<input v-model.trim="settings.restaurantName" required maxlength="120" autocomplete="organization" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
					<div class="mt-4 grid gap-4 sm:grid-cols-2"><label class="grid gap-2 text-sm font-semibold text-ink">Email<input v-model.trim="settings.email" type="email" maxlength="254" autocomplete="email" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="hello@restaurant.com" /></label><label class="grid gap-2 text-sm font-semibold text-ink">Phone<input v-model.trim="settings.phone" type="tel" maxlength="30" autocomplete="tel" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="+1 555 0100" /></label></div>
					<label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Address<textarea v-model.trim="settings.address" maxlength="240" rows="3" autocomplete="street-address" class="resize-y rounded-sm border border-border bg-surface px-3 py-2 font-normal outline-none focus:border-brand" placeholder="Street, city, and postal code" /></label>
				</div>

				<div v-else class="max-w-2xl" role="tabpanel">
					<div class="border-b border-border pb-4"><h2 class="text-lg font-bold text-ink">Tax and receipt</h2><p class="mt-1 text-sm text-muted">The tax rate applies to new orders. Saved orders keep the rate used at checkout.</p></div>
					<label class="mt-5 grid max-w-xs gap-2 text-sm font-semibold text-ink">Sales tax rate (%)<input v-model.number="taxPercent" required type="number" min="0" max="100" step="0.01" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
					<label class="mt-4 grid gap-2 text-sm font-semibold text-ink">Receipt footer <span class="font-normal text-muted">Optional</span><textarea v-model.trim="settings.receiptFooter" maxlength="240" rows="3" class="resize-y rounded-sm border border-border bg-surface px-3 py-2 font-normal outline-none focus:border-brand" placeholder="Thank you for dining with us." /></label>
					<p class="mt-3 text-xs text-muted">Current tax rate: {{ taxPercent.toFixed(2).replace(/\.00$/, '') }}%</p>
				</div>

				<p v-if="settings.error" role="alert" class="mt-4 text-sm text-danger">{{ settings.error }}</p>
				<p v-if="savedMessage" role="status" class="mt-4 text-sm font-semibold text-success">{{ savedMessage }}</p>
				<footer class="mt-7 flex flex-col gap-3 border-t border-border pt-5 sm:flex-row sm:items-center sm:justify-between"><span v-if="settings.updatedAt" class="text-xs text-muted">Last saved {{ new Date(settings.updatedAt).toLocaleString() }}</span><button type="submit" class="min-h-10 rounded-sm bg-brand px-5 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50 sm:ml-auto" :disabled="settings.loading || settings.saving">{{ settings.saving ? 'Saving...' : 'Save settings' }}</button></footer>
			</form>
		</div>
	</section>
</template>
