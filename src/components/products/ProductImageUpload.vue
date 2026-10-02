<script setup>
defineProps({ modelValue: { type: String, default: '' } })
const emit = defineEmits(['update:modelValue'])

function handleImage(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => emit('update:modelValue', reader.result)
  reader.readAsDataURL(file)
}
</script>

<template>
  <label class="group relative grid min-h-40 cursor-pointer place-items-center overflow-hidden rounded-lg border border-dashed border-border bg-background p-5 text-center hover:border-brand">
    <input class="sr-only" type="file" accept="image/png,image/jpeg,image/webp" @change="handleImage" />
    <img v-if="modelValue" :src="modelValue" alt="Product preview" class="absolute inset-0 size-full object-cover" />
    <span class="relative rounded-md bg-surface/90 px-4 py-3 shadow-sm"><strong class="block text-sm text-ink">{{ modelValue ? 'Change product image' : 'Upload product image' }}</strong><small class="mt-1 block text-xs text-muted">PNG, JPG, or WebP up to 2MB</small></span>
  </label>
</template>
