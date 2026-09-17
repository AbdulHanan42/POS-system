<template>
  <span class="base-badge"><slot /></span>
</template>

<style scoped>
.base-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  background: #ffedd5;
  color: var(--color-brand-dark);
  font-size: 0.75rem;
}
</style>
