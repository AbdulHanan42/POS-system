const apiBaseUrl = import.meta.env.VITE_API_URL || '/api'

export async function apiRequest(path, options = {}) {
  let response
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch {
    throw new Error('Unable to reach the backend. Check that the API server is running and try again.')
  }

  const responseText = await response.text()
  let responseBody = null
  if (responseText) {
    try {
      responseBody = JSON.parse(responseText)
    } catch {
      responseBody = responseText
    }
  }

  if (!response.ok) {
    const detail = responseBody?.detail
    const message = Array.isArray(detail)
      ? detail.map((issue) => `${issue.loc?.slice(1).join('.') || 'Request'}: ${issue.msg}`).join('; ')
      : typeof detail === 'string'
        ? detail
        : typeof responseBody === 'string' && responseBody
          ? responseBody
          : `Request failed (${response.status})`
    throw new Error(message)
  }

  return responseBody
}
