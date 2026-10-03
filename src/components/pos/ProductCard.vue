<script setup>
import { computed, ref } from 'vue'
import BaseButton from '../common/BaseButton.vue'
import BaseModal from '../common/BaseModal.vue'

const props = defineProps({
  product: { type: Object, required: true },
  modifierGroups: { type: Array, default: () => [] },
})
const emit = defineEmits(['add'])
const selectedSize = ref('medium')
const showModifiers = ref(false)
const selections = ref({})
const applicableGroups = computed(() => props.modifierGroups.filter((group) =>
  !group.productIds?.length || group.productIds.includes(props.product.id),
))
const basePrice = computed(() => Number(props.product.prices
  ? props.product.prices[selectedSize.value]
  : props.product.price))
const modifierTotal = computed(() => applicableGroups.value.reduce((sum, group) => {
  const selected = selections.value[group.id]
  const names = Array.isArray(selected) ? selected : selected ? [selected] : []
  return sum + group.options.reduce((optionSum, option) =>
    names.includes(option.name) ? optionSum + Number(option.price) : optionSum, 0)
}, 0))
const canConfirm = computed(() => applicableGroups.value.every((group) =>
  !group.isRequired || (Array.isArray(selections.value[group.id])
    ? selections.value[group.id].length > 0
    : Boolean(selections.value[group.id])),
))

function beginAdd() {
  if (!applicableGroups.value.length) {
    emitProduct([])
    return
  }
  selections.value = Object.fromEntries(applicableGroups.value.map((group) => [
    group.id,
    group.allowMultiple ? [] : '',
  ]))
  showModifiers.value = true
}

function emitProduct(modifiers) {
  const isPizza = Boolean(props.product.prices)
  const size = isPizza ? selectedSize.value : null
  const extraPrice = modifiers.reduce((sum, modifier) => sum + modifier.price, 0)
  emit('add', {
    ...props.product,
    price: basePrice.value + extraPrice,
    selectedSize: size,
    modifiers,
  })
  showModifiers.value = false
}

function confirmAdd() {
  if (!canConfirm.value) return
  const modifiers = applicableGroups.value.flatMap((group) => {
    const selected = selections.value[group.id]
    const names = Array.isArray(selected) ? selected : selected ? [selected] : []
    return group.options
      .filter((option) => names.includes(option.name))
      .map((option) => ({ group: group.name, name: option.name, price: Number(option.price) }))
  })
  emitProduct(modifiers)
}
</script>

<template>
  <article class="group overflow-hidden rounded-lg border border-border bg-surface shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
    <div class="relative h-36 overflow-hidden bg-orange-50">
      <img v-if="product.image" :src="product.image" :alt="product.name" class="size-full object-cover transition duration-300 group-hover:scale-105" />
      <span v-if="product.pizzaCategory" class="absolute left-3 top-3 rounded-full bg-surface/90 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-brand">{{ product.pizzaCategory }}</span>
    </div>
    <div class="grid gap-3 p-4">
      <div><h3 class="font-semibold text-ink">{{ product.name }}</h3><p class="mt-1 text-xs text-muted">{{ product.category }}</p></div>
      <div v-if="product.prices" class="flex gap-1 rounded-sm bg-background p-1">
        <button v-for="size in ['small', 'medium', 'large']" :key="size" type="button" class="flex-1 rounded px-1 py-1.5 text-[10px] font-semibold capitalize" :class="selectedSize === size ? 'bg-surface text-brand shadow-sm' : 'text-muted'" @click="selectedSize = size">{{ size.charAt(0).toUpperCase() }} <span class="block font-normal">${{ product.prices[size].toFixed(2) }}</span></button>
      </div>
      <div class="flex items-center justify-between"><strong class="text-base text-ink">${{ basePrice.toFixed(2) }}</strong><BaseButton class="min-h-9 px-3 text-xs" @click="beginAdd">{{ applicableGroups.length ? 'Customize' : 'Add' }}</BaseButton></div>
    </div>
  </article>
  <BaseModal :open="showModifiers">
    <div class="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-md bg-surface p-6 shadow-xl">
      <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Customize item</p>
      <h2 class="mt-1 text-xl font-bold text-ink">{{ product.name }}</h2>
      <p class="mt-1 text-sm text-muted">Base price ${{ basePrice.toFixed(2) }}</p>
      <fieldset v-for="group in applicableGroups" :key="group.id" class="mt-5 border-t border-border pt-4">
        <legend class="flex w-full items-center justify-between gap-3 text-sm font-semibold text-ink"><span>{{ group.name }}<span v-if="group.isRequired" class="ml-1 text-danger">*</span></span><span class="text-xs font-normal text-muted">{{ group.allowMultiple ? 'Choose any' : 'Choose one' }}</span></legend>
        <p v-if="group.description" class="mt-1 text-xs text-muted">{{ group.description }}</p>
        <label v-for="option in group.options" :key="option.name" class="mt-2 flex cursor-pointer items-center gap-3 rounded-sm border border-border px-3 py-2.5 text-sm hover:bg-background">
          <input v-if="group.allowMultiple" v-model="selections[group.id]" type="checkbox" :value="option.name" class="size-4 accent-brand" />
          <input v-else v-model="selections[group.id]" type="radio" :name="`modifier-${group.id}`" :value="option.name" class="size-4 accent-brand" />
          <span class="flex-1 text-ink">{{ option.name }}</span><strong class="text-muted">{{ Number(option.price) ? `+$${Number(option.price).toFixed(2)}` : 'Free' }}</strong>
        </label>
      </fieldset>
      <div class="mt-6 flex items-center justify-between border-t border-border pt-4"><span class="text-sm text-muted">Price per item</span><strong class="text-lg text-ink">${{ (basePrice + modifierTotal).toFixed(2) }}</strong></div>
      <div class="mt-5 flex justify-end gap-2"><BaseButton variant="secondary" @click="showModifiers = false">Cancel</BaseButton><BaseButton :disabled="!canConfirm" @click="confirmAdd">Add to order</BaseButton></div>
    </div>
  </BaseModal>
</template>
