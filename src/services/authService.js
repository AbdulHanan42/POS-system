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
  requestPasswordReset: (email) => apiRequest('/auth/password-reset/request', { method: 'POST', body: JSON.stringify({ email }) }),
  verifyPasswordReset: (email, otp) => apiRequest('/auth/password-reset/verify', { method: 'POST', body: JSON.stringify({ email, otp }) }),
  confirmPasswordReset: (email, otp, newPassword) => apiRequest('/auth/password-reset/confirm', { method: 'POST', body: JSON.stringify({ email, otp, newPassword }) }),
}
