import { ref } from 'vue'

export function useFetch() {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(false)

  async function execute(request) {
    loading.value = true
    error.value = null
    try {
      data.value = await request()
    } catch (requestError) {
      error.value = requestError
    } finally {
      loading.value = false
    }
  }

  return { data, error, loading, execute }
}
