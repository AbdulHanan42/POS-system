import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routePermissions = {
  dashboard: '*',
  pos: 'pos:use',
  tables: 'tables:read',
  menu: '*',
  orders: 'orders:read',
  kitchen: 'kitchen:read',
  customers: 'customers:manage',
  inventory: 'inventory:read',
  purchases: '*',
  reports: '*',
  staff: '*',
  settings: '*',
}

function landingRoute(auth) {
  return [
    ['/dashboard', '*'],
    ['/pos', 'pos:use'],
    ['/kitchen', 'kitchen:read'],
    ['/tables', 'tables:read'],
    ['/orders', 'orders:read'],
  ].find(([, permission]) => auth.can(permission))?.[0] || '/login'
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', meta: { permission: routePermissions.dashboard }, component: () => import('../views/dashboard/Dashboard.vue') },
    { path: '/pos', meta: { permission: routePermissions.pos }, component: () => import('../views/pos/POS.vue') },
    { path: '/tables', meta: { permission: routePermissions.tables }, component: () => import('../views/tables/Tables.vue') },
    { path: '/menu/products', meta: { permission: routePermissions.menu }, component: () => import('../views/menu/Products.vue') },
    { path: '/menu/categories', meta: { permission: routePermissions.menu }, component: () => import('../views/menu/Categories.vue') },
    { path: '/menu/modifiers', meta: { permission: routePermissions.menu }, component: () => import('../views/menu/Modifiers.vue') },
    { path: '/orders', meta: { permission: routePermissions.orders }, component: () => import('../views/orders/Orders.vue') },
    { path: '/menu/products/create', meta: { permission: routePermissions.menu }, component: () => import('../views/menu/CreateProduct.vue') },
    { path: '/menu/products/:id/edit', meta: { permission: routePermissions.menu }, component: () => import('../views/menu/EditProduct.vue') },
    { path: '/menu/products/:id', meta: { permission: routePermissions.menu }, component: () => import('../views/menu/ProductDetails.vue') },
    { path: '/kitchen', meta: { permission: routePermissions.kitchen }, component: () => import('../views/kitchen/Kitchen.vue') },
    { path: '/customers', meta: { permission: routePermissions.customers }, component: () => import('../views/customers/Customers.vue') },
    { path: '/customers/:id', meta: { permission: routePermissions.customers }, component: () => import('../views/customers/CustomerDetails.vue') },
    { path: '/inventory', meta: { permission: routePermissions.inventory }, component: () => import('../views/inventory/Inventory.vue') },
    { path: '/purchases', meta: { permission: routePermissions.purchases }, component: () => import('../views/purchases/Purchases.vue') },
    { path: '/purchases/new', meta: { permission: routePermissions.purchases }, component: () => import('../views/purchases/CreatePurchase.vue') },
    { path: '/reports', meta: { permission: routePermissions.reports }, component: () => import('../views/reports/SalesReport.vue') },
    { path: '/staff', meta: { permission: routePermissions.staff }, component: () => import('../views/staff/Staff.vue') },
    { path: '/staff/roles', meta: { permission: '*' }, component: () => import('../views/staff/Roles.vue') },
    { path: '/login', meta: { public: true, layout: 'auth' }, component: () => import('../views/auth/Login.vue') },
    { path: '/signup', meta: { public: true, layout: 'auth' }, component: () => import('../views/auth/SignUp.vue') },
    { path: '/forgot-password', meta: { public: true, layout: 'auth' }, name: 'forgot-password', component: () => import('../views/auth/ForgotPassword.vue') },
    { path: '/verify-otp', meta: { public: true, layout: 'auth' }, name: 'verify-otp', component: () => import('../views/auth/VerifyOTP.vue') },
    { path: '/reset-password', meta: { public: true, layout: 'auth' }, name: 'reset-password', component: () => import('../views/auth/ResetPassword.vue') },
    { path: '/delivery', meta: { permission: 'orders:read' }, component: () => import('../views/delivery/DeliveryDashboard.vue') },
    { path: '/settings', meta: { permission: routePermissions.settings }, component: () => import('../views/settings/GeneralSettings.vue') },
    { path: '/customer-website', meta: { permission: '*' }, component: () => import('../views/settings/CustomerWebsite.vue') },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const authenticated = await auth.initialize()
  if (to.meta.public) return authenticated ? landingRoute(auth) : true
  if (!authenticated) return { path: '/login', query: { redirect: to.fullPath } }
  if (to.path === '/') return landingRoute(auth)
  if (to.meta.permission && !auth.can(to.meta.permission)) return landingRoute(auth)
  return true
})

export default router
