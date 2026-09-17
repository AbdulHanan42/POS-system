<template>
  <div v-if="open" class="modal" role="dialog" aria-modal="true"><slot /></div>
</template>

<script setup>
defineProps({ open: Boolean })
</script>
