import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('../views/Home.vue') },
    { path: '/track/:orderId', name: 'track-order', component: () => import('../views/TrackOrder.vue') },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router