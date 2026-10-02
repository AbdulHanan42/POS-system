<script setup>
defineProps({ open: Boolean })
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true"><slot /></div>
</template>
