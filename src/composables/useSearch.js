import { computed, ref } from 'vue'

export function useSearch(items, fields = ['name']) {
  const query = ref('')
  const results = computed(() => {
    const normalizedQuery = query.value.trim().toLowerCase()
    if (!normalizedQuery) return items.value ?? items
    return (items.value ?? items).filter((item) =>
      fields.some((field) => String(item[field]).toLowerCase().includes(normalizedQuery)),
    )
  })

  return { query, results }
}
