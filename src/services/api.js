const apiBaseUrl = import.meta.env.VITE_API_URL || '/api'

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  return response.json()
}
