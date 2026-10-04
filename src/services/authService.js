import { apiRequest } from './api.js'

export const authService = {
  login: (credentials) => apiRequest('/auth/login', { method: 'POST', body: JSON.stringify(credentials) }),
  signup: (details) => apiRequest('/auth/signup', { method: 'POST', body: JSON.stringify(details) }),
  me: () => apiRequest('/auth/me'),
  logout: () => apiRequest('/auth/logout', { method: 'POST' }),
  users: () => apiRequest('/auth/users'),
  createUser: (account) => apiRequest('/auth/users', { method: 'POST', body: JSON.stringify(account) }),
  updateUserStatus: (id, status) => apiRequest(`/auth/users/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),
}
