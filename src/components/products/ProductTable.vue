<script setup>
import ProductRow from './ProductRow.vue'

defineProps({ products: { type: Array, default: () => [] } })
const emit = defineEmits(['view', 'edit', 'delete'])
</script>

<template>
	<div class="overflow-x-auto rounded-lg border border-border bg-surface">
		<table class="w-full min-w-[760px] border-collapse text-left">
			<thead class="bg-background text-xs font-semibold uppercase text-muted">
				<tr>
					<th class="px-5 py-3">Product</th>
					<th class="px-5 py-3">Category</th>
					<th class="px-5 py-3">Price</th>
					<th class="px-5 py-3">Status</th>
					<th class="px-5 py-3">Actions</th>
				</tr>
			</thead>
			<tbody>
				<ProductRow
					v-for="product in products"
					:key="product.id"
					:product="product"
					@view="emit('view', product)"
					@edit="emit('edit', product)"
					@delete="emit('delete', product)"
				/>
				<tr v-if="!products.length">
					<td colspan="5" class="px-5 py-10 text-center text-sm text-muted">No products found.</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>
