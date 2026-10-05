<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '../../services/authService.js'

const router = useRouter()
const route = useRoute()
const email = ref('')
const otp = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

onMounted(() => {
  if (route.query.email) {
    email.value = route.query.email
  }
  if (route.query.otp) {
    otp.value = route.query.otp
  }
})

async function submit() {
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  if (newPassword.value.length < 10) {
    error.value = 'Password must be at least 10 characters'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await authService.confirmPasswordReset(
      email.value.trim().toLowerCase(),
      otp.value,
      newPassword.value
    )
    success.value = response.message || 'Password reset successfully'
    window.setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.message || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="w-full max-w-md rounded-md border border-border bg-surface p-6 shadow-sm sm:p-8">
    <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Password Reset</p>
    <h1 class="mt-2 text-2xl font-bold text-ink">Set new password</h1>
    <p class="mt-2 text-sm text-muted">Enter your new password below.</p>
    <form class="mt-6 grid gap-4" @submit.prevent="submit">
      <label class="grid gap-2 text-sm font-semibold text-ink">New password<input v-model="newPassword" type="password" required minlength="10" maxlength="128" autocomplete="new-password" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /><span class="text-xs font-normal text-muted">Use at least 10 characters.</span></label>
      <label class="grid gap-2 text-sm font-semibold text-ink">Confirm password<input v-model="confirmPassword" type="password" required minlength="10" maxlength="128" autocomplete="new-password" class="h-11 rounded-sm border border-border bg-surface px-3 font-normal outline-none focus:border-brand" /></label>
      <p v-if="error" role="alert" class="text-sm text-danger">{{ error }}</p>
      <p v-if="success" role="status" class="text-sm text-success">{{ success }}</p>
      <button type="submit" class="mt-1 min-h-11 rounded-sm bg-brand px-4 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50" :disabled="loading">{{ loading ? 'Resetting...' : 'Reset password' }}</button>
    </form>
    <p class="mt-5 border-t border-border pt-4 text-sm text-muted"><RouterLink to="/login" class="font-semibold text-brand hover:underline">Back to sign in</RouterLink></p>
  </section>
</template>
