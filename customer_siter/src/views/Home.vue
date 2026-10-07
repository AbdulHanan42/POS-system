<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, Check, Clock3, MapPin, Minus, Plus, Search, ShoppingBag, X } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { publicApi, tenantSlug } from '../services/publicApi'
import { useCartStore } from '../stores/cart'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const site = ref({ restaurantName: 'Restaurant', phone: '', address: '', publicDescription: '', logoUrl: '', heroImageUrl: '', openingHours: '', websiteEnabled: true, orderingOpen: true, taxRate: 0.1 })
const menu = ref([])
const zones = ref([])
const activeCategory = ref('All')
const search = ref('')
const selectedSizes = ref({})
const cartOpen = ref(false)
const checkoutOpen = ref(false)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const customer = ref({ name: '', phone: '', address: '', zone: '', notes: '' })

const categories = computed(() => ['All', ...new Set(menu.value.map((item) => item.category))])
const visibleMenu = computed(() => menu.value.filter((item) => {
	const inCategory = activeCategory.value === 'All' || item.category === activeCategory.value
	const query = search.value.trim().toLowerCase()
	const matchesSearch = !query || `${item.name} ${item.category} ${item.description || ''}`.toLowerCase().includes(query)
	return inCategory && matchesSearch
}))
const selectedZone = computed(() => zones.value.find((zone) => zone.name === customer.value.zone))
const deliveryFee = computed(() => Number(selectedZone.value?.fee || 0))
const tax = computed(() => cart.subtotal * Number(site.value.taxRate || 0))
const total = computed(() => cart.subtotal + deliveryFee.value + tax.value)
const orderingAvailable = computed(() => site.value.websiteEnabled && site.value.orderingOpen)
const money = (amount) => `Rs ${Number(amount || 0).toLocaleString('en-PK', { maximumFractionDigits: 0 })}`

function sizeFor(product) {
	const choices = Object.keys(product.prices || {})
	return selectedSizes.value[product.id] || (choices.includes('medium') ? 'medium' : choices[0] || '')
}

function priceFor(product) {
	return Number(product.prices?.[sizeFor(product)] ?? product.price)
}

async function loadStorefront() {
	loading.value = true
	error.value = ''
	cart.initialize(tenantSlug())
	try {
		const [siteData, menuData, zoneData] = await Promise.all([
			publicApi.getSite(),
			publicApi.getMenu(),
			publicApi.getDeliveryZones(),
		])
		site.value = siteData
		menu.value = menuData
		zones.value = zoneData
		customer.value.zone = zones.value[0]?.name || ''
	} catch (cause) {
		error.value = cause.message
	} finally {
		loading.value = false
	}
}

function addToCart(product) {
	if (!orderingAvailable.value) return
	cart.add(product, sizeFor(product), priceFor(product))
	cartOpen.value = true
}

async function placeOrder() {
	error.value = ''
	if (!customer.value.name.trim() || !customer.value.phone.trim() || !customer.value.address.trim() || !customer.value.zone) {
		error.value = 'Complete your name, phone, delivery address, and area.'
		return
	}
	if (!cart.items.length) {
		error.value = 'Add at least one item to your order.'
		return
	}
	if (selectedZone.value && cart.subtotal < Number(selectedZone.value.minOrderAmount)) {
		error.value = `The minimum order for ${selectedZone.value.name} is ${money(selectedZone.value.minOrderAmount)}.`
		return
	}

	submitting.value = true
	try {
		const confirmation = await publicApi.createOrder({
			customer: customer.value.name,
			phone: customer.value.phone,
			deliveryAddress: customer.value.address,
			deliveryZone: customer.value.zone,
			deliveryNotes: customer.value.notes || null,
			items: cart.items.map((item) => ({
				productId: item.productId,
				name: item.name,
				quantity: item.quantity,
				price: item.price,
				selectedSize: item.size || null,
			})),
		})
		cart.clear()
		router.push({ name: 'track-order', params: { orderId: confirmation.id }, query: { tenant: tenantSlug() }, hash: `#${confirmation.trackingToken}` })
	} catch (cause) {
		error.value = cause.message
	} finally {
		submitting.value = false
	}
}

onMounted(loadStorefront)
</script>

<template>
	<main class="min-h-screen bg-[var(--paper)] text-[var(--ink)]">
		<header class="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 md:px-8">
			<a href="#top" class="flex min-w-0 items-center gap-3">
				<img v-if="site.logoUrl" class="size-11 shrink-0 rounded-full bg-white object-contain" :src="site.logoUrl" :alt="`${site.restaurantName} logo`" />
				<span v-else class="grid size-11 shrink-0 place-items-center rounded-full bg-[var(--forest)] text-xl font-bold text-white">{{ site.restaurantName.charAt(0) }}</span>
				<span class="min-w-0"><strong class="block truncate font-serif text-lg">{{ site.restaurantName }}</strong><small class="text-[10px] uppercase tracking-[.18em] text-[var(--muted)]">Kitchen · delivery</small></span>
			</a>
			<nav class="hidden items-center gap-8 text-sm text-stone-600 md:flex"><a href="#menu">Menu</a><a href="#story">Our kitchen</a><a href="#visit">Visit us</a></nav>
			<button class="inline-flex items-center gap-2 rounded-full border border-stone-300 px-4 py-2 text-sm font-semibold hover:border-[var(--forest)]" type="button" @click="cartOpen = true"><ShoppingBag :size="17" /> Your order <span class="grid size-6 place-items-center rounded-full bg-[var(--forest)] text-xs text-white">{{ cart.count }}</span></button>
		</header>

		<p v-if="!orderingAvailable" class="mx-auto max-w-7xl px-5 pb-3 text-sm font-semibold text-red-800 md:px-8" role="status">{{ site.websiteEnabled ? 'Online ordering is paused right now. You can still browse the menu.' : 'This restaurant is not accepting online orders right now.' }}</p>

		<section id="top" class="mx-auto grid max-w-7xl items-center gap-10 px-5 pb-14 pt-3 md:grid-cols-[.9fr_1.1fr] md:px-8 md:pb-20">
			<div class="order-2 md:order-1">
				<p class="mb-5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-[var(--clay)]"><span class="h-px w-7 bg-current"></span> Fresh from our kitchen</p>
				<h1 class="max-w-xl font-serif text-5xl leading-[1.04] text-[var(--forest)] sm:text-6xl">Good food,<br><em class="font-normal text-[var(--clay)]">good to go.</em></h1>
				<p class="mt-5 max-w-md text-sm leading-7 text-[var(--muted)]">{{ site.publicDescription || 'Order your favourites, made fresh and delivered with care.' }}</p>
				<a href="#menu" class="mt-7 inline-flex min-h-12 items-center gap-3 rounded-sm bg-[var(--forest)] px-5 text-sm font-semibold text-white transition hover:bg-[#1f3b30]">Browse the menu <ArrowRight :size="17" /></a>
				<div class="mt-9 flex flex-wrap gap-x-6 gap-y-3 text-xs text-[var(--muted)]"><span class="inline-flex items-center gap-2"><Clock3 :size="15" class="text-[var(--clay)]" /> Delivery from our kitchen</span><span class="inline-flex items-center gap-2"><MapPin :size="15" class="text-[var(--clay)]" /> {{ site.address || 'Made fresh to order' }}</span></div>
			</div>
			<div class="relative order-1 h-[300px] overflow-hidden rounded-sm bg-[#ddd9cc] md:order-2 md:h-[470px]">
				<img class="h-full w-full object-cover" :src="site.heroImageUrl || 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1500&q=85'" :alt="`${site.restaurantName} freshly prepared food`" />
				<div class="absolute bottom-5 left-5 bg-white/95 px-5 py-4 shadow-sm"><strong class="block font-serif text-lg text-[var(--forest)]">Made fresh, every day.</strong><small class="mt-1 block text-xs text-[var(--muted)]">A little care in every order.</small></div>
			</div>
		</section>

		<section id="menu" class="bg-[#eeede6]">
			<div class="mx-auto max-w-7xl px-5 py-14 md:px-8 md:py-20">
				<div class="flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p class="text-[10px] font-bold uppercase tracking-[.18em] text-[var(--clay)]">The menu</p><h2 class="mt-3 font-serif text-4xl text-[var(--forest)]">Something delicious.</h2></div><label class="flex h-11 w-full items-center gap-3 border-b border-stone-400 px-1 text-stone-500 sm:max-w-xs"><Search :size="17" /><span class="sr-only">Search menu</span><input v-model.trim="search" class="w-full bg-transparent text-sm text-[var(--ink)] outline-none" placeholder="Search dishes" type="search" /></label></div>
				<div class="mt-7 flex gap-2 overflow-x-auto pb-2" aria-label="Filter menu by category"><button v-for="category in categories" :key="category" type="button" class="shrink-0 rounded-full border px-4 py-2 text-xs font-semibold transition" :class="activeCategory === category ? 'border-[var(--forest)] bg-[var(--forest)] text-white' : 'border-stone-300 text-stone-600 hover:border-[var(--forest)]'" @click="activeCategory = category">{{ category }}</button></div>
				<p v-if="loading" class="py-16 text-center text-sm text-[var(--muted)]" role="status">Loading the menu…</p>
				<div v-else-if="error && !menu.length" class="py-16 text-center text-sm text-red-800" role="alert">{{ error }} <button class="ml-2 underline" type="button" @click="loadStorefront">Try again</button></div>
				<p v-else-if="!visibleMenu.length" class="py-16 text-center text-sm text-[var(--muted)]">No dishes match that search.</p>
				<div v-else class="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
					<article v-for="product in visibleMenu" :key="product.id" class="overflow-hidden bg-[#faf9f5]">
						<div class="relative h-52 bg-stone-200"><img class="h-full w-full object-cover" :src="product.image || 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80'" :alt="product.name" loading="lazy" /><button class="absolute bottom-3 right-3 grid size-10 place-items-center rounded-full bg-white text-[var(--forest)] shadow disabled:cursor-not-allowed" type="button" :disabled="!orderingAvailable" :aria-label="`Add ${product.name} to order`" @click="addToCart(product)"><Plus :size="20" /></button></div>
						<div class="p-4"><div class="flex items-start justify-between gap-3"><h3 class="font-serif text-lg">{{ product.name }}</h3><strong class="whitespace-nowrap text-sm text-[var(--forest)]">{{ money(priceFor(product)) }}</strong></div><label v-if="product.prices" class="mt-3 flex items-center justify-between gap-3 text-xs text-[var(--muted)]">Choose size<select v-model="selectedSizes[product.id]" class="max-w-36 border border-stone-300 bg-transparent px-2 py-1 text-xs capitalize text-[var(--ink)]"><option v-for="(price, size) in product.prices" :key="size" :value="size">{{ size }} · {{ money(price) }}</option></select></label><p class="mt-2 text-xs leading-5 text-[var(--muted)]">{{ product.description || 'Prepared fresh for your order.' }}</p></div>
					</article>
				</div>
			</div>
		</section>

		<section id="story" class="mx-auto grid max-w-7xl gap-8 px-5 py-16 md:grid-cols-2 md:items-center md:px-8 md:py-24"><div class="h-64 overflow-hidden md:h-80"><img class="h-full w-full object-cover" src="https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=1100&q=85" alt="Restaurant kitchen preparing fresh meals" loading="lazy" /></div><div class="max-w-lg"><p class="text-[10px] font-bold uppercase tracking-[.18em] text-[var(--clay)]">From our kitchen</p><h2 class="mt-3 font-serif text-4xl leading-tight text-[var(--forest)]">A good meal makes the day.</h2><p class="mt-4 text-sm leading-7 text-[var(--muted)]">Thoughtful ingredients, familiar favourites, and a kitchen that cares about what reaches your table.</p></div></section>

		<footer id="visit" class="bg-[#263c32] text-white"><div class="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 text-xs text-white/75 sm:flex-row sm:items-center sm:justify-between md:px-8"><strong class="font-serif text-lg text-white">{{ site.restaurantName }}</strong><span>{{ site.address || 'Fresh food, good company.' }}</span><span v-if="site.openingHours">{{ site.openingHours }}</span><a v-if="site.phone" :href="`tel:${site.phone}`">{{ site.phone }}</a><span>Order online · Pay cash on delivery</span></div></footer>

		<Transition name="veil"><div v-if="cartOpen || checkoutOpen" class="fixed inset-0 z-40 flex justify-end bg-black/45" @click.self="cartOpen = false; checkoutOpen = false"><aside class="relative h-full w-full max-w-md overflow-y-auto bg-[var(--paper)] p-6 shadow-xl sm:p-9" role="dialog" aria-modal="true" :aria-label="checkoutOpen ? 'Delivery checkout' : 'Your order'"><button class="absolute right-5 top-5 grid size-9 place-items-center rounded-full border border-stone-300" type="button" aria-label="Close order panel" @click="cartOpen = false; checkoutOpen = false"><X :size="18" /></button>
			<template v-if="checkoutOpen"><p class="mt-8 text-[10px] font-bold uppercase tracking-[.18em] text-[var(--clay)]">Almost there</p><h2 class="mt-2 font-serif text-3xl text-[var(--forest)]">Delivery details</h2><p class="mt-2 text-sm leading-6 text-[var(--muted)]">Pay cash when your order arrives.</p><form class="mt-6 grid gap-4" @submit.prevent="placeOrder"><label class="grid gap-1.5 text-xs font-semibold">Full name<input v-model.trim="customer.name" required autocomplete="name" class="h-11 border border-stone-300 bg-white px-3 text-sm font-normal" /></label><label class="grid gap-1.5 text-xs font-semibold">Phone number<input v-model.trim="customer.phone" required type="tel" autocomplete="tel" class="h-11 border border-stone-300 bg-white px-3 text-sm font-normal" /></label><label class="grid gap-1.5 text-xs font-semibold">Delivery area<select v-model="customer.zone" required class="h-11 border border-stone-300 bg-white px-3 text-sm font-normal"><option disabled value="">Choose your area</option><option v-for="zone in zones" :key="zone.id" :value="zone.name">{{ zone.name }} · {{ money(zone.fee) }}</option></select></label><label class="grid gap-1.5 text-xs font-semibold">Delivery address<textarea v-model.trim="customer.address" required minlength="8" autocomplete="street-address" rows="2" class="resize-y border border-stone-300 bg-white px-3 py-2 text-sm font-normal" /></label><label class="grid gap-1.5 text-xs font-semibold">Delivery instructions <span class="font-normal text-[var(--muted)]">Optional</span><textarea v-model.trim="customer.notes" rows="2" class="resize-y border border-stone-300 bg-white px-3 py-2 text-sm font-normal" /></label><p v-if="error" class="text-sm text-red-800" role="alert">{{ error }}</p><div class="mt-1 grid gap-2 border-t border-stone-300 pt-4 text-sm"><div class="flex justify-between"><span>Subtotal</span><strong>{{ money(cart.subtotal) }}</strong></div><div class="flex justify-between"><span>Delivery</span><strong>{{ money(deliveryFee) }}</strong></div><div class="flex justify-between"><span>Tax</span><strong>{{ money(tax) }}</strong></div><div class="mt-1 flex justify-between border-t border-stone-300 pt-3 text-base"><strong>Total</strong><strong>{{ money(total) }}</strong></div></div><button class="mt-3 inline-flex min-h-12 items-center justify-center gap-2 bg-[var(--forest)] px-4 text-sm font-semibold text-white disabled:opacity-50" type="submit" :disabled="submitting || !zones.length || !orderingAvailable">{{ submitting ? 'Sending order…' : 'Place delivery order' }} <ArrowRight :size="17" /></button><small class="text-center text-xs text-[var(--muted)]">Cash on delivery</small></form></template>
			<template v-else><p class="mt-8 text-[10px] font-bold uppercase tracking-[.18em] text-[var(--clay)]">Your order</p><h2 class="mt-2 font-serif text-3xl text-[var(--forest)]">Good choices.</h2><p v-if="!cart.items.length" class="mt-5 text-sm text-[var(--muted)]">Your basket is waiting for something delicious.</p><div v-else class="mt-5 grid gap-4"><article v-for="item in cart.items" :key="`${item.productId}-${item.size}`" class="flex gap-3 border-b border-stone-200 pb-4"><img class="size-16 object-cover" :src="item.image || 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=200&q=75'" :alt="item.name" /><div class="min-w-0 flex-1"><strong class="block truncate font-serif">{{ item.name }}</strong><small v-if="item.size" class="text-xs capitalize text-[var(--muted)]">{{ item.size }}</small><div class="mt-2 flex items-center justify-between"><div class="flex items-center gap-3"><button type="button" :aria-label="`Remove one ${item.name}`" @click="cart.setQuantity(item, item.quantity - 1)"><Minus :size="14" /></button><b class="text-xs">{{ item.quantity }}</b><button type="button" :aria-label="`Add one ${item.name}`" @click="cart.setQuantity(item, item.quantity + 1)"><Plus :size="14" /></button></div><strong class="text-sm">{{ money(item.price * item.quantity) }}</strong></div></div></article><div class="flex justify-between border-t border-stone-300 pt-4 text-sm"><span>Subtotal</span><strong>{{ money(cart.subtotal) }}</strong></div><button class="inline-flex min-h-12 items-center justify-center gap-2 bg-[var(--forest)] px-4 text-sm font-semibold text-white" type="button" :disabled="!zones.length" @click="checkoutOpen = true; cartOpen = false">Continue to delivery <ArrowRight :size="17" /></button></div></template>
			</aside></div></Transition>
	</main>
</template>

<style scoped>
.veil-enter-active,.veil-leave-active { transition: opacity .18s ease; }
.veil-enter-from,.veil-leave-to { opacity: 0; }
</style>