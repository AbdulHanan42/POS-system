<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth.js'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')

async function submit() {
  try {
    const user = await auth.login({ email: email.value, password: password.value })
    const safeTarget = typeof route.query.redirect === 'string'
      && route.query.redirect.startsWith('/')
      && !route.query.redirect.startsWith('//')
      ? route.query.redirect
      : user.role === 'Chef' ? '/kitchen' : ['Cashier', 'Waiter'].includes(user.role) ? '/pos' : '/dashboard'
    await router.replace(safeTarget)
  } catch {
    // The store exposes the API error beside the form.
  }
}
</script>

<template>
  <section class="w-full max-w-md rounded-md border border-border bg-surface p-6 shadow-sm sm:p-8">
    <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">RestoPilot workspace</p>
    <h1 class="mt-2 text-2xl font-bold text-ink">Sign in</h1>
    <p class="mt-2 text-sm text-muted">Use your restaurant account to continue.</p>
    <form class="mt-6 grid gap-4" @submit.prevent="submit">
      <label class="grid gap-2 text-sm font-semibold text-ink">Email<input v-model.trim="email" type="email" required autocomplete="username" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="you@restaurant.com" /></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">Password<input v-model="password" type="password" required autocomplete="current-password" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
      <p v-if="auth.error" role="alert" class="text-sm text-danger">{{ auth.error }}</p>
      <button type="submit" class="mt-1 min-h-11 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="auth.loading">{{ auth.loading ? 'Signing in...' : 'Sign in' }}</button>
    </form>
    <p class="mt-5 border-t border-border pt-4 text-sm text-muted">New restaurant? <RouterLink to="/signup" class="font-semibold text-brand hover:underline">Create a workspace</RouterLink></p>
  </section>
</template>
