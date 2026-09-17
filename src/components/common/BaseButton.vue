<script setup>
defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
})
</script>

<template>
  <button :type="type" class="base-button" :class="`base-button--${variant}`">
    <slot />
  </button>
</template>

<style scoped>
.base-button {
  border: 0;
  border-radius: var(--radius-sm);
  padding: 0.625rem 1rem;
  cursor: pointer;
}

.base-button--primary {
  color: white;
  background: var(--color-brand);
}

.base-button--secondary {
  color: var(--color-ink);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}
</style>
