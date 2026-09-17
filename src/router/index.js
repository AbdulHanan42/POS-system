import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('../views/dashboard/Dashboard.vue') },
    { path: '/pos', component: () => import('../views/pos/POS.vue') },
    { path: '/tables', component: () => import('../views/tables/Tables.vue') },
    { path: '/login', component: () => import('../views/auth/Login.vue') },
  ],
})

export default router
