<script setup>
defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
})

const variantClasses = {
  primary: 'bg-brand text-white hover:bg-brand-dark',
  secondary: 'border border-border bg-surface text-ink hover:bg-background',
  danger: 'bg-danger text-white hover:bg-red-800',
  ghost: 'text-muted hover:bg-background hover:text-ink',
}
</script>

<template>
  <button
    :type="type"
    class="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm px-4 text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand disabled:cursor-not-allowed disabled:opacity-50"
    :class="variantClasses[variant] || variantClasses.primary"
  >
    <slot />
  </button>
</template>
