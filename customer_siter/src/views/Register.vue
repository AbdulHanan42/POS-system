<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { UserPlus } from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const name = ref("");
const email = ref("");
const phone = ref("");
const password = ref("");
const confirmPassword = ref("");
const error = ref("");

async function handleRegister() {
  error.value = "";
  
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }

  if (password.value.length < 8) {
    error.value = "Password must be at least 8 characters";
    return;
  }

  try {
    await auth.register({
      name: name.value,
      email: email.value,
      phone: phone.value,
      password: password.value,
    });
    router.push("/");
  } catch (err) {
    error.value = err.message || "Registration failed. Please try again.";
  }
}
</script>

<template>
  <main class="min-h-screen bg-[var(--paper)] flex items-center justify-center px-5 py-16">
    <div class="w-full max-w-md">
      <div class="mb-8 text-center">
        <h1 class="font-serif text-4xl text-[var(--forest)]">Create account</h1>
        <p class="mt-2 text-sm text-[var(--muted)]">Join us to order your favorite food</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Full name</span>
          <input
            v-model="name"
            type="text"
            required
            autocomplete="name"
            class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
            placeholder="John Doe"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Email</span>
          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
            placeholder="your@email.com"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Phone (optional)</span>
          <input
            v-model="phone"
            type="tel"
            autocomplete="tel"
            class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
            placeholder="+1 234 567 8900"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Password</span>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="new-password"
            minlength="8"
            class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
            placeholder="••••••••"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Confirm password</span>
          <input
            v-model="confirmPassword"
            type="password"
            required
            autocomplete="new-password"
            class="w-full h-11 border border-stone-300 bg-white px-3 text-sm text-[var(--ink)] outline-none focus:border-[var(--forest)]"
            placeholder="••••••••"
          />
        </label>

        <p v-if="error" class="text-sm text-red-800" role="alert">{{ error }}</p>

        <button
          type="submit"
          :disabled="auth.loading"
          class="w-full h-12 flex items-center justify-center gap-2 bg-[var(--forest)] text-white text-sm font-semibold hover:bg-[#1f3b30] disabled:opacity-50"
        >
          <UserPlus :size="18" />
          {{ auth.loading ? "Creating account..." : "Create account" }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[var(--muted)]">
        Already have an account?
        <router-link to="/login" class="font-semibold text-[var(--forest)] hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </main>
</template>
