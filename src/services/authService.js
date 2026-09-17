import { apiRequest } from './api.js'

export const authService = {
  login: (credentials) => apiRequest('/login', { method: 'POST', body: JSON.stringify(credentials) }),
}
