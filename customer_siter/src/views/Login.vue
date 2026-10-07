<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { LogIn } from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const email = ref("");
const password = ref("");
const error = ref("");

async function handleLogin() {
  error.value = "";
  try {
    await auth.login({ email: email.value, password: password.value });
    router.push("/");
  } catch (err) {
    error.value = err.message || "Login failed. Please try again.";
  }
}
</script>

<template>
  <main class="min-h-screen bg-[var(--paper)] flex items-center justify-center px-5 py-16">
    <div class="w-full max-w-md">
      <div class="mb-8 text-center">
        <h1 class="font-serif text-4xl text-[var(--forest)]">Welcome back</h1>
        <p class="mt-2 text-sm text-[var(--muted)]">Sign in to your account</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
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
          <span class="mb-1 block text-xs font-semibold text-[var(--ink)]">Password</span>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
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
          <LogIn :size="18" />
          {{ auth.loading ? "Signing in..." : "Sign in" }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[var(--muted)]">
        Don't have an account?
        <router-link to="/register" class="font-semibold text-[var(--forest)] hover:underline">
          Create one
        </router-link>
      </p>
    </div>
  </main>
</template>
