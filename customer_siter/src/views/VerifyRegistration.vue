<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Mail, RefreshCw, ShieldCheck } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const otp = ref('')
const error = ref('')
const notice = ref('')
const resendCountdown = ref(60)
const resending = ref(false)
let countdownTimer

onMounted(() => {
  if (!auth.pendingEmail) {
    router.replace({ name: 'register' })
    return
  }

  countdownTimer = window.setInterval(() => {
    if (resendCountdown.value > 0) resendCountdown.value -= 1
  }, 1000)
})

onBeforeUnmount(() => window.clearInterval(countdownTimer))

function updateOtp(event) {
  otp.value = event.target.value.replace(/\D/g, '').slice(0, 6)
}

async function handleVerify() {
  error.value = ''
  notice.value = ''
  if (!/^\d{6}$/.test(otp.value)) {
    error.value = 'Enter the six-digit code from your email.'
    return
  }

  try {
    await auth.verifyRegistration(otp.value)
    await router.replace('/')
  } catch (err) {
    error.value = err.message || 'We could not verify that code.'
  }
}

async function handleResend() {
  error.value = ''
  notice.value = ''
  resending.value = true
  try {
    const result = await auth.resendRegistrationCode()
    notice.value = result.message
    resendCountdown.value = 60
  } catch (err) {
    error.value = err.message || 'We could not send another code.'
  } finally {
    resending.value = false
  }
}
</script>

<template>
  <main class="min-h-screen bg-[var(--paper)] flex items-center justify-center px-5 py-16">
    <section class="w-full max-w-md">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-5 flex size-14 items-center justify-center border border-[var(--forest)]/20 bg-white text-[var(--forest)]">
          <Mail :size="24" />
        </div>
        <h1 class="font-serif text-4xl text-[var(--forest)]">Check your email</h1>
        <p class="mt-3 text-sm leading-6 text-[var(--muted)]">
          Enter the six-digit verification code sent to
          <span class="font-semibold text-[var(--ink)]">{{ auth.pendingEmail }}</span>.
        </p>
      </div>

      <form @submit.prevent="handleVerify" class="space-y-5">
        <label class="block">
          <span class="mb-2 block text-xs font-semibold text-[var(--ink)]">Verification code</span>
          <input
            :value="otp"
            @input="updateOtp"
            type="text"
            inputmode="numeric"
            autocomplete="one-time-code"
            maxlength="6"
            required
            class="h-14 w-full border border-stone-300 bg-white px-4 text-center font-mono text-2xl tracking-[0.35em] text-[var(--ink)] outline-none focus:border-[var(--forest)]"
            placeholder="000000"
            aria-label="Six-digit verification code"
          />
        </label>

        <p v-if="error" class="text-sm text-red-800" role="alert">{{ error }}</p>
        <p v-if="notice" class="text-sm text-[var(--forest)]" role="status">{{ notice }}</p>

        <button
          type="submit"
          :disabled="auth.loading"
          class="flex h-12 w-full items-center justify-center gap-2 bg-[var(--forest)] text-sm font-semibold text-white hover:bg-[#1f3b30] disabled:opacity-50"
        >
          <ShieldCheck :size="18" />
          {{ auth.loading ? 'Verifying...' : 'Verify and continue' }}
        </button>
      </form>

      <div class="mt-6 flex flex-col items-center gap-4 text-sm">
        <button
          type="button"
          :disabled="resending || resendCountdown > 0"
          class="inline-flex items-center gap-2 font-semibold text-[var(--forest)] hover:underline disabled:cursor-not-allowed disabled:text-[var(--muted)] disabled:no-underline"
          @click="handleResend"
        >
          <RefreshCw :size="15" />
          {{ resending ? 'Sending...' : resendCountdown > 0 ? `Resend code in ${resendCountdown}s` : 'Resend code' }}
        </button>
        <router-link to="/register" class="text-[var(--muted)] hover:text-[var(--forest)]">
          Use a different email address
        </router-link>
      </div>
    </section>
  </main>
</template>