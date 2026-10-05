<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '../../services/authService.js'

const router = useRouter()
const route = useRoute()
const email = ref('')
const otp = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

onMounted(() => {
  if (route.query.email) {
    email.value = route.query.email
  }
})

async function submit() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await authService.verifyPasswordReset(email.value.trim().toLowerCase(), otp.value)
    success.value = response.message || 'OTP verified'
    window.setTimeout(() => {
      router.push({ name: 'reset-password', query: { email: email.value.trim().toLowerCase(), otp: otp.value } })
    }, 1000)
  } catch (err) {
    error.value = err.message || 'Invalid OTP'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="w-full max-w-md rounded-md border border-border bg-surface p-6 shadow-sm sm:p-8">
    <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Password Reset</p>
    <h1 class="mt-2 text-2xl font-bold text-ink">Verify OTP</h1>
    <p class="mt-2 text-sm text-muted">Enter the 6-digit code sent to your email.</p>
    <form class="mt-6 grid gap-4" @submit.prevent="submit">
      <label class="grid gap-2 text-sm font-semibold text-ink">Email<input v-model.trim="email" type="email" required autocomplete="email" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" placeholder="you@restaurant.com" /></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">OTP Code<input v-model="otp" type="text" required maxlength="6" pattern="[0-9]{6}" autocomplete="one-time-code" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand text-center tracking-widest" placeholder="123456" /></label>
      <p v-if="error" role="alert" class="text-sm text-danger">{{ error }}</p>
      <p v-if="success" role="status" class="text-sm text-success">{{ success }}</p>
      <button type="submit" class="mt-1 min-h-11 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="loading">{{ loading ? 'Verifying...' : 'Verify OTP' }}</button>
    </form>
    <p class="mt-5 border-t border-border pt-4 text-sm text-muted"><RouterLink to="/forgot-password" class="font-semibold text-brand hover:underline">Back to forgot password</RouterLink></p>
  </section>
</template>
