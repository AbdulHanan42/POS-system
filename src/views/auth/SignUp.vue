<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth.js'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ tenantName: '', name: '', email: '', password: '' })

async function submit() {
  try {
    await auth.signup({ ...form.value, email: form.value.email.trim().toLowerCase() })
    await router.replace('/dashboard')
  } catch {
    // The store exposes the API error beside the form.
  }
}
</script>

<template>
  <section class="w-full max-w-lg rounded-md border border-border bg-surface p-6 shadow-sm sm:p-8">
    <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Restaurant workspace</p>
    <h1 class="mt-2 text-2xl font-bold text-ink">Create your account</h1>
    <p class="mt-2 text-sm text-muted">Your account will be the workspace administrator.</p>
    <form class="mt-6 grid gap-4" @submit.prevent="submit">
      <label class="grid gap-2 text-sm font-semibold text-ink">Restaurant name<input v-model.trim="form.tenantName" required minlength="2" maxlength="120" autocomplete="organization" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">Your name<input v-model.trim="form.name" required minlength="2" maxlength="120" autocomplete="name" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">Work email<input v-model.trim="form.email" required type="email" maxlength="254" autocomplete="email" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">Password<input v-model="form.password" required type="password" minlength="10" maxlength="128" autocomplete="new-password" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /><span class="text-xs font-normal text-muted">Use at least 10 characters.</span></label>
      <p v-if="auth.error" role="alert" class="text-sm text-danger">{{ auth.error }}</p>
      <button type="submit" class="mt-1 min-h-11 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="auth.loading">{{ auth.loading ? 'Creating workspace...' : 'Create workspace' }}</button>
    </form>
    <p class="mt-5 border-t border-border pt-4 text-sm text-muted">Already registered? <RouterLink to="/login" class="font-semibold text-brand hover:underline">Sign in</RouterLink></p>
  </section>
</template>