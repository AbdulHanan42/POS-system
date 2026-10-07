<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, Check, ChevronDown, Clock3, MapPin, Minus, Plus, ShoppingBag, X } from 'lucide-vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()
const tenant = computed(() => String(route.query.tenant || 'legacy-workspace'))
const menu = ref([])
const zones = ref([])
const activeCategory = ref('All')
const sizeSelections = ref({})
const cart = ref([])
const cartOpen = ref(false)
const checkoutOpen = ref(false)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const confirmation = ref(null)
const customer = ref({ name: '', phone: '', address: '', zone: '', notes: '' })

const categories = computed(() => ['All', ...new Set(menu.value.map((product) => product.category))])
const visibleMenu = computed(() => activeCategory.value === 'All' ? menu.value : menu.value.filter((product) => product.category === activeCategory.value))
const cartCount = computed(() => cart.value.reduce((sum, item) => sum + item.quantity, 0))
const subtotal = computed(() => cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0))
const selectedZone = computed(() => zones.value.find((zone) => zone.name === customer.value.zone))
const fee = computed(() => Number(selectedZone.value?.fee || 0))
const total = computed(() => subtotal.value + fee.value + subtotal.value * 0.1)
const money = (amount) => `Rs ${Number(amount).toLocaleString('en-PK', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
const api = (path) => `/api/public/${path}?tenant=${encodeURIComponent(tenant.value)}`

async function loadMenu() {
  loading.value = true
  try {
    const [menuResponse, zoneResponse] = await Promise.all([fetch(api('menu')), fetch(api('delivery-zones'))])
    if (!menuResponse.ok) throw new Error('We could not load the menu. Please try again in a moment.')
    menu.value = await menuResponse.json()
    zones.value = zoneResponse.ok ? await zoneResponse.json() : []
    customer.value.zone = zones.value[0]?.name || ''
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
}

function sizeFor(product) {
  const availableSizes = Object.keys(product.prices || {})
  return sizeSelections.value[product.id] || (availableSizes.includes('medium') ? 'medium' : availableSizes[0] || '')
}

function priceFor(product, size = sizeFor(product)) {
  return Number(product.prices?.[size] ?? product.price)
}

function addToCart(product) {
  const selectedSize = sizeFor(product)
  const existing = cart.value.find((item) => item.productId === product.id && item.selectedSize === selectedSize)
  if (existing) existing.quantity += 1
  else cart.value.push({ productId: product.id, name: product.name, image: product.image, price: priceFor(product, selectedSize), selectedSize, quantity: 1 })
  error.value = ''
}

function changeQuantity(item, amount) {
  item.quantity += amount
  if (item.quantity <= 0) cart.value = cart.value.filter((line) => line !== item)
}

async function placeOrder() {
  error.value = ''
  if (!customer.value.name || !customer.value.phone || !customer.value.address || !customer.value.zone) {
    error.value = 'Please complete your contact and delivery details.'
    return
  }
  if (selectedZone.value && subtotal.value < Number(selectedZone.value.minOrderAmount)) {
    error.value = `The minimum order for this area is ${money(selectedZone.value.minOrderAmount)}.`
    return
  }
  submitting.value = true
  try {
    const response = await fetch(api('orders'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer: customer.value.name,
        phone: customer.value.phone,
        deliveryAddress: customer.value.address,
        deliveryZone: customer.value.zone,
        deliveryNotes: customer.value.notes || null,
        items: cart.value.map((item) => ({ productId: item.productId, name: item.name, quantity: item.quantity, price: item.price, selectedSize: item.selectedSize || null })),
      }),
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'Your order could not be placed. Please try again.')
    confirmation.value = data
    cart.value = []
    checkoutOpen.value = false
    cartOpen.value = false
  } catch (cause) {
    error.value = cause.message
  } finally {
    submitting.value = false
  }
}

onMounted(loadMenu)
</script>

<template>
  <main class="customer-site min-h-screen bg-[#faf8f4] text-[#272b25]">
    <header class="customer-nav mx-auto flex max-w-7xl items-center justify-between px-5 py-5 md:px-8">
      <a href="#top" class="flex items-center gap-3 no-underline text-inherit">
        <span class="brand-mark">f.</span>
        <span><strong class="block text-lg leading-tight">Fork & Flame</strong><small class="text-xs tracking-[.14em] text-stone-500">KITCHEN · EST. 2012</small></span>
      </a>
      <nav class="hidden items-center gap-8 text-sm font-medium text-stone-600 md:flex">
        <a href="#menu">Menu</a><a href="#story">Our kitchen</a><a href="#footer">Visit us</a>
      </nav>
      <button class="cart-trigger" type="button" @click="cartOpen = true"><ShoppingBag :size="17" /><span>Your order</span><b>{{ cartCount }}</b></button>
    </header>

    <section id="top" class="hero mx-auto grid max-w-7xl items-center gap-8 px-5 pb-12 pt-5 md:grid-cols-[.9fr_1.1fr] md:px-8 md:pb-20 md:pt-10">
      <div class="hero-copy order-2 md:order-1">
        <div class="eyebrow"><span></span> GOOD FOOD, RIGHT AT YOUR DOOR</div>
        <h1>Made with love.<br><em>Delivered</em> with care.</h1>
        <p>Big-hearted cooking, honest ingredients, and the kind of food that makes a good day even better.</p>
        <a class="primary-button inline-flex items-center gap-3" href="#menu">Explore the menu <ArrowRight :size="17" /></a>
        <div class="hero-meta"><span><Clock3 :size="16" /> 30–45 min delivery</span><span><MapPin :size="16" /> Made fresh to order</span></div>
      </div>
      <div class="hero-image order-1 md:order-2"><img src="https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1300&q=85" alt="Freshly prepared colorful meal" /><div class="image-note"><span>✳</span><div><strong>Fresh, always.</strong><small>From our kitchen to your table.</small></div></div></div>
    </section>

    <section id="menu" class="menu-section">
      <div class="mx-auto max-w-7xl px-5 py-14 md:px-8 md:py-20">
        <div class="section-heading"><div><div class="eyebrow"><span></span> THE GOOD STUFF</div><h2>Find your new <em>favorite.</em></h2></div><p>Every plate is made fresh, with ingredients we’re proud to serve.</p></div>
        <div class="category-tabs" role="tablist" aria-label="Menu categories">
          <button v-for="category in categories" :key="category" :class="{ selected: category === activeCategory }" type="button" @click="activeCategory = category">{{ category }}</button>
        </div>

        <div v-if="loading" class="menu-message">Getting the kitchen ready…</div>
        <div v-else-if="error && !menu.length" class="menu-message error-message">{{ error }} <button type="button" @click="loadMenu">Try again</button></div>
        <div v-else-if="!visibleMenu.length" class="menu-message">Our menu is being updated. Check back soon.</div>
        <div v-else class="menu-grid">
          <article v-for="(product, index) in visibleMenu" :key="product.id" class="dish-card">
            <div class="dish-image"><img :src="product.image || 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80'" :alt="product.name" loading="lazy" /><span v-if="index === 0" class="dish-tag">HOUSE FAVORITE</span><button class="add-button" type="button" :aria-label="`Add ${product.name} to order`" @click="addToCart(product)"><Plus :size="20" /></button></div>
            <div class="dish-info"><div><h3>{{ product.name }}</h3><b>{{ money(priceFor(product)) }}</b></div><label v-if="product.prices" class="size-picker">Choose a size<select v-model="sizeSelections[product.id]" :aria-label="`Choose a size for ${product.name}`"><option v-for="(price, size) in product.prices" :key="size" :value="size">{{ size }} · {{ money(price) }}</option></select></label><p>{{ product.description || 'Fresh from our kitchen, made just for you.' }}</p></div>
          </article>
        </div>
      </div>
    </section>

    <section id="story" class="promise mx-auto grid max-w-7xl items-center gap-10 px-5 py-16 md:grid-cols-2 md:px-8 md:py-24">
      <div class="promise-image"><img src="https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=1100&q=85" alt="Chef preparing food in the restaurant kitchen" loading="lazy" /></div>
      <div class="promise-copy"><div class="eyebrow"><span></span> A LITTLE ABOUT US</div><h2>A good meal can<br />change your <em>whole day.</em></h2><p>We believe the best food starts with good ingredients, a little patience, and a kitchen full of people who care. That’s what we bring to every order.</p><div class="signature">Cooked with care, every single time <span>✳</span></div></div>
    </section>

    <footer id="footer" class="site-footer"><div class="mx-auto flex max-w-7xl flex-col justify-between gap-5 px-5 py-8 md:flex-row md:items-center md:px-8"><a href="#top" class="flex items-center gap-3 text-white no-underline"><span class="brand-mark footer-mark">f.</span><strong>Fork & Flame</strong></a><span>Thoughtful food. Good company. Every day.</span><span>© 2026 Fork & Flame Kitchen</span></div></footer>

    <Transition name="fade"><div v-if="cartOpen || checkoutOpen || confirmation" class="overlay" @click.self="cartOpen = false; checkoutOpen = false"><section class="order-panel" role="dialog" aria-modal="true" :aria-label="confirmation ? 'Order confirmation' : checkoutOpen ? 'Checkout' : 'Your order'">
      <template v-if="confirmation"><button class="close-panel" type="button" aria-label="Close" @click="confirmation = null"><X /></button><div class="success-icon"><Check :size="28" /></div><div class="eyebrow"><span></span> ORDER RECEIVED</div><h2>We’re on it.</h2><p class="panel-copy">Thanks for ordering, {{ customer.name }}. The kitchen has your order and will start preparing it shortly.</p><div class="confirmation-card"><span>ORDER NUMBER</span><strong>#{{ confirmation.id }}</strong><span>ESTIMATED DELIVERY</span><strong>{{ confirmation.estimatedTime }} minutes</strong><span>TOTAL</span><strong>{{ money(confirmation.total) }}</strong></div><button class="primary-button full-button" type="button" @click="confirmation = null">Back to the menu <ArrowRight :size="17" /></button></template>
      <template v-else-if="checkoutOpen"><button class="close-panel" type="button" aria-label="Back to order" @click="checkoutOpen = false"><X /></button><div class="eyebrow"><span></span> ALMOST THERE</div><h2>Delivery details</h2><p class="panel-copy">We’ll bring your meal right to your door. Pay cash when it arrives.</p><form class="checkout-form" @submit.prevent="placeOrder"><label>Your name<input v-model.trim="customer.name" autocomplete="name" required placeholder="Name" /></label><label>Phone number<input v-model.trim="customer.phone" autocomplete="tel" required type="tel" placeholder="03xx xxxxxxx" /></label><label>Delivery area<span class="select-wrap"><select v-model="customer.zone" required><option disabled value="">Choose your area</option><option v-for="zone in zones" :key="zone.id" :value="zone.name">{{ zone.name }} · {{ money(zone.fee) }}</option></select><ChevronDown :size="16" /></span></label><label>Delivery address<textarea v-model.trim="customer.address" autocomplete="street-address" required rows="2" placeholder="House, street, and nearby landmark" /></label><label>Notes for the kitchen <span class="optional">OPTIONAL</span><textarea v-model.trim="customer.notes" rows="2" placeholder="Anything we should know?" /></label><p v-if="error" class="form-error">{{ error }}</p><div class="order-totals"><div><span>Subtotal</span><b>{{ money(subtotal) }}</b></div><div><span>Delivery</span><b>{{ money(fee) }}</b></div><div><span>Tax</span><b>{{ money(subtotal * .1) }}</b></div><div class="grand-total"><span>Total</span><b>{{ money(total) }}</b></div></div><button class="primary-button full-button" type="submit" :disabled="submitting || !zones.length">{{ submitting ? 'Sending your order…' : 'Place my order' }} <ArrowRight :size="17" /></button><small class="secure-note">No payment now · Pay cash on delivery</small></form></template>
      <template v-else><button class="close-panel" type="button" aria-label="Close" @click="cartOpen = false"><X /></button><div class="eyebrow"><span></span> YOUR ORDER</div><h2>Good choices.</h2><p class="panel-copy">{{ cartCount ? `${cartCount} delicious ${cartCount === 1 ? 'item' : 'items'} coming right up.` : 'Your basket is waiting for something delicious.' }}</p><div v-if="!cart.length" class="empty-cart"><ShoppingBag :size="30" /><a href="#menu" @click="cartOpen = false">Explore the menu <ArrowRight :size="15" /></a></div><div v-else class="cart-lines"><article v-for="item in cart" :key="`${item.productId}-${item.selectedSize}`" class="cart-line"><img :src="item.image || 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=200&q=75'" :alt="item.name" /><div class="line-detail"><strong>{{ item.name }}<small v-if="item.selectedSize">{{ item.selectedSize }}</small></strong><span>{{ money(item.price) }}</span><div class="quantity-control"><button type="button" :aria-label="`Remove one ${item.name}`" @click="changeQuantity(item, -1)"><Minus :size="13" /></button><b>{{ item.quantity }}</b><button type="button" :aria-label="`Add one ${item.name}`" @click="changeQuantity(item, 1)"><Plus :size="13" /></button></div></div></article><div class="cart-subtotal"><span>Subtotal</span><b>{{ money(subtotal) }}</b></div><button class="primary-button full-button" type="button" @click="checkoutOpen = true; cartOpen = false">Continue to delivery <ArrowRight :size="17" /></button></div></template>
    </section></div></Transition>
  </main>
</template>

<style scoped>
.customer-site { --olive: #39452f; --orange: #c1663f; --cream: #faf8f4; font-family: 'DM Sans', Inter, ui-sans-serif, system-ui, sans-serif; }
.customer-site a { color: inherit; text-decoration: none; }
.brand-mark { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 50%; background: var(--olive); color: white; font: italic 700 25px Georgia,serif; }
.cart-trigger { display:flex; align-items:center; gap:9px; border:1px solid #dedbd3; border-radius:999px; padding:9px 10px 9px 15px; background:transparent; font-size:13px; font-weight:600; cursor:pointer; }
.cart-trigger b { display:grid; width:24px; height:24px; place-items:center; border-radius:50%; background:var(--olive); color:#fff; font-size:11px; }
.hero-copy { padding: 18px 0 28px; }
.eyebrow { display:flex; align-items:center; gap:9px; color:#8e684f; font-size:10px; font-weight:700; letter-spacing:.17em; }
.eyebrow span { width:20px; height:1px; background:#c1663f; }
.hero h1,.section-heading h2,.promise h2,.order-panel h2 { margin:20px 0 14px; color:#31392d; font:500 clamp(42px,5vw,68px)/1.04 Georgia,'Times New Roman',serif; letter-spacing:-.045em; }
.hero h1 em,.section-heading h2 em,.promise h2 em { color:var(--orange); font-weight:500; }
.hero-copy>p,.section-heading>p,.promise-copy>p { max-width:440px; color:#77766e; font-size:15px; line-height:1.8; }
.primary-button { min-height:50px; border:0; border-radius:4px; padding:0 21px; background:var(--olive); color:#fff!important; font-size:13px; font-weight:600; cursor:pointer; transition:background .2s,transform .2s; }
.primary-button:hover { transform:translateY(-1px); background:#293322; }
.hero-copy>.primary-button { margin-top:15px; }
.hero-meta { display:flex; flex-wrap:wrap; gap:22px; margin-top:33px; color:#77766e; font-size:11px; }
.hero-meta span { display:flex; align-items:center; gap:7px; }.hero-meta svg { color:var(--orange); }
.hero-image { position:relative; height:clamp(310px,41vw,510px); overflow:visible; }
.hero-image>img,.promise-image img { width:100%; height:100%; border-radius:5px; object-fit:cover; }
.image-note { position:absolute; right:-9px; bottom:22px; display:flex; align-items:center; gap:12px; padding:15px 19px; background:#fffdf9; box-shadow:0 9px 30px #24221d19; }
.image-note>span { color:var(--orange); font-size:28px; }.image-note strong,.image-note small { display:block; }.image-note strong { font:600 15px Georgia,serif; }.image-note small { margin-top:4px; color:#88847b; font-size:10px; }
.menu-section { background:#f0eee8; }.section-heading { display:flex; align-items:end; justify-content:space-between; gap:25px; }.section-heading h2,.promise h2 { margin-top:14px; font-size:clamp(36px,4vw,52px); }.section-heading>p { max-width:280px; margin-bottom:17px; font-size:13px; }
.category-tabs { display:flex; gap:8px; overflow-x:auto; padding:22px 0 25px; }.category-tabs button { flex:none; border:1px solid #d9d6cd; border-radius:999px; padding:9px 17px; background:transparent; color:#696a61; font-size:12px; cursor:pointer; }.category-tabs button.selected { border-color:var(--olive); background:var(--olive); color:#fff; }
.menu-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:22px; }.dish-card { overflow:hidden; border-radius:5px; background:#fffdfa; }.dish-image { position:relative; height:210px; overflow:hidden; background:#e7e3d8; }.dish-image>img { width:100%; height:100%; object-fit:cover; transition:transform .4s; }.dish-card:hover .dish-image>img { transform:scale(1.035); }.dish-tag { position:absolute; top:13px; left:13px; border-radius:2px; padding:7px 9px; background:#fffdf2; color:#6b654b; font-size:8px; font-weight:700; letter-spacing:.12em; }.add-button { position:absolute; right:13px; bottom:13px; display:grid; width:38px; height:38px; place-items:center; border:0; border-radius:50%; background:#fffdf7; color:var(--olive); box-shadow:0 3px 14px #2222; cursor:pointer; }.dish-info { padding:17px 18px 19px; }.dish-info>div { display:flex; justify-content:space-between; gap:12px; }.dish-info h3 { margin:0; font:600 18px Georgia,serif; }.dish-info b { color:var(--olive); font-size:14px; white-space:nowrap; }.dish-info p { margin:9px 0 0; color:#858178; font-size:11px; line-height:1.6; }.menu-message { padding:35px 0; color:#79776f; text-align:center; }.error-message { color:#9b3e2d; }.error-message button { margin-left:7px; border:0; background:none; color:#39452f; text-decoration:underline; cursor:pointer; }
.promise { padding-top:65px; padding-bottom:65px; }.promise-image { height:330px; }.promise-copy { padding:15px 3vw; }.promise-copy>p { max-width:420px; font-size:13px; }.signature { margin-top:27px; color:#77766e; font:italic 15px Georgia,serif; }.signature span { padding-left:7px; color:var(--orange); font-size:22px; }
.site-footer { background:#303a2a; color:#deded4; font-size:11px; }.site-footer .footer-mark { width:35px; height:35px; background:#f4eee2; color:var(--olive); font-size:21px; }.site-footer>div>span { color:#c1c3b9; }
.overlay { position:fixed; z-index:30; inset:0; display:flex; justify-content:flex-end; background:#1d211db3; backdrop-filter:blur(3px); }.order-panel { position:relative; width:min(100%,480px); height:100%; overflow-y:auto; padding:42px clamp(24px,6vw,48px); background:var(--cream); box-shadow:-10px 0 40px #0002; }.close-panel { position:absolute; top:20px; right:20px; display:grid; width:36px; height:36px; place-items:center; border:1px solid #dedbd3; border-radius:50%; background:transparent; color:#5f6258; cursor:pointer; }.close-panel svg { width:18px; }.order-panel h2 { margin:14px 0 8px; font-size:42px; }.panel-copy { margin:0 0 24px; color:#7b796f; font-size:13px; line-height:1.6; }.empty-cart { display:flex; min-height:220px; flex-direction:column; align-items:center; justify-content:center; gap:15px; color:#8d8a80; }.empty-cart a { display:flex; align-items:center; gap:7px; color:var(--olive); font-size:13px; font-weight:600; }.cart-lines { display:grid; gap:4px; }.cart-line { display:flex; gap:14px; border-bottom:1px solid #e7e3db; padding:15px 0; }.cart-line>img { width:74px; height:74px; border-radius:4px; object-fit:cover; }.line-detail { display:grid; grid-template-columns:1fr auto; flex:1; gap:6px; align-content:start; }.line-detail>strong { font:600 15px Georgia,serif; }.line-detail>span { color:#555c4c; font-size:13px; }.quantity-control { display:flex; width:max-content; align-items:center; gap:12px; border:1px solid #e0ddd4; border-radius:99px; padding:4px 7px; }.quantity-control button { display:grid; place-items:center; border:0; background:none; color:#5a6152; cursor:pointer; }.quantity-control b { font-size:11px; }.cart-subtotal { display:flex; justify-content:space-between; margin:20px 0; font-size:14px; }.full-button { display:flex; width:100%; align-items:center; justify-content:center; gap:9px; }.checkout-form { display:grid; gap:14px; }.checkout-form label { display:grid; gap:6px; color:#4f5349; font-size:11px; font-weight:600; }.checkout-form input,.checkout-form textarea,.checkout-form select { width:100%; border:1px solid #dfdcd3; border-radius:3px; outline:none; padding:11px 12px; background:#fffefa; color:#30352d; font-size:13px; resize:vertical; }.checkout-form input:focus,.checkout-form textarea:focus,.checkout-form select:focus { border-color:#69765b; box-shadow:0 0 0 2px #69765b20; }.select-wrap { position:relative; }.select-wrap select { appearance:none; }.select-wrap svg { position:absolute; top:12px; right:12px; pointer-events:none; }.optional { float:right; margin-left:6px; color:#a19d92; font-size:8px; letter-spacing:.1em; }.form-error { margin:0; color:#a44632; font-size:12px; }.order-totals { display:grid; gap:9px; border-top:1px solid #e5e1d8; padding:16px 0; color:#747268; font-size:12px; }.order-totals>div { display:flex; justify-content:space-between; }.order-totals b { color:#42463d; font-weight:600; }.order-totals .grand-total { margin-top:5px; border-top:1px solid #e5e1d8; padding-top:13px; color:#343a30; font-size:15px; }.order-totals .grand-total b { font-size:17px; }.secure-note { color:#88857b; text-align:center; font-size:10px; }.success-icon { display:grid; width:58px; height:58px; place-items:center; margin:24px 0; border-radius:50%; background:#e3eadc; color:#4d6845; }.confirmation-card { display:grid; grid-template-columns:1fr auto; gap:12px; margin:24px 0; border:1px solid #e2ded5; padding:17px; }.confirmation-card span { color:#89867c; font-size:9px; letter-spacing:.12em; }.confirmation-card strong { color:#3b4334; font-size:13px; text-align:right; }.fade-enter-active,.fade-leave-active { transition:opacity .2s; }.fade-enter-from,.fade-leave-to { opacity:0; }
@media (max-width: 700px) { .section-heading { display:block; }.section-heading>p { margin:0; }.menu-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }.dish-image { height:155px; }.dish-info { padding:13px; }.dish-info h3 { font-size:15px; }.dish-info b { font-size:12px; }.dish-info p { font-size:10px; }.promise { gap:24px; }.promise-image { height:260px; }.promise-copy { padding:0; } }
@media (max-width: 430px) { .hero h1 { font-size:43px; }.hero-meta { gap:11px; }.menu-grid { grid-template-columns:1fr; }.dish-image { height:220px; }.site-footer>div { align-items:flex-start; }.image-note { right:0; } }
.size-picker { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-top:12px; color:#858178; font-size:10px; }.size-picker select { max-width:125px; border:1px solid #e2ded5; border-radius:3px; padding:6px 8px; background:#fffdfa; color:#39452f; font-size:11px; text-transform:capitalize; }.line-detail small { display:block; margin-top:4px; color:#89867c; font-size:10px; font-weight:400; text-transform:capitalize; }
</style>
