import { ref } from 'vue'

export function usePagination() {
  const page = ref(1)
  const perPage = ref(10)
  return { page, perPage }
}
