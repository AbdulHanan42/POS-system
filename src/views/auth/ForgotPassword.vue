<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../../services/authService.js'

const router = useRouter()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await authService.requestPasswordReset(email.value.trim().toLowerCase())
    success.value = response.message || 'OTP sent to your email'
    window.setTimeout(() => {
      router.push({ name: 'verify-otp', query: { email: email.value.trim().toLowerCase() } })
    }, 2000)
  } catch (err) {
    error.value = err.message || 'Failed to send OTP'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="w-full max-w-md rounded-md border border-border bg-surface p-6 shadow-sm sm:p-8">
    <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Password Reset</p>
    <h1 class="mt-2 text-2xl font-bold text-ink">Forgot password</h1>
    <p class="mt-2 text-sm text-muted">Enter your email to receive a password reset code.</p>
    <form class="mt-6 grid gap-4" @submit.prevent="submit">
      <label class="grid gap-2 text-sm font-semibold text-ink">Email<input v-model.trim="email" type="email" required autocomplete="email" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="you@restaurant.com" /></label>
      <p v-if="error" role="alert" class="text-sm text-danger">{{ error }}</p>
      <p v-if="success" role="status" class="text-sm text-success">{{ success }}</p>
      <button type="submit" class="mt-1 min-h-11 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="loading">{{ loading ? 'Sending...' : 'Send OTP' }}</button>
    </form>
    <p class="mt-5 border-t border-border pt-4 text-sm text-muted">Remember your password? <RouterLink to="/login" class="font-semibold text-brand hover:underline">Sign in</RouterLink></p>
  </section>
</template>
