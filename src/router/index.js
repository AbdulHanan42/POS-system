import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('../views/dashboard/Dashboard.vue') },
    { path: '/pos', component: () => import('../views/pos/POS.vue') },
    { path: '/tables', component: () => import('../views/tables/Tables.vue') },
    { path: '/menu/products', component: () => import('../views/menu/Products.vue') },
    { path: '/menu/categories', component: () => import('../views/menu/Categories.vue') },
    { path: '/menu/modifiers', component: () => import('../views/menu/Modifiers.vue') },
    { path: '/orders', component: () => import('../views/orders/Orders.vue') },
    { path: '/kitchen', component: () => import('../views/kitchen/Kitchen.vue') },
    { path: '/customers', component: () => import('../views/customers/Customers.vue') },
    { path: '/inventory', component: () => import('../views/inventory/Inventory.vue') },
    { path: '/purchases', component: () => import('../views/purchases/Purchases.vue') },
    { path: '/reports', component: () => import('../views/reports/SalesReport.vue') },
    { path: '/staff', component: () => import('../views/staff/Staff.vue') },
    { path: '/login', component: () => import('../views/auth/Login.vue') },
    { path: '/settings', component: () => import('../views/settings/GeneralSettings.vue') },
  ],
})

export default router
